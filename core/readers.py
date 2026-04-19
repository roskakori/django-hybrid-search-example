from collections.abc import Iterator
from dataclasses import dataclass

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, Q
from pgvector.django import CosineDistance

from core.models import ISO_LANGUAGE_TO_EMBEDDING_MODEL_MAP, ISO_LANGUAGE_TO_TS_CONFIG_MAP, Document, IsoLanguage
from core.ollama_session import OllamaSession

MAX_SEARCH_RESULT_COUNT = 20

_HYBRID_FTS_WEIGHT = 0.2  # Must be between 0.0 and 1.0


@dataclass
class DocumentFound:
    id: int
    iso_language: IsoLanguage
    title: str
    content: str
    fts_rank: float | None = None
    semantic_distance: float | None = None
    hybrid_rank: float | None = None


def documents_matching_plain_search(iso_language: IsoLanguage, term: str) -> Iterator[DocumentFound]:
    documents_found = (
        Document.objects.only("iso_language", "title", "content")
        .filter(iso_language=iso_language)
        .filter(
            Q(title__icontains=term) | Q(content__icontains=term),
        )
        .order_by("-id")
    )[:MAX_SEARCH_RESULT_COUNT]

    for document in documents_found:
        yield DocumentFound(
            id=document.id,
            iso_language=IsoLanguage(document.iso_language),
            title=document.title,
            content=document.content,
        )


def documents_matching_full_text_search(iso_language: IsoLanguage, term: str) -> Iterator[DocumentFound]:
    config = ISO_LANGUAGE_TO_TS_CONFIG_MAP[iso_language]
    search_query = SearchQuery(term, search_type="raw", config=config)
    search_rank = SearchRank(F("fts_vector"), search_query)
    documents_found = (
        Document.objects.only("iso_language", "title", "content")
        .annotate(rank=search_rank)
        .filter(iso_language=iso_language, fts_vector=search_query, rank__gt=0.0)  # Perform full text search on index.
        .order_by("-rank")  # Yield most relevant entries first.
    )[:MAX_SEARCH_RESULT_COUNT]

    for document in documents_found:
        yield DocumentFound(
            id=document.id,
            iso_language=IsoLanguage(document.iso_language),
            title=document.title,
            content=document.content,
            fts_rank=document.rank,
        )


def documents_matching_semantic_search(
    ollama_session: OllamaSession, iso_language: IsoLanguage, term: str
) -> list[DocumentFound]:
    # Compute the semantic vector of the search term.
    model = ISO_LANGUAGE_TO_EMBEDDING_MODEL_MAP[iso_language]
    term_vector = ollama_session.embed(model, term)

    documents_found = (
        Document.objects.only("iso_language", "title", "content")
        .annotate(
            semantic_distance=CosineDistance("semantic_vector", term_vector),
        )
        .filter(iso_language=iso_language, semantic_vector__isnull=False)
        .order_by("semantic_distance")[:MAX_SEARCH_RESULT_COUNT]
    )

    # We can't do a `yield` here because the ollama_session gets closed after the function returns the generator,
    # and the `ollama_session.embed()` is only called the when the actual item is requested from the generator.
    return [
        DocumentFound(
            id=document.id,
            iso_language=IsoLanguage(document.iso_language),
            semantic_distance=document.semantic_distance,
            title=document.title,
            content=document.content,
        )
        for document in documents_found
    ]


def documents_matching_hybrid_search(
    ollama_session: OllamaSession, iso_language: IsoLanguage, term: str
) -> list[DocumentFound]:
    id_to_semantic_documents_found_map = {
        document_found.id: document_found
        for document_found in documents_matching_semantic_search(ollama_session, iso_language, term)
    }
    id_to_fts_documents_found_map = {
        document_found.id: document_found for document_found in documents_matching_full_text_search(iso_language, term)
    }

    # The maximum FTS rank so we can normalize ot to a number
    # between 0.0 and 1.0. If there is no single document found by FTS,
    # it will be 1.0 to avoid division by zero later.
    max_fts_rank = (
        max(fts_document_found.fts_rank for fts_document_found in id_to_fts_documents_found_map.values())
        if id_to_fts_documents_found_map
        else 1.0
    )

    # The union of both the FTS and semantic document IDs.
    all_document_found_ids = set(id_to_semantic_documents_found_map.keys()) | set(id_to_fts_documents_found_map.keys())

    hybrid_documents_found = []
    for document_found_id in all_document_found_ids:
        semantic_document_found = id_to_semantic_documents_found_map.get(document_found_id)
        fts_document_found = id_to_fts_documents_found_map.get(document_found_id)
        base_document_found = fts_document_found or semantic_document_found  # At least one of them is not `None`.
        normalized_fts_rank = fts_document_found.fts_rank / max_fts_rank if fts_document_found is not None else 0.0
        semantic_distance = semantic_document_found.semantic_distance if semantic_document_found is not None else 0.0

        # This will result in a number between 0.0 and 2.0.
        hybrid_rank = normalized_fts_rank * _HYBRID_FTS_WEIGHT + semantic_distance * (1.0 - _HYBRID_FTS_WEIGHT)
        hybrid_documents_found.append(
            DocumentFound(
                id=document_found_id,
                iso_language=base_document_found.iso_language,
                semantic_distance=semantic_document_found.semantic_distance,
                fts_rank=normalized_fts_rank,
                hybrid_rank=hybrid_rank,
                title=base_document_found.title,
                content=base_document_found.content,
            )
        )
    hybrid_documents_found.sort(key=lambda document: document.hybrid_rank, reverse=True)
    return hybrid_documents_found[:MAX_SEARCH_RESULT_COUNT]

from collections.abc import Iterator
from dataclasses import dataclass

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, Q
from pgvector.django import CosineDistance

from core.models import ISO_LANGUAGE_TO_EMBEDDING_MODEL_MAP, ISO_LANGUAGE_TO_TS_CONFIG_MAP, Document, IsoLanguage
from core.ollama_session import OllamaSession

MAX_SEARCH_RESULT_COUNT = 20


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
        .filter(iso_language=iso_language)
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

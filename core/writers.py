from core.models import ISO_LANGUAGE_TO_EMBEDDING_MODEL_MAP, Document, IsoLanguage
from core.ollama_session import OllamaSession


def update_all_document_semantic_vectors(ollama_session: OllamaSession, *, force: bool = False) -> tuple[int, int]:
    documents_to_update = Document.objects.all()
    if not force:
        documents_to_update = documents_to_update.filter(semantic_vector__isnull=True)
    documents_to_update_count = documents_to_update.count()
    document_count = Document.objects.count()
    iso_languages_in_use = [
        IsoLanguage(iso_language)
        for iso_language in documents_to_update.values_list("iso_language", flat=True)
        .distinct()
        .order_by("iso_language")
    ]
    embedding_models_in_use = sorted(
        {ISO_LANGUAGE_TO_EMBEDDING_MODEL_MAP[iso_language] for iso_language in iso_languages_in_use}
    )
    for embedding_model in embedding_models_in_use:
        ollama_session.pull(embedding_model)
    for document in documents_to_update:
        update_document_semantic_vector(ollama_session, document)
    return documents_to_update_count, document_count


def update_document_semantic_vector(ollama_session: OllamaSession, document: Document):
    """Update the semantic vector for a given document."""
    model = ISO_LANGUAGE_TO_EMBEDDING_MODEL_MAP[IsoLanguage(document.iso_language)]
    text = document.title + "\n\n" + document.content
    document.semantic_vector = ollama_session.embed(model, text)
    document.save(update_fields=["semantic_vector"])

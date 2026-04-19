import pytest

from core.models import Document, IsoLanguage
from core.ollama_session import OllamaSession
from core.readers import documents_matching_hybrid_search, documents_matching_semantic_search
from core.writers import update_all_document_semantic_vectors


@pytest.mark.django_db
def test_can_find_documents_matching_semantic_search():
    document = Document.objects.create(iso_language=IsoLanguage.ENGLISH, title="hello world")
    with OllamaSession() as ollama_session:
        update_all_document_semantic_vectors(ollama_session)
        document.refresh_from_db()
        assert document.semantic_vector is not None

        documents_found = list(documents_matching_semantic_search(ollama_session, IsoLanguage.ENGLISH, "hello"))
        assert len(documents_found) == 1
        assert documents_found[0].title == "hello world"


@pytest.mark.django_db
def test_can_find_documents_matching_hybrid_search():
    Document.objects.create(iso_language=IsoLanguage.ENGLISH, title="cat")
    Document.objects.create(iso_language=IsoLanguage.ENGLISH, title="dog")
    Document.objects.create(iso_language=IsoLanguage.ENGLISH, title="puma")
    with OllamaSession() as ollama_session:
        update_all_document_semantic_vectors(ollama_session)

        documents_found = documents_matching_hybrid_search(ollama_session, IsoLanguage.ENGLISH, "cat")
        assert [document_found.title for document_found in documents_found] == ["cat", "puma", "dog"]

import pytest

from core.models import Document, IsoLanguage
from core.ollama_session import OllamaSession
from core.readers import documents_matching_semantic_search
from core.writers import update_all_document_semantic_vectors


@pytest.mark.django_db
def test_can_find_documents_matching_semantic_vector():
    document = Document.objects.create(iso_language=IsoLanguage.ENGLISH, title="hello world")
    with OllamaSession() as ollama_session:
        update_all_document_semantic_vectors(ollama_session)
        document.refresh_from_db()
        assert document.semantic_vector is not None

        documents_found = list(documents_matching_semantic_search(ollama_session, IsoLanguage.ENGLISH, "hello"))
        assert len(documents_found) == 1
        assert documents_found[0].title == "hello world"

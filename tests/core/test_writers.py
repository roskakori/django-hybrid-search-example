import pytest

from core.models import Document, IsoLanguage
from core.ollama_session import OllamaSession
from core.writers import update_document_semantic_vector


@pytest.mark.django_db
def test_can_update_document_semantic_vector():
    document = Document.objects.create(iso_language=IsoLanguage.ENGLISH, title="hello world")
    with OllamaSession() as ollama_session:
        update_document_semantic_vector(ollama_session, document)

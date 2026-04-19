from core.models import ISO_LANGUAGE_TO_EMBEDDING_MODEL_MAP, OLLAMA_VECTOR_SIZE, IsoLanguage
from core.ollama_session import OllamaSession

_EMBEDDING_MODEL = ISO_LANGUAGE_TO_EMBEDDING_MODEL_MAP[IsoLanguage.ENGLISH]


def test_can_pull_model():
    with OllamaSession() as ollama:
        ollama.pull(_EMBEDDING_MODEL)


def test_can_compute_embedding():
    with OllamaSession() as ollama:
        embedding = ollama.embed(_EMBEDDING_MODEL, "Hello world!")
    assert embedding is not None
    assert len(embedding) == OLLAMA_VECTOR_SIZE

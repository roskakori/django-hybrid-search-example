import json
import logging

import requests
from django.conf import settings
from requests import Response

from core.models import OLLAMA_VECTOR_SIZE

_log = logging.getLogger(__name__)


class OllamaSession:
    def __init__(self):
        self._session = requests.Session()
        self._api_url = settings.OLLAMA_URL.rstrip("/") + "/api/"

    def embed(self, model: str, text: str) -> list[float]:
        response = self.post(
            "embed",
            json={
                "dimensions": OLLAMA_VECTOR_SIZE,
                "input": text,
                "model": model,
            },
        )
        return response.json()["embeddings"][0]

    def pull(self, model: str):
        response = self.post("pull", json={"model": model}, stream=True)
        for line in response.iter_lines(decode_unicode=True):
            if line:
                status_map = json.loads(line)
                completed = status_map.get("completed")
                total = status_map.get("total")
                if completed is not None and total not in (None, 0):
                    progress = completed / total * 100
                    _log.info(f"Pulling model {model}: {progress:.1f}%")

    def post(self, relative_url: str, json: dict | None = None, stream: bool = False) -> Response:
        assert self._session is not None, "Session is closed"
        url = self._api_url + relative_url
        result = self._session.post(url, json=json, stream=stream)
        result.raise_for_status()
        return result

    def close(self):
        self._session.close()
        self._session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

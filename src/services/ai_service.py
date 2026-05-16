import json
import urllib.request
import urllib.error


class AiService:
    """
    Wraps the Ollama REST API for model listing and text generation.
    Pure Python, no Qt dependency.
    """

    @staticmethod
    def list_models(host: str = "http://localhost:11434") -> list[dict]:
        url = f"{host}/api/tags"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return data.get("models", [])
        except Exception:
            return []

    @staticmethod
    def generate(host: str, model: str, prompt: str, timeout: int = 120) -> str:
        url = f"{host}/api/generate"
        payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            return data.get("response", "")

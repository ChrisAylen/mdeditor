from src.services.ai_service import AiService


class AIProviderError(Exception):
    pass


class AIProviderClient:
    def __init__(self, host: str = "http://localhost:11434", model: str = ""):
        self.host = host.rstrip("/")
        self.model = model

    def chat(self, prompt: str) -> str:
        if not self.model:
            raise AIProviderError("No AI model configured.")
        try:
            return AiService.generate(self.host, self.model, prompt)
        except Exception as e:
            raise AIProviderError(str(e)) from e

    def check_available(self) -> str | None:
        if not self.model:
            return "No AI model configured."
        if not self.host:
            return "No AI host configured."
        models = AiService.list_models(self.host)
        if not models:
            return (
                f"Cannot reach Ollama at {self.host} or no models installed. "
                "Check that Ollama is running."
            )
        return None

from .groq_client import GroqClient
from .mock_client import MockClient


class LLMFactory:

    @staticmethod
    def get_client(provider="groq"):
        if provider == "groq":
            return GroqClient()
        return MockClient()
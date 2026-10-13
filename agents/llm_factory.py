"""
Deterministic mock responder only. Provider names do not activate external services.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Nanopore Sequencing Basecaller"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} mock responder]: Demo response only; no inference, verification, or clinical validation. Query: '{prompt[:60]}...'."


class LLMFactory:
    """Returns a local mock responder; no external model providers are connected."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Nanopore Sequencing Basecaller"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        elif prov in ["ollama", "local"]:
            return MockLLM(system_name)
        elif prov in ["claude", "anthropic"]:
            return MockLLM(system_name)
        elif prov in ["openai", "gpt4"]:
            return MockLLM(system_name)
        return MockLLM(system_name)

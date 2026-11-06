"""Explicit offline model adapter; no hidden network calls."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelOutput:
    text: str
    provider: str
    simulated: bool

class OfflineMockProvider:
    """Deterministic placeholder for tests, NOT a generative AI service."""
    def generate(self, prompt: str) -> ModelOutput:
        if not isinstance(prompt, str):
            raise TypeError("prompt must be text")
        return ModelOutput(text="[offline mock: no generated content]", provider="offline_mock", simulated=True)

def provider_from_config(name: str = "offline_mock"):
    if name != "offline_mock":
        raise ValueError("Only offline_mock is enabled; external providers require explicit integration and approval")
    return OfflineMockProvider()

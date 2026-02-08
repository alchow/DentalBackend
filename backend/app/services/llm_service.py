"""LLM Service - Abstraction layer for multiple LLM providers.

Supports swapping between OpenAI, Gemini, and Anthropic via configuration.
"""
import os
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import yaml


@dataclass
class SummaryResult:
    """Result from LLM summary generation."""
    content: dict
    model_provider: str
    model_name: str
    confidence_score: float
    prompt_version: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_summary(self, notes: list[str], prompt: str) -> SummaryResult:
        """Generate a patient summary from notes."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of this provider."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, model: str = None):
        # Allow override via env var
        self.model = model or os.getenv("LLM_MODEL", "gpt-4.1-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def generate_summary(self, notes: list[str], prompt: str) -> SummaryResult:
        import httpx
        
        notes_text = "\n---\n".join(notes)
        full_prompt = prompt.replace("{notes}", notes_text)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": full_prompt}],
                    "temperature": 0.3
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
        # v2 prompt returns Markdown, store as-is
        content_text = data["choices"][0]["message"]["content"]
        
        return SummaryResult(
            content={"summary_markdown": content_text},
            model_provider=self.provider_name,
            model_name=self.model,
            confidence_score=0.85,
            prompt_version=""
        )


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""
    
    def __init__(self, model: str = "gemini-pro"):
        self.model = model
        self.api_key = os.getenv("GEMINI_API_KEY")
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    async def generate_summary(self, notes: list[str], prompt: str) -> SummaryResult:
        import httpx
        
        notes_text = "\n---\n".join(notes)
        full_prompt = prompt.replace("{notes}", notes_text)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": self.api_key},
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {"temperature": 0.3}
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        # Extract JSON from response
        content = json.loads(text.strip().strip("```json").strip("```"))
        
        return SummaryResult(
            content=content,
            model_provider=self.provider_name,
            model_name=self.model,
            confidence_score=0.85,
            prompt_version=""
        )


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    async def generate_summary(self, notes: list[str], prompt: str) -> SummaryResult:
        import httpx
        
        notes_text = "\n---\n".join(notes)
        full_prompt = prompt.replace("{notes}", notes_text)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": full_prompt}]
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
        text = data["content"][0]["text"]
        content = json.loads(text.strip().strip("```json").strip("```"))
        
        return SummaryResult(
            content=content,
            model_provider=self.provider_name,
            model_name=self.model,
            confidence_score=0.85,
            prompt_version=""
        )


def get_llm_provider(name: Optional[str] = None) -> LLMProvider:
    """Get LLM provider by name. Defaults to LLM_PROVIDER env var."""
    provider_name = name or os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL")
    
    providers = {
        "openai": lambda: OpenAIProvider(model) if model else OpenAIProvider(),
        "gemini": lambda: GeminiProvider(model) if model else GeminiProvider(),
        "anthropic": lambda: AnthropicProvider(model) if model else AnthropicProvider()
    }
    
    if provider_name not in providers:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    
    return providers[provider_name]()


def load_prompt(prompt_name: str) -> tuple[str, str]:
    """Load prompt content and return (content, version)."""
    prompts_dir = Path(__file__).parent.parent.parent / "prompts"
    config_path = prompts_dir / "config.yaml"
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    version = config.get(prompt_name, {}).get("active_version", "v1")
    prompt_path = prompts_dir / prompt_name / f"{version}.txt"
    
    with open(prompt_path) as f:
        content = f.read()
    
    return content, version

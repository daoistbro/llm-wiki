#!/usr/bin/env python3
"""
LLM Provider Interface and Implementations

Supports multiple LLM providers: OpenAI, Anthropic, Ollama, etc.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str = "openai"
    api_key: Optional[str] = None
    model: str = "gpt-4"
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass

    @abstractmethod
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """Chat completion"""
        pass

    @abstractmethod
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract entities from text"""
        pass

    @abstractmethod
    def extract_concepts(self, text: str) -> List[Dict]:
        """Extract concepts from text"""
        pass

    @abstractmethod
    def summarize(self, text: str) -> str:
        """Summarize text"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )
        return response.choices[0].message.content

    def chat(self, messages: List[Dict], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
        )
        return response.choices[0].message.content

    def extract_entities(self, text: str) -> List[Dict]:
        prompt = f"""Extract entities (people, organizations, projects) from the following text.
Return as JSON array with format: {{"name": "Entity Name", "type": "person|organization|project", "description": "Brief description"}}

Text:
{text}"""
        response = self.generate(prompt)
        try:
            return json.loads(response)
        except:
            return []

    def extract_concepts(self, text: str) -> List[Dict]:
        prompt = f"""Extract key concepts, ideas, and methodologies from the following text.
Return as JSON array with format: {{"name": "Concept Name", "domain": "Field", "description": "Brief description"}}

Text:
{text}"""
        response = self.generate(prompt)
        try:
            return json.loads(response)
        except:
            return []

    def summarize(self, text: str) -> str:
        prompt = f"""Summarize the following text in 3-5 sentences, capturing the main points and key insights.

Text:
{text}"""
        return self.generate(prompt)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.api_key)
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

    def generate(self, prompt: str, **kwargs) -> str:
        message = self.client.messages.create(
            model=self.config.model,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def chat(self, messages: List[Dict], **kwargs) -> str:
        # Convert messages to Anthropic format
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                # Anthropic handles system messages differently
                continue
            anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

        message = self.client.messages.create(
            model=self.config.model,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            messages=anthropic_messages
        )
        return message.content[0].text

    def extract_entities(self, text: str) -> List[Dict]:
        prompt = f"""Extract entities (people, organizations, projects) from the following text.
Return as JSON array with format: {{"name": "Entity Name", "type": "person|organization|project", "description": "Brief description"}}

Text:
{text}"""
        response = self.generate(prompt)
        try:
            return json.loads(response)
        except:
            return []

    def extract_concepts(self, text: str) -> List[Dict]:
        prompt = f"""Extract key concepts, ideas, and methodologies from the following text.
Return as JSON array with format: {{"name": "Concept Name", "domain": "Field", "description": "Brief description"}}

Text:
{text}"""
        response = self.generate(prompt)
        try:
            return json.loads(response)
        except:
            return []

    def summarize(self, text: str) -> str:
        prompt = f"""Summarize the following text in 3-5 sentences, capturing the main points and key insights.

Text:
{text}"""
        return self.generate(prompt)


class OllamaProvider(LLMProvider):
    """Ollama local model provider"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("requests package required. Install with: pip install requests")

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            },
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()["response"]

    def chat(self, messages: List[Dict], **kwargs) -> str:
        # Convert messages to single prompt for Ollama
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        return self.generate(prompt, **kwargs)

    def extract_entities(self, text: str) -> List[Dict]:
        prompt = f"""Extract entities (people, organizations, projects) from the following text.
Return as JSON array with format: {{"name": "Entity Name", "type": "person|organization|project", "description": "Brief description"}}

Text:
{text}"""
        response = self.generate(prompt)
        try:
            return json.loads(response)
        except:
            return []

    def extract_concepts(self, text: str) -> List[Dict]:
        prompt = f"""Extract key concepts, ideas, and methodologies from the following text.
Return as JSON array with format: {{"name": "Concept Name", "domain": "Field", "description": "Brief description"}}

Text:
{text}"""
        response = self.generate(prompt)
        try:
            return json.loads(response)
        except:
            return []

    def summarize(self, text: str) -> str:
        prompt = f"""Summarize the following text in 3-5 sentences, capturing the main points and key insights.

Text:
{text}"""
        return self.generate(prompt)


def create_provider(config: Optional[LLMConfig] = None) -> LLMProvider:
    """Factory function to create LLM provider from config or environment variables"""

    if config is None:
        config = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            api_key=os.getenv("LLM_API_KEY"),
            model=os.getenv("LLM_MODEL", "gpt-4"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096"))
        )

    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,  # Alias
        "ollama": OllamaProvider,
    }

    provider_class = providers.get(config.provider.lower())
    if provider_class is None:
        raise ValueError(f"Unknown provider: {config.provider}")

    return provider_class(config)


def load_config_from_yaml(config_path: str) -> LLMConfig:
    """Load LLM config from YAML file"""
    try:
        import yaml
    except ImportError:
        raise ImportError("pyyaml required. Install with: pip install pyyaml")

    with open(config_path) as f:
        data = yaml.safe_load(f)

    llm_data = data.get("llm", {})
    return LLMConfig(
        provider=llm_data.get("provider", "openai"),
        api_key=os.path.expandvars(llm_data.get("api_key", "")),
        model=llm_data.get("model", "gpt-4"),
        base_url=llm_data.get("base_url"),
        temperature=llm_data.get("temperature", 0.7),
        max_tokens=llm_data.get("max_tokens", 4096)
    )

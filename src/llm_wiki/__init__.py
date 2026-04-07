"""
LLM Wiki - Incremental knowledge base system powered by LLM

Based on Karpathy's LLM Wiki concept:
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
"""

__version__ = "0.1.0"
__author__ = "daoistbro"
__email__ = "daoistbrother@outlook.com"

from llm_wiki.core import LLMWiki, WikiConfig, SourceDocument
from llm_wiki.llm import (
    LLMProvider,
    LLMConfig,
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    create_provider,
    load_config_from_yaml,
)
from llm_wiki.obsidian import (
    ObsidianIntegration,
    ObsidianConfig,
    setup_obsidian_vault,
    convert_llmwiki_to_obsidian,
)

__all__ = [
    # Core
    "LLMWiki",
    "WikiConfig",
    "SourceDocument",
    # LLM Providers
    "LLMProvider",
    "LLMConfig",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "create_provider",
    "load_config_from_yaml",
    # Obsidian Integration
    "ObsidianIntegration",
    "ObsidianConfig",
    "setup_obsidian_vault",
    "convert_llmwiki_to_obsidian",
]

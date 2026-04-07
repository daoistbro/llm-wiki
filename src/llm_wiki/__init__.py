"""
LLM Wiki - Incremental knowledge base system powered by LLM

Based on Karpathy's LLM Wiki concept:
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
"""

__version__ = "0.1.0"
__author__ = "daoistbro"
__email__ = "daoistbrother@outlook.com"

from llm_wiki.core import LLMWiki, WikiConfig, SourceDocument

__all__ = [
    "LLMWiki",
    "WikiConfig",
    "SourceDocument",
]

# 🧠 LLM Wiki

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **Incremental knowledge base system powered by LLM**
>
> A Python implementation of Karpathy's [LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

## 🌟 Features

- 🧠 **Multi-LLM Support**: OpenAI, Anthropic Claude, Ollama (本地模型), OpenAI-Compatible APIs
- 📝 **Obsidian Compatible**: 双向链接 [[Wiki Links]]，模板系统
- 🔌 **Easy Configuration**: 环境变量 或 YAML 配置文件
- 📦 **Zero Config**: 开箱即用，自动识别配置
- 🔗 **Bi-directional Links**: Obsidian 风格的 Wiki 链接
- 📊 **Auto Index**: 自动生成索引和健康检查

**Traditional RAG vs LLM Wiki:**

| Traditional RAG | LLM Wiki |
|-----------------|----------|
| Query → Retrieve → Generate | Source → **Compile** → Maintain |
| No accumulation, starts from scratch | Persistent, compounding knowledge |
| Contradictions not flagged | Cross-references already built |
| Knowledge scattered | Knowledge structured & interconnected |

**Key Insight:**

> The wiki is a persistent, compounding artifact. Cross-references are already there. Contradictions are already flagged. The synthesis already reflects everything you've read.

## 🏗️ Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Raw Sources (Immutable Layer)                          │
│  • Articles, papers, images, data files                 │
│  • Never modified after ingestion                       │
│  • Source of truth                                      │
└─────────────────────────────────────────────────────────┘
                    ↓ Read-only
┌─────────────────────────────────────────────────────────┐
│  Wiki (Compiled Knowledge Layer)                        │
│  • Markdown files (summaries, entities, concepts)       │
│  • LLM owns this layer - writes & maintains             │
│  • You read, LLM writes                                 │
└─────────────────────────────────────────────────────────┘
                    ↑ Configuration
┌─────────────────────────────────────────────────────────┐
│  Schema (Configuration Layer)                           │
│  • AGENTS.md / CLAUDE.md                                │
│  • Defines structure, conventions, workflows            │
│  • Co-evolved by you + LLM                              │
└─────────────────────────────────────────────────────────┘
```

## ⚡ Quick Start

### 1. Install with LLM support

```bash
# Basic installation
pip install llm-wiki

# With OpenAI support
pip install "llm-wiki[openai]"

# With all LLM providers (OpenAI + Claude + Ollama)
pip install "llm-wiki[all]"
```

### 2. Configure your LLM API

**方法 1: 环境变量 (.env 文件)**

```bash
cd your-wiki

# Create .env file
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4
```

**方法 2: YAML 配置文件**

```yaml
# llm-wiki.yaml
llm:
  provider: openai
  api_key: ${OPENAI_API_KEY}
  model: gpt-4
```

**支持的大模型**:

| 提供商 | 环境变量 | 示例模型 |
|--------|----------|----------|
| OpenAI | `LLM_PROVIDER=openai` | `gpt-4`, `gpt-4o` |
| Anthropic | `LLM_PROVIDER=anthropic` | `claude-sonnet-4-20250514` |
| Ollama (本地) | `LLM_PROVIDER=ollama` | `llama3.2`, `mistral` |
| OpenAI-Compatible | `LLM_PROVIDER=openai-compatible` | 任意兼容的模型 |

### 3. Initialize and Use

```bash
# Initialize wiki
llm-wiki init my-knowledge

# Add documents
cp ~/Downloads/paper.pdf my-knowledge/raw/

# Scan for unprocessed sources
llm-wiki scan

# Process with LLM (自动使用配置的 API)
python process_with_llm.py
```

### 4. Open in Obsidian

```python
from llm_wiki import convert_llmwiki_to_obsidian

# 转换为 Obsidian 兼容结构
convert_llmwiki_to_obsidian(
    wiki_path="my-knowledge",
    vault_path="~/obsidian-vault/llm-wiki"
)

# 然后在 Obsidian 中打开 ~/obsidian-vault/llm-wiki
```

## 🔌 LLM API Configuration

### 方式一：环境变量

```bash
# .env 文件
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4
LLM_BASE_URL=https://api.openai.com/v1
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

### 方式二：YAML 配置文件

```yaml
# llm-wiki.yaml
llm:
  provider: anthropic
  api_key: ${ANTHROPIC_API_KEY}
  model: claude-sonnet-4-20250514
  temperature: 0.7
  max_tokens: 4096

wiki:
  base_dir: .
  raw_dir: raw
  wiki_dir: wiki

obsidian:
  enabled: true
  vault_path: ~/obsidian-vault
```

### 方式三：代码配置

```python
from llm_wiki import LLMWiki, create_provider, setup_obsidian_vault

# 使用 OpenAI
llm = create_provider({
    "provider": "openai",
    "api_key": "sk-...",
    "model": "gpt-4"
})

# 使用 Claude
llm = create_provider({
    "provider": "anthropic",
    "api_key": "sk-ant-...",
    "model": "claude-sonnet-4-20250514"
})

# 使用本地模型 (Ollama)
llm = create_provider({
    "provider": "ollama",
    "model": "llama3.2",
    "base_url": "http://localhost:11434"
})
```

## 🚀 Full Example

```python
from llm_wiki import LLMWiki, create_provider, setup_obsidian_vault

# 1. 设置 LLM
llm = create_provider({
    "provider": "openai",
    "model": "gpt-4"
})

# 2. 初始化 Wiki
wiki = LLMWiki("my-knowledge")

# 3. 使用 LLM 处理文档
for source in wiki.get_unprocessed_sources():
    # 提取实体
    entities = llm.extract_entities(source.content)
    
    # 提取概念
    concepts = llm.extract_concepts(source.content)
    
    # 生成摘要
    summary = llm.summarize(source.content)
    
    # 创建 Wiki 页面
    for entity in entities:
        wiki.create_page("entity", entity["name"], entity["description"])
    
    for concept in concepts:
        wiki.create_page("concept", concept["name"], concept["description"])
    
    wiki.create_page("summary", source.metadata["name"], summary)
    wiki.mark_source_processed(source)
    wiki.append_log("ingest", f"Processed: {source.metadata['name']}")

# 4. 更新索引
wiki.update_index()

# 5. 健康检查
issues = wiki.lint()
for issue in issues:
    print(f"[{issue['severity']}] {issue['message']}")

# 6. 设置 Obsidian 集成 (可选)
setup_obsidian_vault("my-knowledge")
```

## 📦 Installation

```bash
# Basic installation
pip install llm-wiki

# From source
git clone https://github.com/daoistbro/llm-wiki.git
cd llm-wiki
pip install -e ".[all]"
```

## 🎯 What is LLM Wiki?

## 📖 Core Concepts

### Ingest (摄取)

Process new sources and integrate into the wiki:

1. Read source document
2. Extract key information (entities, concepts, claims)
3. Create or update wiki pages
4. Update cross-references
5. Record in log

A single source might touch 10-15 wiki pages.

### Query (查询)

Answer questions using the wiki:

1. Read index.md to find relevant pages
2. Deep-read relevant pages
3. Synthesize answer with citations
4. **Good answers become new wiki pages** (compounding)

### Lint (健康检查)

Periodic health check:

- Find contradictions between pages
- Find orphan pages (no inbound links)
- Find stale information (superseded by new sources)
- Find missing cross-references
- Find gaps that need new sources

## 🔧 CLI Reference

```bash
# Initialize a new wiki
llm-wiki init [DIRECTORY]

# Show wiki status
llm-wiki status

# Scan for unprocessed sources
llm-wiki scan

# Run health check
llm-wiki lint

# Update index
llm-wiki update-index

# Create a wiki page
llm-wiki create <type> <name>

# Mark source as processed
llm-wiki mark <source-hash>
```

## 📝 AGENTS.md Schema

The `AGENTS.md` file is the wiki's "constitution". It defines:

- Directory structure conventions
- Page format standards
- Ingestion workflows
- Query patterns
- Quality rules

LLMs read this file to understand how to maintain the wiki.

## 🔄 Integration Examples

### With OpenAI

```python
import openai
from llm_wiki import LLMWiki

wiki = LLMWiki("my-wiki")

def process_with_gpt(source):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": wiki.get_schema()},
            {"role": "user", "content": f"Extract entities, concepts, and summarize:\n\n{source.content}"}
        ]
    )
    return parse_llm_response(response.choices[0].message.content)
```

### With Claude

```python
import anthropic
from llm_wiki import LLMWiki

wiki = LLMWiki("my-wiki")

def process_with_claude(source):
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=wiki.get_schema(),
        messages=[
            {"role": "user", "content": f"Process this document and create wiki entries:\n\n{source.content}"}
        ]
    )
    return parse_llm_response(message.content[0].text)
```

### With Local LLM (Ollama)

```python
import requests
from llm_wiki import LLMWiki

wiki = LLMWiki("my-wiki")

def process_with_ollama(source):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": f"{wiki.get_schema()}\n\nProcess and create wiki entries:\n\n{source.content}",
            "stream": False
        }
    )
    return parse_llm_response(response.json()["response"])
```

## 🗂️ Page Formats

### Entity Page

```markdown
---
title: Andrej Karpathy
type: entity
created: 2026-04-07
updated: 2026-04-07
tags: [AI, Deep Learning, Tesla]
---

# Andrej Karpathy

> Type: Person

## Overview

AI researcher, former Director of AI at Tesla...

## Key Contributions

- Created `micrograd` - autograd engine
- Led Tesla Autopilot vision team
- Popularized "Software 2.0" concept

## Related Entities

- [[Tesla]] - Former employer
- [[OpenAI]] - Co-founder

## Related Concepts

- [[Software 2.0]]
- [[Neural Network Optimization]]

## Sources

- [[source:karpathy-gist]]
```

### Concept Page

```markdown
---
title: Software 2.0
type: concept
created: 2026-04-07
updated: 2026-04-07
domain: AI/ML
---

# Software 2.0

> Domain: AI/ML

## Definition

A paradigm where programs are written by optimization
rather than explicit coding...

## Key Points

- Goals expressed as datasets, not code
- Programs learned from examples
- Gradients replace manual debugging

## Related Concepts

- [[Neural Networks]]
- [[Gradient Descent]]

## Sources

- [[source:karpathy-blog-software2]]
```

## 🎯 Use Cases

### Personal Knowledge Base

Track goals, health, self-improvement - journal entries, articles, podcast notes - building a structured picture of yourself over time.

### Research Wiki

Deep-diving on a topic over weeks/months - papers, articles, reports - incrementally building a comprehensive wiki with evolving thesis.

### Book Companion

File each chapter as you read, build out pages for characters, themes, plot threads. By the end, you have a rich companion wiki.

### Team/Business Wiki

Internal wiki maintained by LLMs, fed by Slack threads, meeting transcripts, project documents. The wiki stays current because LLMs do the maintenance no one wants to do.

## 🔗 Related Projects

- [atomic-knowledge](https://github.com/Nimo1987/atomic-knowledge) - Markdown-first work-memory protocol
- [llm-wiki-template](https://github.com/bashiraziz/llm-wiki-template) - Template implementation
- [qmd](https://github.com/tobi/qmd) - Local search engine for markdown (recommended)
- [Obsidian](https://obsidian.md) - The IDE for your wiki (LLM is the programmer)

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Andrej Karpathy](https://github.com/karpathy) for the original [LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- The community implementations that inspired this project

---

**Made with ❤️ by [daoistbro](https://github.com/daoistbro)**

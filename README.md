# 🧠 LLM Wiki

[![PyPI version](https://badge.fury.io/py/llm-wiki.svg)](https://badge.fury.io/py/llm-wiki)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **Incremental knowledge base system powered by LLM**
>
> A Python implementation of Karpathy's [LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

## 🎯 What is LLM Wiki?

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

## 📦 Installation

```bash
# From PyPI (coming soon)
pip install llm-wiki

# From source
git clone https://github.com/daoistbro/llm-wiki.git
cd llm-wiki
pip install -e .
```

## 🚀 Quick Start

### 1. Initialize a Wiki

```bash
llm-wiki init my-knowledge-base
cd my-knowledge-base
```

This creates:

```
my-knowledge-base/
├── raw/                    # Source documents
│   └── attachments/        # Images & files
├── wiki/                   # Compiled knowledge
│   ├── entities/           # People, organizations, projects
│   ├── concepts/           # Ideas, methods, technologies
│   ├── summaries/          # Document summaries
│   ├── index.md            # Master index
│   └── log.md              # Activity log
└── AGENTS.md               # Schema configuration
```

### 2. Add Source Documents

```bash
# Copy documents to raw/
cp ~/Downloads/paper.pdf raw/
cp ~/Notes/meeting-notes.md raw/
```

### 3. Check Status

```bash
llm-wiki status
```

Output:

```
📊 Wiki Status
   Base Directory: my-knowledge-base
   Processed Sources: 0
   Pending Sources: 2
   Wiki Pages:
     - Entities: 0
     - Concepts: 0
     - Summaries: 0
     - Total: 0
```

### 4. (LLM Integration) Process Sources

The Python library provides the infrastructure. For intelligent processing, integrate with your LLM:

```python
from llm_wiki import LLMWiki

wiki = LLMWiki("my-knowledge-base")

# Get unprocessed sources
for source in wiki.get_unprocessed_sources():
    # Your LLM extracts knowledge
    entities = your_llm.extract_entities(source.content)
    concepts = your_llm.extract_concepts(source.content)
    summary = your_llm.summarize(source.content)
    
    # Create wiki pages
    for entity in entities:
        wiki.create_page("entity", entity.name, entity.content)
    
    wiki.create_page("summary", source.name, summary)
    wiki.mark_processed(source)
    wiki.log("ingest", f"Processed: {source.name}")

wiki.update_index()
```

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

# LLM API Configuration Examples

This document shows how to configure different LLM providers for use with LLM Wiki.

## Configuration Methods

### 1. Environment Variables

Create a `.env` file in your wiki directory:

```bash
# .env
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4
LLM_BASE_URL=https://api.openai.com/v1  # Optional: for custom endpoints
```

### 2. YAML Configuration

Create a `llm-wiki.yaml` file:

```yaml
llm:
  provider: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}  # Use environment variable
  base_url: https://api.openai.com/v1
  temperature: 0.7
  max_tokens: 4096

wiki:
  base_dir: .
  raw_dir: raw
  wiki_dir: wiki
  
obsidian:
  enabled: true
  vault_path: ~/obsidian-vault
  sync_interval: 300  # seconds
```

### 3. Programmatic Configuration

```python
from llm_wiki import LLMWiki
from llm_wiki.llm import OpenAIProvider, ClaudeProvider

# Using OpenAI
wiki = LLMWiki("my-wiki", llm_provider=OpenAIProvider(
    api_key="sk-...",
    model="gpt-4"
))

# Using Claude
wiki = LLMWiki("my-wiki", llm_provider=ClaudeProvider(
    api_key="sk-ant-...",
    model="claude-sonnet-4-20250514"
))
```

## Supported Providers

### OpenAI

```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4
```

Models: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`, `gpt-4o`

### Anthropic Claude

```bash
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-4-20250514
```

Models: `claude-sonnet-4-20250514`, `claude-opus-4-20250514`, `claude-haiku-3-5-20241022`

### Local Models (Ollama)

```bash
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
```

Models: `llama3.2`, `mistral`, `codellama`, `qwen2.5`

### OpenAI-Compatible APIs

For any OpenAI-compatible API (like vLLM, LM Studio, etc.):

```bash
LLM_PROVIDER=openai-compatible
LLM_API_KEY=your-key  # Optional for local APIs
LLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL=your-model-name
```

### Azure OpenAI

```bash
LLM_PROVIDER=azure
LLM_API_KEY=your-azure-key
LLM_BASE_URL=https://your-resource.openai.azure.com
LLM_API_VERSION=2024-02-15-preview
LLM_DEPLOYMENT=your-deployment-name
```

## Using with Obsidian

LLM Wiki is designed to work seamlessly with Obsidian. Here's how:

### Obsidian Vault Structure

```
your-vault/
├── raw/           # Source documents (LLM Wiki)
│   ├── articles/
│   ├── papers/
│   └── notes/
├── wiki/          # Compiled knowledge (LLM Wiki)
│   ├── entities/  # [[Wiki Links]] work in Obsidian
│   ├── concepts/
│   └── summaries/
├── templates/     # Obsidian templates
│   └── llm-wiki-template.md
└── .obsidian/     # Obsidian config
```

### Bi-directional Links

LLM Wiki uses Obsidian-compatible link syntax:

```markdown
[[Entity Name]]           # Link to entity
[[Concept Name|alias]]    # Link with alias
[[source:filename]]       # Link to source document
```

### Obsidian Plugin Integration

Create a simple plugin to sync with LLM Wiki:

```javascript
// .obsidian/plugins/llm-wiki/main.js
const { Plugin } = require('obsidian');

class LLMWikiPlugin extends Plugin {
    async onload() {
        this.addCommand({
            id: 'process-sources',
            name: 'Process Raw Sources',
            callback: () => this.processSources()
        });
        
        this.addCommand({
            id: 'update-index',
            name: 'Update Wiki Index',
            callback: () => this.updateIndex()
        });
    }
    
    async processSources() {
        // Call LLM Wiki CLI or API
        const { exec } = require('child_process');
        exec('llm-wiki scan && llm-wiki process', (error, stdout) => {
            if (error) {
                new Notice('Error processing sources');
                return;
            }
            new Notice('Sources processed!');
        });
    }
}
```

### Sync Workflow

1. **In Obsidian**: Create notes in `raw/` folder
2. **Run LLM Wiki**: Process sources to generate wiki pages
3. **In Obsidian**: View and edit generated pages in `wiki/`
4. **Iterate**: Changes are tracked and can be re-processed

### Obsidian Templates

Create a template for LLM Wiki pages:

```markdown
---
title: {{title}}
type: {{type}}
created: {{date}}
updated: {{date}}
tags: []
---

# {{title}}

> Type: {{type}}

## Overview

{{content}}

## Related

- [[Related Entity]]
- [[Related Concept]]

## Sources

- [[source:{{source}}]]
```

## Environment Variable Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider to use | `openai` |
| `LLM_API_KEY` | API key for the provider | Required |
| `LLM_MODEL` | Model to use | Provider-specific |
| `LLM_BASE_URL` | Base URL for API | Provider-specific |
| `LLM_TEMPERATURE` | Sampling temperature | `0.7` |
| `LLM_MAX_TOKENS` | Maximum tokens | `4096` |

## Security Best Practices

1. **Never commit API keys** to version control
2. Use `.env` files and add them to `.gitignore`
3. Use environment variables in production
4. Rotate keys regularly
5. Use separate keys for development and production

## Example: Complete Setup

```bash
# 1. Create wiki
llm-wiki init my-knowledge

# 2. Configure LLM
cd my-knowledge
echo "LLM_PROVIDER=openai" > .env
echo "LLM_API_KEY=sk-..." >> .env
echo "LLM_MODEL=gpt-4" >> .env

# 3. Add documents
cp ~/Downloads/paper.pdf raw/

# 4. Process with LLM
llm-wiki process --all

# 5. Open in Obsidian
# Open the my-knowledge folder as a vault in Obsidian
```

## Troubleshooting

### API Key Issues

```bash
# Test your API key
curl -H "Authorization: Bearer $LLM_API_KEY" \
     https://api.openai.com/v1/models
```

### Connection Issues

```bash
# Test local model
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello"
}'
```

### Rate Limits

If you hit rate limits, consider:
- Using a different model
- Reducing `max_tokens`
- Adding retry logic
- Using local models

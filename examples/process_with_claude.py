#!/usr/bin/env python3
"""
Example: Process sources with Anthropic Claude

This example shows how to use LLM Wiki with Anthropic Claude
to automatically extract entities, concepts, and summaries.
"""

import os
from llm_wiki import LLMWiki, create_provider

# Configure your Anthropic API key
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-api-key-here"

# Initialize wiki
wiki = LLMWiki("my-knowledge")

# Create LLM provider
llm = create_provider({
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514"
})

# Process all unprocessed sources
print("📄 Processing unprocessed sources with Claude...")

for source in wiki.get_unprocessed_sources():
    print(f"\n📖 Processing: {source.metadata['name']}")

    try:
        # Extract entities
        print("  - Extracting entities...")
        entities = llm.extract_entities(source.content)
        print(f"    Found {len(entities)} entities")

        for entity in entities:
            wiki.create_page(
                "entity",
                entity["name"],
                f"# {entity['name']}\n\n{entity['description']}",
                metadata={"type": entity.get("type", "unknown")}
            )

        # Extract concepts
        print("  - Extracting concepts...")
        concepts = llm.extract_concepts(source.content)
        print(f"    Found {len(concepts)} concepts")

        for concept in concepts:
            wiki.create_page(
                "concept",
                concept["name"],
                f"# {concept['name']}\n\n{concept['description']}",
                metadata={"domain": concept.get("domain", "general")}
            )

        # Generate summary
        print("  - Generating summary...")
        summary = llm.summarize(source.content)
        wiki.create_page(
            "summary",
            source.metadata["name"],
            f"# {source.metadata['name']}\n\n{summary}",
            metadata={"source": source.metadata["name"]}
        )

        # Mark as processed
        wiki.mark_source_processed(source)
        wiki.append_log("ingest", f"Processed: {source.metadata['name']}")

        print(f"  ✅ Completed: {source.metadata['name']}")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        continue

# Update index
print("\n📊 Updating index...")
wiki.update_index()

# Run health check
print("\n🔍 Running health check...")
issues = wiki.lint()
if issues:
    for issue in issues:
        print(f"  [{issue['severity']}] {issue['message']}")
else:
    print("  ✅ No issues found")

# Show final status
print("\n📊 Final Status:")
status = wiki.status()
print(f"  Processed sources: {status['processed_sources']}")
print(f"  Wiki pages: {status['wiki_pages']['total']}")
print(f"    - Entities: {status['wiki_pages']['entities']}")
print(f"    - Concepts: {status['wiki_pages']['concepts']}")
print(f"    - Summaries: {status['wiki_pages']['summaries']}")

#!/usr/bin/env python3
"""
Obsidian Integration for LLM Wiki

Provides seamless integration with Obsidian vaults.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ObsidianConfig:
    """Obsidian integration configuration"""
    enabled: bool = True
    vault_path: str = ""
    sync_interval: int = 300
    templates_dir: str = "templates"
    attachments_dir: str = "attachments"
    create_backlinks: bool = True
    use_aliases: bool = True


class ObsidianIntegration:
    """Obsidian vault integration"""

    def __init__(self, vault_path: str, config: Optional[ObsidianConfig] = None):
        self.vault_path = Path(vault_path).expanduser()
        self.config = config or ObsidianConfig(vault_path=vault_path)

        if not self.vault_path.exists():
            raise ValueError(f"Obsidian vault not found: {vault_path}")

        self._ensure_structure()

    def _ensure_structure(self):
        """Ensure required directories exist"""
        dirs = [
            self.vault_path / "raw",
            self.vault_path / "wiki",
            self.vault_path / "wiki" / "entities",
            self.vault_path / "wiki" / "concepts",
            self.vault_path / "wiki" / "summaries",
            self.vault_path / self.config.templates_dir,
            self.vault_path / self.config.attachments_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def create_template(self, template_type: str) -> Path:
        """Create Obsidian template file"""

        templates = {
            "entity": """---
title: {{title}}
type: entity
created: {{date}}
updated: {{date}}
tags: []
---

# {{title}}

> Type: {{entity_type}}

## Overview

{{overview}}

## Key Information

{{key_info}}

## Related Entities

{{#related_entities}}
- [[{{name}}]] - {{relation}}
{{/related_entities}}

## Related Concepts

{{#related_concepts}}
- [[{{name}}]]
{{/related_concepts}}

## Sources

{{#sources}}
- [[source:{{name}}]]
{{/sources}}

---
#entity #{{entity_type}}
""",

            "concept": """---
title: {{title}}
type: concept
created: {{date}}
updated: {{date}}
domain: {{domain}}
tags: []
---

# {{title}}

> Domain: {{domain}}

## Definition

{{definition}}

## Key Points

{{#key_points}}
- {{.}}
{{/key_points}}

## Examples

{{#examples}}
- {{.}}
{{/examples}}

## Related Concepts

{{#related_concepts}}
- [[{{name}}]]
{{/related_concepts}}

## Related Entities

{{#related_entities}}
- [[{{name}}]]
{{/related_entities}}

## Sources

{{#sources}}
- [[source:{{name}}]]
{{/sources}}

---
#concept #{{domain}}
""",

            "summary": """---
title: {{title}}
type: summary
created: {{date}}
updated: {{date}}
source: {{source}}
tags: []
---

# {{title}}

> Source: [[source:{{source}}]]

## Summary

{{summary}}

## Key Takeaways

{{#takeaways}}
- {{.}}
{{/takeaways}}

## Important Quotes

{{#quotes}}
> {{.}}
{{/quotes}}

## Related

{{#related}}
- [[{{name}}]] - {{relation}}
{{/related}}

## Questions

{{#questions}}
- {{.}}
{{/questions}}

---
#summary #{{source_type}}
"""
        }

        template_content = templates.get(template_type, "")
        template_path = self.vault_path / self.config.templates_dir / f"{template_type}.md"

        if not template_content:
            raise ValueError(f"Unknown template type: {template_type}")

        template_path.write_text(template_content)
        return template_path

    def create_source_link(self, source_path: Path) -> Path:
        """Create a link file for source document in Obsidian"""

        source_name = source_path.stem
        link_path = self.vault_path / "raw" / f"{source_name}.md"

        # Create Obsidian-compatible link file
        content = f"""---
title: {source_name}
type: source
created: {datetime.utcnow().strftime("%Y-%m-%d")}
path: {source_path}
---

# {source_name}

> Source Document

## Original File

`{source_path}`

## Processing Status

- [ ] Extracted entities
- [ ] Extracted concepts
- [ ] Created summary
- [ ] Updated index

## Notes

Add your notes about this source document here.

---
#source
"""

        link_path.write_text(content)
        return link_path

    def sync_attachment(self, file_path: Path) -> Path:
        """Copy attachment to Obsidian attachments directory"""

        dest_path = self.vault_path / self.config.attachments_dir / file_path.name
        shutil.copy2(file_path, dest_path)
        return dest_path

    def get_backlinks(self, page_name: str) -> List[Dict]:
        """Get all pages that link to the given page"""

        backlinks = []
        wiki_path = self.vault_path / "wiki"

        for md_file in wiki_path.rglob("*.md"):
            if md_file.name in ["index.md", "log.md"]:
                continue

            content = md_file.read_text(encoding="utf-8", errors="ignore")

            # Check for various link formats
            link_patterns = [
                f"[[{page_name}]]",
                f"[[{page_name}|",
                f"[source:{page_name}]]",
            ]

            for pattern in link_patterns:
                if pattern in content:
                    backlinks.append({
                        "path": str(md_file.relative_to(self.vault_path)),
                        "name": md_file.stem
                    })
                    break

        return backlinks

    def update_graph_view(self):
        """Update Obsidian graph view metadata"""

        # Create a graph.json for custom visualization
        graph_data = {
            "nodes": [],
            "edges": []
        }

        wiki_path = self.vault_path / "wiki"
        all_pages = {}

        # Collect all pages and their links
        for md_file in wiki_path.rglob("*.md"):
            if md_file.name in ["index.md", "log.md"]:
                continue

            content = md_file.read_text(encoding="utf-8", errors="ignore")
            page_name = md_file.stem

            # Extract links
            import re
            links = re.findall(r'\[\[([^\]|]+)', content)

            all_pages[page_name] = {
                "path": str(md_file.relative_to(self.vault_path)),
                "links": links
            }

        # Build graph data
        for page, data in all_pages.items():
            graph_data["nodes"].append({
                "id": page,
                "label": page,
                "path": data["path"]
            })

            for link in data["links"]:
                if link in all_pages:
                    graph_data["edges"].append({
                        "source": page,
                        "target": link
                    })

        # Write graph data
        graph_path = self.vault_path / "wiki" / "graph.json"
        graph_path.write_text(json.dumps(graph_data, indent=2))

        return graph_path

    def create_obsidian_config(self):
        """Create or update Obsidian workspace configuration"""

        obsidian_dir = self.vault_path / ".obsidian"
        obsidian_dir.mkdir(exist_ok=True)

        # Create app.json with LLM Wiki friendly settings
        app_json = {
            "legacyEditor": False,
            "livePreview": True,
            "readableLineLength": True,
            "showFrontmatter": True,
            "autoPairMarkdown": True,
            "showInlineTitle": True,
            "spellcheck": True
        }
        (obsidian_dir / "app.json").write_text(json.dumps(app_json, indent=2))

        # Create hotkeys for LLM Wiki commands
        hotkeys_json = [
            {"command": "llm-wiki:process-sources", "keys": ["Ctrl+Shift+P"]},
            {"command": "llm-wiki:update-index", "keys": ["Ctrl+Shift+I"]}
        ]
        (obsidian_dir / "hotkeys.json").write_text(json.dumps(hotkeys_json, indent=2))

        return obsidian_dir


def setup_obsidian_vault(vault_path: str) -> ObsidianIntegration:
    """Set up LLM Wiki structure in an Obsidian vault"""

    obsidian = ObsidianIntegration(vault_path)

    # Create templates
    for template_type in ["entity", "concept", "summary"]:
        obsidian.create_template(template_type)

    # Create Obsidian config
    obsidian.create_obsidian_config()

    # Update graph view
    obsidian.update_graph_view()

    return obsidian


def convert_llmwiki_to_obsidian(wiki_path: str, vault_path: str) -> None:
    """Convert existing LLM Wiki to Obsidian-compatible vault"""

    wiki_path = Path(wiki_path)
    vault_path = Path(vault_path)

    # Create vault structure
    vault_path.mkdir(parents=True, exist_ok=True)

    # Copy wiki directory
    if (wiki_path / "wiki").exists():
        shutil.copytree(wiki_path / "wiki", vault_path / "wiki", dirs_exist_ok=True)

    # Copy raw directory
    if (wiki_path / "raw").exists():
        shutil.copytree(wiki_path / "raw", vault_path / "raw", dirs_exist_ok=True)

    # Copy schema file
    schema_src = wiki_path / "AGENTS.md"
    if schema_src.exists():
        shutil.copy2(schema_src, vault_path / "AGENTS.md")

    # Set up Obsidian integration
    setup_obsidian_vault(str(vault_path))

    print(f"✅ Converted LLM Wiki to Obsidian vault: {vault_path}")
    print(f"   - Open this folder in Obsidian")
    print(f"   - Templates created in {vault_path}/templates/")
    print(f"   - Use [[Wiki Links]] for navigation")

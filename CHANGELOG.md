# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of LLM Wiki
- Core LLMWiki class with full functionality
- CLI tool with init, status, scan, lint, create, mark commands
- Support for entities, concepts, and summaries page types
- Automatic index generation and maintenance
- Health check (lint) functionality
- Wiki log for tracking operations
- Schema file (AGENTS.md) for configuration
- Source document tracking with hash-based deduplication
- YAML frontmatter support for wiki pages

### Documentation
- Comprehensive README with quick start guide
- Integration examples for OpenAI, Claude, and Ollama
- Page format specifications
- CLI reference documentation

### Testing
- Unit tests for core functionality
- Test coverage for WikiConfig, LLMWiki, and SourceDocument

## [0.1.0] - 2026-04-07

### Added
- Initial release
- Three-layer architecture implementation (Raw Sources → Wiki → Schema)
- Python package with proper structure
- MIT License

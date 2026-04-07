#!/usr/bin/env python3
"""
Tests for LLM Wiki core module
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import unittest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_wiki.core import LLMWiki, WikiConfig, SourceDocument


class TestWikiConfig(unittest.TestCase):
    """Tests for WikiConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = WikiConfig()
        self.assertEqual(config.raw_dir, "raw")
        self.assertEqual(config.wiki_dir, "wiki")
        self.assertEqual(config.index_file, "index.md")
        self.assertEqual(config.log_file, "log.md")
        self.assertEqual(config.schema_file, "AGENTS.md")

    def test_custom_config(self):
        """Test custom configuration values"""
        config = WikiConfig(
            raw_dir="sources",
            wiki_dir="knowledge",
            index_file="catalog.md"
        )
        self.assertEqual(config.raw_dir, "sources")
        self.assertEqual(config.wiki_dir, "knowledge")
        self.assertEqual(config.index_file, "catalog.md")


class TestLLMWiki(unittest.TestCase):
    """Tests for LLMWiki class"""

    def setUp(self):
        """Create a temporary directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.wiki = LLMWiki(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_init_creates_directories(self):
        """Test that initialization creates required directories"""
        self.assertTrue((Path(self.temp_dir) / "raw").exists())
        self.assertTrue((Path(self.temp_dir) / "wiki").exists())
        self.assertTrue((Path(self.temp_dir) / "wiki" / "entities").exists())
        self.assertTrue((Path(self.temp_dir) / "wiki" / "concepts").exists())
        self.assertTrue((Path(self.temp_dir) / "wiki" / "summaries").exists())

    def test_init_creates_files(self):
        """Test that initialization creates required files"""
        self.assertTrue((Path(self.temp_dir) / "wiki" / "index.md").exists())
        self.assertTrue((Path(self.temp_dir) / "wiki" / "log.md").exists())
        self.assertTrue((Path(self.temp_dir) / "AGENTS.md").exists())

    def test_status_empty_wiki(self):
        """Test status of an empty wiki"""
        status = self.wiki.status()
        self.assertEqual(status["processed_sources"], 0)
        self.assertEqual(status["unprocessed_sources"], 0)
        self.assertEqual(status["wiki_pages"]["total"], 0)
        self.assertTrue(status["has_index"])
        self.assertTrue(status["has_log"])
        self.assertTrue(status["has_schema"])

    def test_scan_empty_raw(self):
        """Test scanning empty raw directory"""
        sources = self.wiki.scan_raw_sources()
        self.assertEqual(len(sources), 0)

    def test_scan_with_documents(self):
        """Test scanning raw directory with documents"""
        # Create a test document
        raw_path = Path(self.temp_dir) / "raw"
        test_doc = raw_path / "test.md"
        test_doc.write_text("# Test Document\n\nThis is a test.")

        sources = self.wiki.scan_raw_sources()
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].metadata["name"], "test.md")

    def test_get_unprocessed_sources(self):
        """Test getting unprocessed sources"""
        # Create a test document
        raw_path = Path(self.temp_dir) / "raw"
        test_doc = raw_path / "test.md"
        test_doc.write_text("# Test Document\n\nThis is a test.")

        unprocessed = self.wiki.get_unprocessed_sources()
        self.assertEqual(len(unprocessed), 1)

    def test_mark_source_processed(self):
        """Test marking a source as processed"""
        # Create a test document
        raw_path = Path(self.temp_dir) / "raw"
        test_doc = raw_path / "test.md"
        test_doc.write_text("# Test Document\n\nThis is a test.")

        sources = self.wiki.scan_raw_sources()
        self.wiki.mark_source_processed(sources[0])

        # Check that it's now in processed sources
        processed = self.wiki.get_processed_sources()
        self.assertIn(sources[0].hash, processed)

        # Check that unprocessed is now empty
        unprocessed = self.wiki.get_unprocessed_sources()
        self.assertEqual(len(unprocessed), 0)

    def test_create_page(self):
        """Test creating a wiki page"""
        page_path = self.wiki.create_page(
            "entity",
            "Test Entity",
            "# Test Entity\n\nThis is a test entity."
        )
        self.assertTrue(page_path.exists())
        self.assertTrue(str(page_path).endswith("Test_Entity.md"))

    def test_append_log(self):
        """Test appending to log"""
        self.wiki.append_log("test", "Test log entry", {"key": "value"})

        log_path = Path(self.temp_dir) / "wiki" / "log.md"
        log_content = log_path.read_text()
        self.assertIn("Test log entry", log_content)
        self.assertIn("key: value", log_content)

    def test_update_index(self):
        """Test updating index"""
        # Create some pages
        self.wiki.create_page("entity", "Entity1", "Content 1")
        self.wiki.create_page("concept", "Concept1", "Content 2")

        self.wiki.update_index()

        index_path = Path(self.temp_dir) / "wiki" / "index.md"
        index_content = index_path.read_text()
        self.assertIn("Entity1", index_content)
        self.assertIn("Concept1", index_content)

    def test_lint_empty(self):
        """Test lint on empty wiki"""
        issues = self.wiki.lint()
        # Empty directories should generate info-level issues
        self.assertTrue(any(i["type"] == "empty_directory" for i in issues))


class TestSourceDocument(unittest.TestCase):
    """Tests for SourceDocument"""

    def test_source_document_creation(self):
        """Test creating a SourceDocument"""
        doc = SourceDocument(
            path=Path("/tmp/test.md"),
            content="Test content",
            hash="abc123",
            metadata={"name": "test.md"}
        )
        self.assertEqual(doc.path, Path("/tmp/test.md"))
        self.assertEqual(doc.content, "Test content")
        self.assertEqual(doc.hash, "abc123")
        self.assertFalse(doc.processed)


if __name__ == "__main__":
    unittest.main()

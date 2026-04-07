#!/usr/bin/env python3
"""
LLM Wiki Core - 核心模块

基于 Karpathy 的 LLM Wiki 概念实现
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

try:
    import frontmatter
except ImportError:
    frontmatter = None


@dataclass
class WikiConfig:
    """Wiki 配置"""
    raw_dir: str = "raw"
    wiki_dir: str = "wiki"
    index_file: str = "index.md"
    log_file: str = "log.md"
    schema_file: str = "AGENTS.md"
    attachments_dir: str = "raw/attachments"


@dataclass
class SourceDocument:
    """源文档"""
    path: Path
    content: str
    hash: str
    metadata: Dict[str, Any]
    processed: bool = False
    processed_at: Optional[datetime] = None


class LLMWiki:
    """LLM Wiki 主类"""

    def __init__(self, base_dir: str, config: Optional[WikiConfig] = None):
        self.base_dir = Path(base_dir)
        self.config = config or WikiConfig()
        self._init_directories()
        self._init_files()

    def _init_directories(self):
        """初始化目录结构"""
        dirs = [
            self.base_dir / self.config.raw_dir,
            self.base_dir / self.config.wiki_dir,
            self.base_dir / self.config.attachments_dir,
            self.base_dir / self.config.wiki_dir / "entities",
            self.base_dir / self.config.wiki_dir / "concepts",
            self.base_dir / self.config.wiki_dir / "summaries",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def _init_files(self):
        """初始化文件"""
        # 索引文件
        index_path = self.base_dir / self.config.wiki_dir / self.config.index_file
        if not index_path.exists():
            self._write_file(index_path, self._generate_index_template())

        # 日志文件
        log_path = self.base_dir / self.config.wiki_dir / self.config.log_file
        if not log_path.exists():
            self._write_file(log_path, "# Wiki Log\n\n> 按时间顺序记录所有操作\n\n")

        # Schema 文件
        schema_path = self.base_dir / self.config.schema_file
        if not schema_path.exists():
            self._write_file(schema_path, self._generate_schema_template())

    def _generate_index_template(self) -> str:
        """生成索引模板"""
        return """# Wiki Index

> 所有 Wiki 页面的目录索引

## 📊 统计

- 总页面数: 0
- 实体页: 0
- 概念页: 0
- 摘要页: 0
- 最后更新: {date}

---

## 📁 实体 (Entities)

> 人物、组织、项目等

*(暂无)*

---

## 💡 概念 (Concepts)

> 核心概念、方法论、技术等

*(暂无)*

---

## 📄 摘要 (Summaries)

> 文档摘要、读书笔记等

*(暂无)*

---

## 📥 已处理源文档

*(暂无)*
""".format(date=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))

    def _generate_schema_template(self) -> str:
        """生成 Schema 模板"""
        return """# AGENTS.md - LLM Wiki Schema

> 此文件定义 LLM Wiki 的结构和规则

## 目录结构

```
{base_dir}/
├── raw/           # 原始文档（不可变）
│   ├── attachments/  # 附件（图片等）
│   └── *.md, *.pdf, *.txt  # 源文件
├── wiki/          # Wiki 输出
│   ├── entities/  # 实体页
│   ├── concepts/  # 概念页
│   ├── summaries/ # 摘要页
│   ├── index.md   # 索引
│   └── log.md     # 日志
└── AGENTS.md      # 本文件
```

## 工作流

### Ingest (摄取)

1. 读取 `raw/` 目录中的新文档
2. 提取关键信息、实体、概念
3. 创建或更新相关 Wiki 页面
4. 更新 index.md
5. 记录到 log.md

### Query (查询)

1. 读取 index.md 找到相关页面
2. 深入阅读相关页面
3. 综合回答，引用来源

### Lint (健康检查)

- 检查矛盾信息
- 检查孤立页面
- 检查过时信息
- 检查缺失引用

## 页面格式

### 实体页

```markdown
# [实体名称]

> 类型: 人物/组织/项目/...

## 基本信息

- 创建时间: YYYY-MM-DD
- 最后更新: YYYY-MM-DD
- 来源文档: [[source:xxx]]

## 描述

[LLM 生成的描述]

## 相关实体

- [[entity:xxx]]
- [[entity:yyy]]

## 相关概念

- [[concept:xxx]]
```

### 概念页

```markdown
# [概念名称]

> 领域: xxx

## 定义

[LLM 生成的定义]

## 关键要点

- 要点1
- 要点2

## 相关来源

- [[source:xxx]]
```

## 修改历史

- {date}: 初始化 Wiki
""".format(date=datetime.utcnow().strftime("%Y-%m-%d"), base_dir=self.base_dir.name)

    def _write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _hash_content(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def scan_raw_sources(self) -> List[SourceDocument]:
        """扫描原始文档"""
        raw_path = self.base_dir / self.config.raw_dir
        documents = []

        # 支持的文件类型
        extensions = [".md", ".txt", ".json"]
        for ext in extensions:
            for file_path in raw_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        doc = SourceDocument(
                            path=file_path,
                            content=content,
                            hash=self._hash_content(content),
                            metadata={
                                "name": file_path.name,
                                "relative_path": str(file_path.relative_to(raw_path)),
                                "size": len(content),
                            }
                        )
                        documents.append(doc)
                    except Exception as e:
                        print(f"Warning: Could not read {file_path}: {e}")

        return documents

    def get_processed_sources(self) -> Dict[str, Dict]:
        """获取已处理源文档记录"""
        registry_path = self.base_dir / ".wiki_registry.json"
        if registry_path.exists():
            return json.loads(registry_path.read_text())
        return {}

    def mark_source_processed(self, source: SourceDocument):
        """标记源文档为已处理"""
        registry = self.get_processed_sources()
        registry[source.hash] = {
            "path": str(source.path),
            "name": source.metadata["name"],
            "processed_at": datetime.utcnow().isoformat(),
        }
        registry_path = self.base_dir / ".wiki_registry.json"
        registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False))

    def get_unprocessed_sources(self) -> List[SourceDocument]:
        """获取未处理的源文档"""
        all_sources = self.scan_raw_sources()
        processed = self.get_processed_sources()
        return [s for s in all_sources if s.hash not in processed]

    def append_log(self, entry_type: str, content: str, details: Optional[Dict] = None):
        """追加日志条目"""
        log_path = self.base_dir / self.config.wiki_dir / self.config.log_file
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        entry = f"\n## [{timestamp}] {entry_type}\n\n{content}\n"
        if details:
            entry += "\n**详情:**\n"
            for k, v in details.items():
                entry += f"- {k}: {v}\n"
        entry += "\n---\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def create_page(self, page_type: str, name: str, content: str, metadata: Optional[Dict] = None):
        """创建 Wiki 页面"""
        type_dir = self.base_dir / self.config.wiki_dir / f"{page_type}s"
        type_dir.mkdir(parents=True, exist_ok=True)

        # 清理文件名
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        page_path = type_dir / f"{safe_name}.md"

        # 添加 YAML frontmatter
        fm = {
            "title": name,
            "type": page_type,
            "created": datetime.utcnow().strftime("%Y-%m-%d"),
            "updated": datetime.utcnow().strftime("%Y-%m-%d"),
        }
        if metadata:
            fm.update(metadata)

        if frontmatter:
            full_content = frontmatter.dumps(frontmatter.Post(content, **fm))
        else:
            # 简单的 frontmatter 格式
            fm_str = "\n".join(f"{k}: {v}" for k, v in fm.items())
            full_content = f"---\n{fm_str}\n---\n\n{content}"

        self._write_file(page_path, full_content)
        return page_path

    def update_index(self):
        """更新索引"""
        wiki_path = self.base_dir / self.config.wiki_dir

        entities = list((wiki_path / "entities").glob("*.md")) if (wiki_path / "entities").exists() else []
        concepts = list((wiki_path / "concepts").glob("*.md")) if (wiki_path / "concepts").exists() else []
        summaries = list((wiki_path / "summaries").glob("*.md")) if (wiki_path / "summaries").exists() else []

        # 生成索引内容
        index_content = f"""# Wiki Index

> 所有 Wiki 页面的目录索引

## 📊 统计

- 总页面数: {len(entities) + len(concepts) + len(summaries)}
- 实体页: {len(entities)}
- 概念页: {len(concepts)}
- 摘要页: {len(summaries)}
- 最后更新: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}

---

## 📁 实体 (Entities)

> 人物、组织、项目等

"""
        for page in sorted(entities):
            title = self._get_page_title(page)
            index_content += f"- [[{title}]] - {page.relative_to(wiki_path)}\n"
        if not entities:
            index_content += "*(暂无)*\n"

        index_content += "\n---\n\n## 💡 概念 (Concepts)\n\n> 核心概念、方法论、技术等\n\n"
        for page in sorted(concepts):
            title = self._get_page_title(page)
            index_content += f"- [[{title}]] - {page.relative_to(wiki_path)}\n"
        if not concepts:
            index_content += "*(暂无)*\n"

        index_content += "\n---\n\n## 📄 摘要 (Summaries)\n\n> 文档摘要、读书笔记等\n\n"
        for page in sorted(summaries):
            title = self._get_page_title(page)
            index_content += f"- [[{title}]] - {page.relative_to(wiki_path)}\n"
        if not summaries:
            index_content += "*(暂无)*\n"

        # 写入索引
        index_path = wiki_path / self.config.index_file
        self._write_file(index_path, index_content)

    def _get_page_title(self, page: Path) -> str:
        """从页面获取标题"""
        if frontmatter:
            try:
                post = frontmatter.load(page)
                return post.get("title", page.stem)
            except:
                pass
        return page.stem

    def lint(self) -> List[Dict]:
        """健康检查"""
        issues = []
        wiki_path = self.base_dir / self.config.wiki_dir

        # 收集所有页面内容
        all_pages = list(wiki_path.rglob("*.md"))
        all_content = ""
        for page in all_pages:
            if page.name in [self.config.index_file, self.config.log_file]:
                continue
            all_content += page.read_text(encoding="utf-8", errors="ignore")

        # 检查孤立页面
        for page in all_pages:
            if page.name in [self.config.index_file, self.config.log_file]:
                continue
            page_name = page.stem
            if f"[[{page_name}]]" not in all_content and f"[[{page_name}|" not in all_content:
                issues.append({
                    "type": "orphan_page",
                    "severity": "warning",
                    "page": str(page.relative_to(wiki_path)),
                    "message": f"页面 '{page_name}' 没有被其他页面引用"
                })

        # 检查空目录
        for subdir in ["entities", "concepts", "summaries"]:
            dir_path = wiki_path / subdir
            if dir_path.exists() and not list(dir_path.glob("*.md")):
                issues.append({
                    "type": "empty_directory",
                    "severity": "info",
                    "directory": subdir,
                    "message": f"目录 '{subdir}' 为空"
                })

        return issues

    def status(self) -> Dict:
        """获取 Wiki 状态"""
        processed = self.get_processed_sources()
        unprocessed = self.get_unprocessed_sources()
        wiki_path = self.base_dir / self.config.wiki_dir

        entities = list((wiki_path / "entities").glob("*.md")) if (wiki_path / "entities").exists() else []
        concepts = list((wiki_path / "concepts").glob("*.md")) if (wiki_path / "concepts").exists() else []
        summaries = list((wiki_path / "summaries").glob("*.md")) if (wiki_path / "summaries").exists() else []

        return {
            "base_dir": str(self.base_dir),
            "processed_sources": len(processed),
            "unprocessed_sources": len(unprocessed),
            "wiki_pages": {
                "entities": len(entities),
                "concepts": len(concepts),
                "summaries": len(summaries),
                "total": len(entities) + len(concepts) + len(summaries)
            },
            "has_index": (wiki_path / self.config.index_file).exists(),
            "has_log": (wiki_path / self.config.log_file).exists(),
            "has_schema": (self.base_dir / self.config.schema_file).exists(),
        }

    def get_schema(self) -> str:
        """获取 Schema 内容"""
        schema_path = self.base_dir / self.config.schema_file
        if schema_path.exists():
            return schema_path.read_text(encoding="utf-8")
        return ""

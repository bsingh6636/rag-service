import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"

FALLBACK_METADATA = {
    "fastapi-features.md": {
        "title": "FastAPI features",
        "source": "https://fastapi.tiangolo.com/features/",
    },
    "fastapi-dependencies.md": {
        "title": "FastAPI Dependency Injection",
        "source": "https://fastapi.tiangolo.com/tutorial/dependencies/",
    },
    "fastapi-security.md": {
        "title": "FastAPI Security and Authentication",
        "source": "https://fastapi.tiangolo.com/tutorial/security/",
    },
    "fastapi-sql-databases.md": {
        "title": "FastAPI with SQL Databases",
        "source": "https://fastapi.tiangolo.com/tutorial/sql-databases/",
    },
    "fastapi-background-tasks.md": {
        "title": "FastAPI Background Tasks",
        "source": "https://fastapi.tiangolo.com/tutorial/background-tasks/",
    },
}


def parse_markdown_document(path: Path) -> dict[str, str]:
    raw_text = path.read_text(encoding="utf-8")
    if not raw_text.strip():
        raise ValueError(f"Document '{path.name}' is empty")

    title: str | None = None
    source: str | None = None
    content: str = raw_text

    # Extract YAML frontmatter if present
    if raw_text.startswith("---"):
        parts = raw_text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            content = parts[2].strip()
            for line in frontmatter.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip().lower()
                    val = val.strip().strip('"').strip("'")
                    if key == "title":
                        title = val
                    elif key == "source":
                        source = val

    # Fallback to known registry
    if path.name in FALLBACK_METADATA:
        if not title:
            title = FALLBACK_METADATA[path.name]["title"]
        if not source:
            source = FALLBACK_METADATA[path.name]["source"]

    # Fallback title from first markdown heading
    if not title:
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("#"):
                raw_title = line.lstrip("#").strip()
                if "{" in raw_title:
                    raw_title = raw_title.split("{")[0].strip()
                if raw_title:
                    title = raw_title
                    break

    # Fallback defaults
    if not title:
        title = path.stem.replace("-", " ").title()
    if not source:
        source = f"https://fastapi.tiangolo.com/{path.stem}/"

    return {
        "title": title,
        "source": source,
        "content": content,
    }


def load_documents() -> list[dict[str, str]]:
    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Documentation directory not found: {DOCS_DIR}")

    md_files = sorted(DOCS_DIR.glob("*.md"))
    if not md_files:
        raise ValueError(f"No markdown documents found in {DOCS_DIR}")

    documents = [parse_markdown_document(path) for path in md_files]
    logger.info("Loaded %d documents from %s", len(documents), DOCS_DIR)
    return documents


def load_document() -> dict[str, str]:
    """Backward compatibility helper returning the primary features document."""
    documents = load_documents()
    for doc in documents:
        if "features" in doc["source"]:
            return doc
    return documents[0]

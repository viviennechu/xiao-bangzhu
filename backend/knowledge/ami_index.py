"""AMI Montessori knowledge base — index .docx files and retrieve relevant snippets."""
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

AMI_DIR = os.environ.get(
    "AMI_KNOWLEDGE_DIR",
    "/Users/a_bab/Desktop/all_claude/ami蒙特梭利/ami"
)

# In-memory index: {filename: plain_text}
_index: dict[str, str] = {}


def _extract_text(path: Path) -> str:
    from docx import Document
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def load_index() -> None:
    """Load all .docx files under AMI_DIR into memory. Call once at startup."""
    global _index
    ami_path = Path(AMI_DIR)

    if not ami_path.exists():
        logger.warning("AMI directory not found: %s — knowledge base disabled", AMI_DIR)
        return

    docx_files = list(ami_path.rglob("*.docx"))
    loaded = 0
    for path in docx_files:
        try:
            text = _extract_text(path)
            if text.strip():
                _index[path.name] = text
                loaded += 1
        except Exception as exc:
            logger.warning("Failed to read AMI file %s: %s", path.name, exc)

    logger.info("AMI knowledge base loaded: %d documents", loaded)


def get_ami_snippet(topic_query: str) -> str | None:
    """Return the most relevant AMI text snippet (≤600 chars) for the given topic.

    Scores each indexed document by keyword overlap with the query.
    Returns None if no relevant document found.
    """
    if not _index:
        return None

    keywords = set(topic_query.lower().split())
    if not keywords:
        return None

    best_score = 0
    best_text = None

    for text in _index.values():
        text_lower = text.lower()
        score = sum(text_lower.count(kw) for kw in keywords)
        if score > best_score:
            best_score = score
            best_text = text

    if best_score == 0 or best_text is None:
        return None

    return best_text.strip()[:600]

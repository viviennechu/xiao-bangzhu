"""Smart style selector — pick the most topic-relevant articles from posts.json."""
import json
import os
import re
from pathlib import Path

POSTS_FILE = os.environ.get(
    "POSTS_JSON",
    "/Users/a_bab/Desktop/all_claude/關於大v/posts.json"
)

_posts: list[dict] = []


def _load_posts() -> list[dict]:
    global _posts
    if not _posts:
        path = Path(POSTS_FILE)
        if path.exists():
            with open(path, encoding="utf-8") as f:
                _posts = json.load(f)
    return _posts


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&[a-z]+;", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _score(post: dict, keywords: list[str]) -> int:
    searchable = (
        post.get("title", "") + " "
        + post.get("excerpt", "") + " "
        + " ".join(str(t) for t in post.get("tags", []))
    ).lower()
    return sum(searchable.count(kw) for kw in keywords)


def select_style_examples(
    topic_query: str,
    n: int = 3,
    category_filter: str | None = None,
) -> list[str]:
    """Return n article texts as style examples, scored by keyword relevance.

    Args:
        topic_query: The topic to match against article titles/excerpts/tags.
        n: Number of examples to return.
        category_filter: If provided, restrict to articles matching this category/tag.
                         Falls back to all articles if no matches found.

    Returns:
        List of plain-text article snippets (≤800 chars each).
    """
    posts = _load_posts()
    if not posts:
        return []

    keywords = [kw for kw in topic_query.lower().split() if len(kw) > 1]

    # Apply category filter if provided
    filtered = posts
    if category_filter:
        tag_lower = category_filter.lower()
        candidate = [
            p for p in posts
            if tag_lower in (p.get("title", "") + " ".join(str(t) for t in p.get("tags", []))
                             + " ".join(str(c) for c in p.get("categories", []))).lower()
        ]
        if candidate:
            filtered = candidate

    # Score and sort
    scored = [(p, _score(p, keywords)) for p in filtered]
    scored.sort(key=lambda x: -x[1])

    # Take top n with score > 0; fill remainder from most recent
    top = [p for p, s in scored if s > 0][:n]

    if len(top) < n:
        recent = sorted(
            [p for p in filtered if p not in top],
            key=lambda p: p.get("date", ""),
            reverse=True,
        )
        top.extend(recent[: n - len(top)])

    examples = []
    for post in top[:n]:
        content = _strip_html(post.get("content", ""))
        examples.append(content[:800])

    return examples

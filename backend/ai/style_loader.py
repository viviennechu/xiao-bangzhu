"""Load writing style examples — delegates to smart_style_selector."""
from ai.smart_style_selector import select_style_examples


def load_style_examples(n: int = 3, topic: str = "", category_filter: str | None = None) -> list[str]:
    """Return n style examples relevant to the given topic.

    Delegates to smart_style_selector which scores posts.json by keyword overlap.
    """
    return select_style_examples(topic_query=topic, n=n, category_filter=category_filter)

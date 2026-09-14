"""Search-term matching. Takes values only, never locators."""

from __future__ import annotations

import re
from typing import Any

from robot.api.deco import keyword


def _normalize(value: Any) -> str:
    """Strip to comparable characters so ``iphone17`` matches ``Apple iPhone 17``."""
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


@keyword("Search Term Should Be Searchable")
def search_term_should_be_searchable(term: Any) -> None:
    """Fail if the term has nothing that could match a product title."""
    if not _normalize(term):
        raise AssertionError(f"Search term must contain letters or numbers: {term!r}")


@keyword("Title Matches Search Term")
def title_matches_search_term(title: Any, term: Any) -> bool:
    """Return whether the title is relevant to the term."""
    search_term_should_be_searchable(term)
    return _normalize(term) in _normalize(title)

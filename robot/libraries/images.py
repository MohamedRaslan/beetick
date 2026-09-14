"""Image-state validation for `Image Should Be Fully Loaded`.

Takes the state dictionary read from the browser, so DOM access stays in the
resource file. The expected source pattern and size floor are passed in because
they describe the site rather than the check.
"""

from __future__ import annotations

import re
from typing import Any

from robot.api.deco import keyword


@keyword("Image State Should Be Loaded")
def image_state_should_be_loaded(
    state: Any,
    expected_alt: str,
    source_pattern: str,
    minimum_width: int,
) -> None:
    """Fail unless the browser decoded a real image belonging to ``expected_alt``."""
    if state["alt"] != expected_alt:
        raise AssertionError(
            "Image alt text should match the selected product. "
            f"Expected {expected_alt!r}, got {state['alt']!r}."
        )

    if not re.search(source_pattern, str(state["src"])):
        raise AssertionError(
            f"Image source should match {source_pattern!r}. State: {dict(state)}."
        )

    # A failed fetch leaves complete true with no intrinsic width.
    if state["complete"] is not True:
        raise AssertionError(f"Image did not finish loading. State: {dict(state)}.")

    natural_width = int(state["naturalWidth"])
    if natural_width < int(minimum_width):
        raise AssertionError(
            f"Image is too small to be real product media; expected at least "
            f"{minimum_width}px wide. State: {dict(state)}."
        )

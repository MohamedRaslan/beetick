"""Add-to-cart payload and URL parsing. Takes values only, never locators."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs, urlparse

from robot.api.deco import keyword


ADD_TO_CART_MESSAGE = "Product added to cart successfully"


@keyword("Get Offering Guid From Url")
def get_offering_guid_from_url(url: str) -> str:
    """Return the offering id identifying the variant on a product page URL."""
    values = parse_qs(urlparse(url).query).get("offering_id", [])

    if not values:
        raise AssertionError(f"Product URL has no offering_id: {url}")

    return values[0]


@keyword("Add To Cart Response Should Be Valid")
def add_to_cart_response_should_be_valid(
    response: Any, offering_guid: str, quantity: int = 1
) -> None:
    """Assert the mutation was made for ``offering_guid`` and succeeded.

    Checks the request payload as well as the response, so a success recorded
    for another product cannot pass. ``quantity`` is what the caller asked to
    add, not a property of the endpoint.
    """
    post_data = _as_json(response["request"]["postData"], "request postData")

    if post_data.get("offering_guid") != offering_guid:
        raise AssertionError(
            "Add-to-cart payload should use the selected offering. "
            f"Expected {offering_guid!r}, got {post_data.get('offering_guid')!r}."
        )

    expected_quantity = _as_int(quantity, "expected quantity")
    if _as_int(post_data.get("quantity"), "request quantity") != expected_quantity:
        raise AssertionError(
            f"Add-to-cart quantity should be {expected_quantity}. "
            f"Got {post_data.get('quantity')!r}."
        )

    body = _as_json(response["body"], "response body")

    if body.get("message") != ADD_TO_CART_MESSAGE:
        raise AssertionError(
            f"Unexpected add-to-cart message. Expected {ADD_TO_CART_MESSAGE!r}, "
            f"got {body.get('message')!r}."
        )

    total_quantity = _as_int(body.get("total_quantity"), "response total_quantity")
    if total_quantity <= 0:
        raise AssertionError(
            f"Cart should hold at least one item. Got total_quantity {total_quantity}."
        )


def _as_json(value: Any, field_name: str) -> dict[str, Any]:
    # postData and body arrive parsed or as JSON text depending on the endpoint.
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise AssertionError(f"Expected {field_name} to be JSON.") from error

    if not isinstance(value, dict):
        raise AssertionError(f"Expected {field_name} to be an object, got {value!r}.")

    return value


def _as_int(value: Any, field_name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise AssertionError(
            f"Expected {field_name} to be an integer, got {value!r}."
        ) from error

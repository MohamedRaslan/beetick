import { expect, type Page, type Response } from "@playwright/test";

const ADD_TO_CART_PATH = "/blink/api/v4/carts/add-to-cart";

export function getOfferingGuid(productUrl: string): string {
  const offeringGuid = new URL(productUrl).searchParams.get("offering_id");

  if (!offeringGuid) {
    throw new Error("Product URL has no offering_id");
  }

  return offeringGuid;
}

/** Register before the click that triggers it. */
export function waitForAddToCartResponse(page: Page): Promise<Response> {
  return page.waitForResponse((response) => {
    const url = new URL(response.url());

    return response.request().method() === "POST" && url.pathname.endsWith(ADD_TO_CART_PATH);
  });
}

export async function expectSuccessfulAddToCart(
  response: Response,
  reqPayload: { offering_guid: string; quantity: number },
): Promise<void> {
  expect(response.status()).toBe(200);
  // Only the fields this journey owns; the endpoint may carry others.
  expect(response.request().postDataJSON()).toMatchObject(reqPayload);

  const body = await response.json();
  expect(body).toMatchObject({
    message: "Product added to cart successfully",
    total_quantity: expect.any(Number),
  });
  expect(body.total_quantity).toBeGreaterThan(0);
}

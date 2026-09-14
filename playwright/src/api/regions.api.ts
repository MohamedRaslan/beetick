import { expect, type Page, type Response } from "@playwright/test";

const REGIONS_PATH = "/milano/api/v2/regions";

/** Register before navigating. */
export function waitForRegionsResponse(page: Page): Promise<Response> {
  return page.waitForResponse((response) => {
    const url = new URL(response.url());

    return (
      response.request().method() === "GET" &&
      url.pathname === REGIONS_PATH &&
      url.searchParams.has("localization_code")
    );
  });
}

export function expectSuccessfulRegionsResponse(response: Response): void {
  expect(
    response.status(),
    `Regions request failed: ${response.url()}`,
  ).toBe(200);
}

import { type Page } from "@playwright/test";

/** Navigation only; readiness is asserted through the header. */
export class HomePage {
  public constructor(
    private readonly page: Page,
    private readonly baseURL: string,
  ) {}

  public async open(): Promise<void> {
    // Third-party resources delay the load event; readiness is asserted separately.
    await this.page.goto(this.baseURL, { waitUntil: "domcontentloaded" });
  }
}

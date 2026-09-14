import { expect, type Locator, type Page } from "@playwright/test";

import { ProductCard } from "../components/product-card.component";
import { normalizeForProductMatch } from "../support/product-name";

export class SearchResultsPage {
  public readonly heading: Locator;
  public readonly products: Locator;

  public constructor(private readonly page: Page) {
    this.heading = page.getByRole("heading", { level: 1 });
    this.products = page.getByTestId("product-card");
  }

  public product(index: number): ProductCard {
    return new ProductCard(this.page, this.products.nth(index));
  }

  /** The first result whose title is relevant to the term, in page order. */
  public async firstProductMatching(searchTerm: string): Promise<ProductCard> {
    const normalizedSearchTerm = normalizeForProductMatch(searchTerm);

    if (!normalizedSearchTerm) {
      throw new Error("Search term must contain letters or numbers");
    }

    await expect(this.products.first()).toBeVisible();

    const productCount = await this.products.count();
    const inspectedProductNames: string[] = [];

    for (let index = 0; index < productCount; index += 1) {
      const candidate = this.product(index);
      const productName = await candidate.name();
      inspectedProductNames.push(productName);

      if (normalizeForProductMatch(productName).includes(normalizedSearchTerm)) {
        await expect(candidate.root).toBeVisible();
        return candidate;
      }
    }

    throw new Error(
      `Expected at least one search result title to match "${searchTerm}", ` +
        `but inspected ${productCount} result(s): ${inspectedProductNames.join(" | ")}`,
    );
  }
}

import { type Locator, type Page } from "@playwright/test";

export class ProductPage {
  public readonly heading: Locator;
  public readonly addToCartButton: Locator;
  /** Appears once the product is in the cart. */
  public readonly addedQuantityControl: Locator;

  public constructor(private readonly page: Page) {
    this.heading = page.getByRole("heading", { level: 1 });
    // Role lookups skip the aria-hidden duplicate in the sticky buy bar.
    this.addToCartButton = page.getByRole("button", {
      name: "Add to cart",
      exact: true,
    });
    this.addedQuantityControl = page.getByRole("button", {
      name: "Decrease quantity",
      exact: true,
    });
  }

  public async name(): Promise<string> {
    const productName = (await this.heading.innerText()).trim();

    if (!productName) {
      throw new Error("The product page has no visible heading");
    }

    return productName;
  }

  /** A gallery image in display order; index 0 is the main image. */
  public async image(index = 0): Promise<Locator> {
    return this.page
      .getByRole("img", { name: await this.name(), exact: true })
      .nth(index);
  }

  public async addToCart(): Promise<void> {
    await this.addToCartButton.click();
  }
}

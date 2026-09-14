import { type Locator, type Page } from "@playwright/test";

import { ProductPage } from "../pages/product.page";

export class ProductCard {
  public readonly title: Locator;
  public readonly image: Locator;
  public readonly link: Locator;

  public constructor(
    private readonly page: Page,
    public readonly root: Locator,
  ) {
    this.title = root.getByTestId("product-card-title");
    // Cards also carry a promotional badge image; the product image is first.
    this.image = root.locator("img[alt]").first();
    this.link = root.getByTestId("product-card-link");
  }

  public async name(): Promise<string> {
    const productName = (await this.title.innerText()).trim();

    if (!productName) {
      throw new Error("The selected product card has no visible title");
    }

    return productName;
  }

  public async open(): Promise<ProductPage> {
    await Promise.all([
      this.page.waitForURL((url) => url.pathname.startsWith("/en/p/")),
      this.link.click(),
    ]);

    return new ProductPage(this.page);
  }
}

import { expect, type Locator } from "@playwright/test";

import { SearchResultsPage } from "../pages/search-results.page";
import { CartDrawer } from "./cart-drawer.component";

export class SearchBox {
  public readonly input: Locator;

  public constructor(root: Locator) {
    // Two responsive copies are rendered; only one is visible.
    this.input = root.getByTestId("search-input").filter({ visible: true });
  }

  public async submit(term: string): Promise<SearchResultsPage> {
    const page = this.input.page();

    await this.input.fill(term);
    await Promise.all([
      page.waitForURL(
        (url) => url.pathname.endsWith("/en/s") && url.searchParams.get("q") === term,
      ),
      // Pressed on the input so an open suggestion cannot swallow it.
      this.input.press("Enter"),
    ]);

    return new SearchResultsPage(page);
  }
}

export class CartIcon {
  public readonly button: Locator;

  public constructor(root: Locator) {
    this.button = root.getByRole("button", { name: "Cart", exact: true });
  }

  public async open(): Promise<CartDrawer> {
    await this.button.click();

    // The drawer renders in a portal outside the header.
    return new CartDrawer(this.button.page().getByTestId("drawer-content"));
  }
}

/** The site header, present on every route. */
export class Header {
  public readonly search: SearchBox;
  public readonly cart: CartIcon;
  public readonly deliveryLocation: Locator;

  public constructor(
    public readonly root: Locator,
    private readonly expectedDeliveryLocation = "Cairo",
  ) {
    this.search = new SearchBox(root);
    this.cart = new CartIcon(root);
    this.deliveryLocation = root
      .getByText(/^Delivering to:/i)
      .filter({ visible: true });
  }

  public async waitUntilReady(): Promise<void> {
    await expect(this.deliveryLocation).toBeVisible();
    await expect(this.deliveryLocation).toContainText(this.expectedDeliveryLocation);
    await expect(this.search.input).toBeEditable();
  }
}

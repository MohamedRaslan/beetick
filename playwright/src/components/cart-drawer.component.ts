import { type Locator } from "@playwright/test";

import { normalizeForProductMatch } from "../support/product-name";

export class CartDrawerHeader {
  public readonly title: Locator;
  public readonly itemCount: Locator;

  public constructor(public readonly root: Locator) {
    this.title = root.getByTestId("drawer-title");
    this.itemCount = root.getByTestId("drawer-description");
  }
}

/** One product row in the cart drawer. */
export class CartItem {
  public readonly image: Locator;
  public readonly title: Locator;
  public readonly price: Locator;
  public readonly decrease: Locator;
  public readonly increase: Locator;
  public readonly quantity: Locator;

  public constructor(public readonly root: Locator) {
    this.image = root.locator("img");
    this.title = root.getByRole("heading");
    this.price = root.getByTestId("current-price");
    this.decrease = root.getByRole("button", {
      name: "Decrease quantity",
      exact: true,
    });
    this.increase = root.getByRole("button", {
      name: "Increase quantity",
      exact: true,
    });
    // The value sits in an unlabelled div right after the decrease button.
    this.quantity = root.locator('button[aria-label="Decrease quantity"] + div');
  }

  public async name(): Promise<string> {
    const itemName = (await this.title.innerText()).trim();

    if (!itemName) {
      throw new Error("The cart item has no visible title");
    }

    return itemName;
  }
}

export class CartDrawer {
  public readonly header: CartDrawerHeader;
  public readonly items: Locator;
  public readonly checkout: Locator;

  public constructor(public readonly root: Locator) {
    this.header = new CartDrawerHeader(root.getByTestId("drawer-header"));
    this.items = root.getByTestId("drawer-body").locator("article");
    // The checkout button's accessible name also carries the subtotal.
    this.checkout = root
      .getByTestId("drawer-footer")
      .getByRole("button", { name: /checkout/i });
  }

  /** Resolves one row by position, or by product name compared normalized. */
  public async item(indexOrProductName: number | string): Promise<CartItem> {
    // The body is populated by the cart request after the drawer opens.
    await this.items.first().waitFor();

    if (typeof indexOrProductName === "number") {
      return new CartItem(this.items.nth(indexOrProductName));
    }

    const expectedName = normalizeForProductMatch(indexOrProductName);
    const itemCount = await this.items.count();
    const inspectedNames: string[] = [];

    for (let index = 0; index < itemCount; index += 1) {
      const candidate = new CartItem(this.items.nth(index));
      const candidateName = await candidate.name();
      inspectedNames.push(candidateName);

      if (normalizeForProductMatch(candidateName) === expectedName) {
        return candidate;
      }
    }

    throw new Error(
      `Expected a cart item named "${indexOrProductName}", ` +
        `but inspected ${itemCount} item(s): ${inspectedNames.join(" | ")}`,
    );
  }
}

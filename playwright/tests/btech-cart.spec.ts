import { expectSuccessfulAddToCart, getOfferingGuid, waitForAddToCartResponse } from "../src/api/cart.api";
import { expect, test } from "../src/fixtures/btech.fixture";
import { expectLoadedImage, expectProductImagePresent } from "../src/support/image-assertions";

test.describe(
  "B.TECH search-to-cart journey",
  {
    tag: ["@smoke", "@e2e", "@ui", "@cart"],
    annotation: {
      type: "requirement",
      description:
        "Open B.TECH, search for the required product term, select the first matching result, add it to the cart, and verify the cart drawer.",
    },
  },
  () => {
    test.beforeEach("Open a ready storefront", async ({ btech }) => {
      await btech.open();
    });

    test.afterEach("Attach failure context", async ({ page }, testInfo) => {
      if (testInfo.status !== testInfo.expectedStatus) {
        await testInfo.attach("final-url", {
          body: page.url(),
          contentType: "text/plain",
        });
      }
    });

    test("adds the first matching search result to the cart", async ({ btech, page }) => {
      const searchTerm = "iphone17";
      const results = await test.step(`Search for ${searchTerm}`, async () => {
        const searchResults = await btech.header.search.submit(searchTerm);
        await expect(searchResults.heading).toHaveText(searchTerm);

        return searchResults;
      });

      const { firstResult, productName } =
        await test.step("Select the first matching result and verify its card image", async () => {
          const selectedResult = await results.firstProductMatching(searchTerm);
          await expect(selectedResult.root).toBeVisible();
          const selectedProductName = await selectedResult.name();
          await expectProductImagePresent(selectedResult.image, selectedProductName);

          return {
            firstResult: selectedResult,
            productName: selectedProductName,
          };
        });

      const product = await test.step("Open the selected product", async () => {
        const selectedProduct = await firstResult.open();
        await expect(selectedProduct.heading).toHaveText(productName);
        await expectLoadedImage(await selectedProduct.image(), productName);

        return selectedProduct;
      });

      await test.step("Add the selected product to the cart", async () => {
        await expect(product.addToCartButton).toBeVisible();
        await expect(product.addToCartButton).toBeEnabled();

        const offeringGuid = getOfferingGuid(page.url());
        const [addToCartResponse] = await Promise.all([waitForAddToCartResponse(page), product.addToCart()]);
        await expectSuccessfulAddToCart(addToCartResponse, { offering_guid: offeringGuid, quantity: 1 });
        await expect(product.addedQuantityControl).toBeVisible();
      });

      await test.step("Open the cart drawer and verify the selected product", async () => {
        const cart = await btech.header.cart.open();
        await expect(cart.root).toBeVisible();
        await expect(cart.header.title).toHaveText("Cart");
        await expect(cart.header.itemCount).toContainText("1");

        const item = await cart.item(productName);
        await expect(item.root).toBeVisible();
        await expect(item.title).toHaveText(productName);
        await expect(item.quantity).toHaveText("1");
      });
    });
  },
);

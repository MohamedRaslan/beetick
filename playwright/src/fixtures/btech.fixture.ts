import { expect, test as base } from "@playwright/test";

import { BtechApp } from "../app/btech.app";

type BtechFixtures = {
  btech: BtechApp;
};

/** Test entry point: use this `test` instead of Playwright's own. */
export const test = base.extend<BtechFixtures>({
  btech: async ({ baseURL, page }, use) => {
    if (!baseURL) {
      throw new Error("Playwright baseURL is not configured");
    }

    await use(new BtechApp(page, baseURL));
  },
});

export { expect };

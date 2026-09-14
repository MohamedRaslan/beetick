import { type Page } from "@playwright/test";

import {
  expectSuccessfulRegionsResponse,
  waitForRegionsResponse,
} from "../api/regions.api";
import { Header } from "../components/header.component";
import { HomePage } from "../pages/home.page";

/** Application entry point, supplied to every test by the `btech` fixture. */
export class BtechApp {
  public readonly home: HomePage;
  public readonly header: Header;

  public constructor(
    private readonly page: Page,
    baseURL: string,
  ) {
    this.header = new Header(page.locator("header"));
    this.home = new HomePage(page, baseURL);
  }

  public async open(): Promise<void> {
    const regionsResponsePromise = waitForRegionsResponse(this.page);
    const [, regionsResponse] = await Promise.all([
      this.home.open(),
      regionsResponsePromise,
    ]);

    // The header renders its delivery city from this response.
    expectSuccessfulRegionsResponse(regionsResponse);
    await this.header.waitUntilReady();
  }
}

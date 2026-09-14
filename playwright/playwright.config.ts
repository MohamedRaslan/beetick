import { defineConfig, devices } from "@playwright/test";
import dotenv from "dotenv";

dotenv.config({ quiet: true });

const baseURL = process.env.BEE_TICK_BASE_URL ?? "https://btech.com/en";
const parsedBaseURL = new URL(baseURL);
const isDemoReport = ["true", "1"].includes((process.env.BEE_TICK_DEMO_REPORT ?? "").toLowerCase());

if (!["http:", "https:"].includes(parsedBaseURL.protocol)) {
  throw new Error("BEE_TICK_BASE_URL must be an absolute HTTP(S) URL");
}

export default defineConfig({
  testDir: "./tests",
  outputDir: "./test-results",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  workers: 1,
  reporter: process.env.CI
    ? [
        ["github"],
        ["junit", { outputFile: "test-results/junit.xml" }],
        ...(isDemoReport ? ([["json", { outputFile: "test-results/demo-results.json" }]] as const) : []),
        ["html", { open: "never", outputFolder: "playwright-report" }],
      ]
    : [
        ["list"],
        ...(isDemoReport ? ([["json", { outputFile: "test-results/demo-results.json" }]] as const) : []),
        ["html", { open: "never", outputFolder: "playwright-report" }],
      ],
  use: {
    baseURL: parsedBaseURL.toString(),
    headless: true,
    screenshot: isDemoReport ? "on" : "only-on-failure",
    trace: isDemoReport ? "on" : "retain-on-failure",
    video: isDemoReport ? "on" : "off",
    viewport: { width: 1440, height: 900 },
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});

# Playwright TypeScript

This is the secondary implementation. It owns its Node.js dependencies and configuration under `playwright/`.

## Requirements

- Node.js 24 LTS
- Chromium system dependencies

## Recommended: pnpm

Enable Corepack, which provides the repository-pinned pnpm version, then run these commands from `playwright/`:

```powershell
corepack enable
pnpm install --frozen-lockfile
pnpm exec playwright install chromium
pnpm test
```

The run creates an HTML report in `playwright-report/`. Open the latest report with:

```powershell
pnpm report
```

For a headed run:

```powershell
pnpm test:headed
```

On Linux CI, install browser operating-system dependencies with:

```bash
pnpm exec playwright install --with-deps chromium
```

## Alternative: npm

Run these commands from `playwright/`:

```powershell
npm install --no-package-lock
npx playwright install chromium
npm test
```

Use `--no-package-lock` because `pnpm-lock.yaml` is the authoritative Node lockfile for this implementation.

For a headed npm run:

```powershell
npm run test:headed
```

Open the latest HTML report with:

```powershell
npm run report
```

## Configuration

Copy `.env.example` to `.env` only when the storefront URL needs a local override. `playwright.config.ts` loads this value.

| Variable | Default | Purpose |
| --- | --- | --- |
| `BEE_TICK_BASE_URL` | `https://btech.com/en` | Public storefront URL |

The required `iphone17` value is test data declared in `tests/btech-cart.spec.ts`, not an environment setting. Chromium, headless mode, reporter selection, and timeout bounds live in `playwright.config.ts`. Headless mode is the default; use `pnpm test:headed` or `npm run test:headed` for local debugging.

## Wait policy

Playwright's locator actions and web-first assertions auto-wait for actionable or asserted states. Add an explicit wait only for a specific observable condition, such as a targeted response, the expected URL, a loaded image, an updated cart count, or the visible cart drawer.

`BtechApp.open()` registers a targeted wait for the initial regions request before navigation, requires its `200` response, and then waits for the `Delivering to:` header to resolve to a city and for an editable search input. Navigation itself resolves at `domcontentloaded`: third-party resources delay the `load` event, and readiness is asserted through the regions response and the header instead. This is a narrow application-readiness barrier, not a replacement for UI assertions and not a claim that the regions request alone enables search.

Search and product navigation then rely on their expected URLs and user-visible state because those routes are rendered through Next.js React Server Components rather than a stable business API. Autocomplete is deliberately not awaited because Enter submission works without it once the header is ready. Search results are filtered by normalized title text, so `iphone17` can match a title rendered as `iPhone 17`; the test selects the first matching candidate in DOM order. The add-to-cart mutation remains the only business API contract assertion: its response wait is registered before the click, and the test verifies status `200`, the selected dynamic offering payload, and the expected success response before continuing with cart UI assertions.

| Scope | Maximum | Reason |
| --- | --- | --- |
| Web-first assertion | `10s` | Keeps UI checks bounded while allowing normal production-site rendering. |
| Navigation | Playwright default `30s` | Avoids a custom oversized navigation ceiling. |
| Image condition | `10s` | Gives a lazy-loaded image time to load after scrolling. |
| Whole test | `60s` | Caps the live journey without hiding slow failures. |

These values are upper bounds: execution continues as soon as the condition is met. Do not use `page.waitForTimeout()`, another fixed delay, or `networkidle` as a substitute for a user-visible condition.

## Reporting

Locally, Playwright uses the `list` reporter plus the HTML report. In CI, it switches to the built-in `github` reporter, writes `test-results/junit.xml`, and keeps the same HTML report. This gives terminal readability, code-review annotations, machine-readable CI output, and a browsable failure report without adding a third-party reporting dependency.

The spec uses `test.describe`, named setup/teardown hooks, and `test.step` blocks so the HTML report and trace viewer show the journey in business-readable chunks.

The GitHub Pages demo uses an opt-in showcase run so normal local execution does not record video for every pass:

```powershell
$env:BEE_TICK_DEMO_REPORT = "true"
pnpm exec playwright test
Remove-Item Env:\BEE_TICK_DEMO_REPORT
```

Good future options if the suite grows:

- Allure: useful for richer dashboards, history, severity/epic metadata, and stakeholder-friendly reporting, but it adds extra dependencies and usually Java/report-generation setup.
- CTRF: useful when multiple frameworks need one normalized JSON report format for aggregation or PR summaries.
- Monocart Reporter: useful for custom dashboards, trends, coverage-style views, and deeper visual analytics.
- Playwright blob reporter: useful when CI sharding is introduced and reports need to be merged.

For this assignment, built-in Playwright reporting plus failure traces/screenshots is the recommended default. HTML reports, traces, screenshots, JUnit XML, and test results are generated locally and ignored by Git.

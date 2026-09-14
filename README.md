# beetick

Dual-framework E2E automation showcase with Robot Framework, Playwright TypeScript, CI-generated evidence, videos, traces, and a live dashboard.

[![E2E](https://github.com/MohamedRaslan/beetick/actions/workflows/e2e.yml/badge.svg)](https://github.com/MohamedRaslan/beetick/actions/workflows/e2e.yml)

The required search-to-cart journey, implemented twice against the live storefront:

1. Open `https://btech.com/en`
2. Search for `iphone17`
3. Select the first matching result and verify it has an image
4. Add it to the cart
5. Open the cart

Nothing is mocked. There is no application to deploy, no test data to seed, and no credentials.

## Start here

[![Automation demo preview](https://mohamedraslan.github.io/beetick/preview.png)](https://mohamedraslan.github.io/beetick/)

**Live demo:** https://mohamedraslan.github.io/beetick/

**Architecture:** https://mohamedraslan.github.io/beetick/architecture.html

The GitHub Pages demo is updated by CI after the Robot and Playwright jobs finish. It includes the assignment walkthrough, latest status cards, direct links to the latest reports/videos/traces, execution history, and average timings.

## Quick start

**Robot Framework** — the primary implementation:

```bash
cd robot
uv sync --frozen
uv run rfbrowser init chromium
uv run robot --outputdir results --xunit xunit.xml tests
```

Report: `robot/results/report.html` · Step log: `robot/results/log.html`

**Playwright TypeScript** — the secondary implementation:

```bash
cd playwright
corepack enable
pnpm install --frozen-lockfile
pnpm exec playwright install chromium
pnpm test
```

Report: `pnpm report`

Both default to headless Chromium. For a visible browser use `--variable HEADLESS:false` or `pnpm test:headed`. Each implementation's README documents a `pip` / `npm` alternative.

## Repository map

| Path | What it is |
| --- | --- |
| [`robot/`](robot/README.md) | Robot Framework implementation — setup, wait policy, configuration |
| [`playwright/`](playwright/README.md) | Playwright TypeScript implementation — setup, wait policy, reporting |
| [`.github/workflows/e2e.yml`](.github/workflows/e2e.yml) | CI workflow that runs both suites and publishes the live dashboard |

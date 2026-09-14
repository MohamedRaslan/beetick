# B.TECH Test Automation

[![E2E](https://github.com/MohamedRaslan/beetick/actions/workflows/e2e.yml/badge.svg)](https://github.com/MohamedRaslan/beetick/actions/workflows/e2e.yml)

The B.TECH search-to-cart journey, implemented twice against the live storefront:

1. Open `https://btech.com/en`
2. Search for `iphone17`
3. Select the first matching result and verify it has an image
4. Add it to the cart
5. Open the cart

Nothing is mocked. There is no application to deploy, no test data to seed, and no credentials.

## Start here — [`demo/index.html`](demo/index.html)

**Open that file in a browser.** One page covering the assignment, the architecture of both implementations, and the real reports from executed runs — Robot's full step log, and Playwright's report with video and trace.

```bash
python demo/serve.py      # standard library only; opens http://127.0.0.1:8000/demo/
```

Opening the file directly works for everything except Playwright's trace viewer, which refuses `file://`. The server above is the one-command fix.

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
| [`demo/`](demo/index.html) | Visual walkthrough and the committed reports from executed runs |
| [`demo/notes.html`](demo/notes.html) | Engineering notes: decisions, limits, and pipeline placement |
| [`robot/`](robot/README.md) | Robot Framework implementation — setup, wait policy, configuration |
| [`playwright/`](playwright/README.md) | Playwright TypeScript implementation — setup, wait policy, reporting |
| [`.github/workflows/e2e.yml`](.github/workflows/e2e.yml) | CI running both suites as parallel jobs |

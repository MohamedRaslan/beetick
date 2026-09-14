# B.TECH Test Automation

This repository contains two independent implementations of the same B.TECH search-to-cart scenario:

1. Open `https://btech.com/en`.
2. Search for `iphone17`.
3. Select the first result whose title matches the search term and verify it has an image.
4. Add the selected product to the cart.
5. Open the cart drawer.

Each implementation owns its dependencies, environment example, setup instructions, execution commands, and generated output:

- [Robot Framework implementation](robot/README.md), the primary solution
- [Playwright TypeScript implementation](playwright/README.md), the secondary solution

The tests drive the public B.TECH website. There is no application to deploy, no test data to seed, and no credentials required.

## Start here — [`demo/index.html`](demo/index.html)

**Open that file in a browser.** It is a single self-contained page covering the assignment, the architecture of both implementations, the decisions behind them, and the real reports from executed runs — both suites passing, with Robot's full step log and Playwright's report, video, and trace attached.

```bash
python demo/serve.py      # standard library only; opens http://127.0.0.1:8000/demo/
```

Opening the file directly works for everything except Playwright's trace viewer, which refuses `file://`. The server above is the one-command fix.

## Quick Start

Each suite runs in well under a minute.

### Robot Framework — primary

```bash
cd robot
uv sync --frozen
uv run rfbrowser init chromium
uv run robot --outputdir results --xunit xunit.xml tests
```

**Report:** open `robot/results/report.html` for the summary, or `robot/results/log.html` for the step-by-step execution log. `results/xunit.xml` is the machine-readable output for CI.

### Playwright TypeScript — secondary

```bash
cd playwright
corepack enable
pnpm install --frozen-lockfile
pnpm exec playwright install chromium
pnpm test
```

**Report:** run `pnpm report` to open the HTML report, which includes a trace for any failed run.

Both suites default to headless Chromium. For a visible browser use `uv run robot --variable HEADLESS:false --outputdir results tests` or `pnpm test:headed`. Each README documents a `pip` / `npm` alternative if the recommended toolchain is unavailable.

## Test Design Notes

### What the image assertion proves, and what it does not

The journey checks the product image twice, deliberately at different depths:

- On the **search result card**, presence only: an image element is visible, its `alt` matches the selected product, and its `src` is not empty. This answers the requirement at the point the assignment names it.
- On the **product page**, that the browser genuinely fetched and decoded the image: `complete` is true, the intrinsic width is at least 200px, and the source comes from the product media CDN.

A failed fetch leaves `complete` true with `naturalWidth` at zero, so those two together catch the broken-image case that a visibility check misses entirely. The width floor rejects tracking pixels and blur-up placeholders that were never swapped for the real image, and the source check rejects fallback art served from elsewhere.

**None of this proves the image looks correct.** A valid, fully decoded photograph of the wrong product would pass, and so would a correct image hidden behind an overlay. Catching those needs pixel comparison.

Visual regression is excluded on purpose. This test selects its product dynamically — whichever live result matches the search term that day — so there is no stable baseline to compare against, and product photography on a public storefront changes without notice. Screenshot baselines here would fail on merchandising updates rather than on defects, which teaches people to ignore failures. Visual regression earns its place against a pinned fixture environment or a component library, not a production journey that picks its own subject.

### Browser lifecycle

Every test runs in a fresh browser context, so cart and session state cannot leak between runs:

- **Robot Framework** does this explicitly: `Test Setup    Open Fresh B.TECH Browser` and `Test Teardown    Close B.TECH Browser`. The teardown also captures a full-page screenshot when the test failed.
- **Playwright** gets the same isolation from its built-in `page` fixture, which creates a context per test and closes it afterwards, so the spec contains no explicit open or close. `beforeEach` opens a ready storefront; `afterEach` attaches the final URL on failure.

## Continuous Integration

[`.github/workflows/e2e.yml`](.github/workflows/e2e.yml) is a template that runs both suites as parallel jobs on push, pull request, and manual dispatch. Each job installs its own toolchain, runs headless Chromium, and uploads its reports as artifacts: Robot's `log.html`, `report.html`, and `xunit.xml`; Playwright's HTML report and failure traces. It has not been executed in this repository — verify the pinned action versions against your organisation's policy before enabling it on a protected branch.

Retries are deliberately set to zero. Against a live storefront, a visible failure with a trace is more honest than a hidden retry. If production instability proves recurrent, add exactly one retry and document the reason.

### Where the pipeline belongs

As written, the workflow lives in this repository and triggers on its own pushes and pull requests — which is right while the tests are the thing being changed. In a real delivery pipeline the trigger usually belongs to the **application** repository instead: a developer opens a PR, or a release lands on staging, and that repository runs this suite as a quality gate.

The suite needs no changes for that. It takes its target from `BEE_TICK_BASE_URL`, so the caller points it at whichever environment was just deployed. Two standard wirings:

| Approach | How it works | Fits when |
| --- | --- | --- |
| `workflow_call` | This workflow is marked reusable; the application repository invokes it as a job and gets pass/fail inline in its own checks. | Both repositories are in the same GitHub organisation. Simplest, and results block the PR directly. |
| `repository_dispatch` | The application's pipeline sends an event carrying the deployed URL; this repository runs and reports back through a commit status. | The application lives elsewhere — another org, GitLab, Jenkins — or the suite also runs on its own schedule. |

Making it callable is a small addition to the trigger block:

```yaml
on:
  workflow_call:
    inputs:
      base_url:
        type: string
        required: true

jobs:
  robot-e2e:
    env:
      BEE_TICK_BASE_URL: ${{ inputs.base_url }}
```

And from the application repository, after its deploy job:

```yaml
e2e:
  needs: deploy-staging
  uses: <owner>/beetick/.github/workflows/e2e.yml@main
  with:
    base_url: https://staging.example.com/en
```

## Tooling Policy

- Recommended: `uv` for Robot Framework and `pnpm` for Playwright TypeScript.
- Supported alternatives: an ordinary Python `venv` with `pip`, and `npm` for Node.js.
- Robot uses `robot/uv.lock` as its authoritative lock and exports `robot/requirements.txt` for `pip` users.
- Playwright uses `playwright/pnpm-lock.yaml` as its authoritative lock; the npm path installs from the same `package.json` without creating a second committed lockfile.

## Repository Map

| Path | What it is |
| --- | --- |
| `demo/` | The visual walkthrough and the committed reports from executed runs |
| `robot/` | Robot Framework implementation — the primary solution |
| `playwright/` | Playwright TypeScript implementation — the secondary solution |
| `.github/workflows/e2e.yml` | CI template running both suites |

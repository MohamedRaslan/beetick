# Robot Framework

This is the primary implementation. It uses Robot Framework with Browser Library and keeps its Python environment inside `robot/.venv`.

## Requirements

- Python 3.13
- Node.js 24 LTS, required by the standard Browser Library package
- Chromium system dependencies

## Project structure

Robot has two kinds of keywords in this project:

- Flow keywords in `resources/flows/`, which own the order of a journey and give the tests their vocabulary. A test reads only in terms of these.
- Implementation keywords in page, component, api, and assertion resources, which own locators, waits, image checks, and endpoint checks.

Underneath them, `resources/browser.resource` is the one technical import — Browser Library, `Collections`, and the Python helper modules in `libraries/`. Every resource that calls Browser keywords imports it.

Settings live in exactly one file, `config.py`: the storefront URL, browser, headless mode, the four timeout ceilings, and the expected delivery location. Only the URL is environment configuration, read from `.env`. The rest are runner policy — defaults in the file, overridden per run by `--variable`, which Robot gives priority over any variable file:

```powershell
uv run robot --variable HEADLESS:false --variable BROWSER:firefox tests
```

Every browser interaction is a Browser Library keyword called from a resource file, so each step appears in `log.html` and Browser's retrying assertions do the waiting. Python is reserved for logic that reads better as code than as Robot table syntax: search text normalization (`search.py`), `offering_id` extraction and add-to-cart request/response validation (`cart.py`), and image-state validation (`images.py`). Those keywords are value-only — they take strings, dictionaries, or a captured response, never a locator.

## Recommended: uv

Install `uv` on Windows with:

```powershell
winget install --id astral-sh.uv --exact
```

See the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) for macOS, Linux, and other installation methods.

Run these commands from `robot/`:

```powershell
uv sync --frozen
uv run rfbrowser init chromium
uv run robot --outputdir results --xunit xunit.xml tests
```

The run creates Robot's native `output.xml`, `log.html`, and `report.html` files under `results/`, plus `xunit.xml` for CI systems.

`uv sync` creates `.venv` automatically. `uv run` uses it without requiring shell activation.

For a headed run:

```powershell
uv run robot --variable HEADLESS:false --outputdir results --xunit xunit.xml tests
```

## VS Code

Install the `RobotCode - Robot Framework Support` extension, open `beetick/robot` as the workspace folder, and select `robot/.venv/Scripts/python.exe` (or `robot/.venv/bin/python`) as the interpreter. Run `uv sync --frozen` and `uv run rfbrowser init chromium` once, and the Test Explorer will discover and run the suite.

There is no `robot.toml`. It is RobotCode's configuration file, not Robot Framework's, so the documented `robot` commands ignore it — keeping settings in it meant they applied in the editor but not on the command line. Everything lives in `config.py` instead, and headed debugging is a `--variable` override.

If the editor reports `No keyword with name 'Wait For Elements State' found` while the suite still runs, the file being edited does not itself import the resource providing that keyword. Runtime resolves through the full import graph; editor diagnostics need a visible import from the current file, which is why every resource that calls Browser keywords imports `resources/browser.resource`.

On Linux CI, initialize Chromium and its operating-system dependencies with:

```bash
uv run rfbrowser init chromium --with-deps
```

## Alternative: venv and pip

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
rfbrowser init chromium
robot --outputdir results --xunit xunit.xml tests
```

macOS or Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
rfbrowser init chromium --with-deps
robot --outputdir results --xunit xunit.xml tests
```

`pyproject.toml` and `uv.lock` are authoritative. `requirements.txt` is generated from the lock for compatibility:

```powershell
uv export --only-dev --format requirements-txt --no-hashes --output-file requirements.txt
```

## Configuration

Copy `.env.example` to `.env` only when a default needs a local override. `config.py` loads it.

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `BEE_TICK_BASE_URL` | `https://btech.com/en` | Public storefront URL |

Everything else in `config.py` is runner policy rather than environment configuration, so it is changed per run with `--variable`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `BROWSER` | `chromium` | Browser Library engine |
| `HEADLESS` | `${TRUE}` | Headless mode |
| `ACTION_TIMEOUT` | `10s` | Ceiling for ordinary actions and assertions |
| `NAVIGATION_TIMEOUT` | `30s` | Ceiling for navigation and the startup regions response |
| `NETWORK_TIMEOUT` | `15s` | Ceiling for the add-to-cart response |
| `IMAGE_TIMEOUT` | `10s` | Ceiling for a lazy image to finish loading |
| `EXPECTED_DELIVERY_LOCATION` | `Cairo` | City the header should resolve to |

The required `iphone17` value is test data declared in `tests/btech_cart.robot`, not configuration of either kind.

## Wait policy

Browser Library's automatic waiting handles normal actions. Explicit waits are reserved for observable conditions such as the startup regions response, the visible `Delivering to:` header state, an editable search input, the URL changing, a matching search-result title, an image reaching `complete` with a positive `naturalWidth`, the add-to-cart response, and the cart drawer containing the selected product.

Search and product pages are rendered through Next.js React Server Components, so the Robot implementation follows the Playwright approach and does not assert a separate search/product backend API. Search results are filtered by normalized title text, so `iphone17` can match a title rendered as `iPhone 17`; the test selects the first matching candidate in DOM order. Add-to-cart is the one business mutation observed at the network level.

| Scope | Maximum | Reason |
| --- | --- | --- |
| Browser Library action/assertion default | `10s` | Keeps ordinary UI checks bounded. |
| Navigation | `30s` | Uses a modest ceiling for the live storefront navigation. |
| Startup regions response | `30s` | Arrives late in page load, so it uses the navigation ceiling rather than the network one. |
| Cart mutation response | `15s` | Follows a click, so it is expected promptly. |
| Image condition | `10s` | Gives a lazy-loaded image time to load after scrolling. |

There is intentionally no `Test Timeout`. Robot implements it with `SIGALRM` on POSIX, and signals can only be armed from the main thread, while Browser Library executes `Promise To` keywords in worker threads — the combination raises `ValueError: signal only works in main thread of the main interpreter` on Linux and macOS. It passes on Windows only because Robot uses a thread-based timer there. The per-operation ceilings above bound every wait, and CI caps the job at ten minutes.

These values are upper bounds: execution continues as soon as the condition is met. Do not use `Sleep` or another fixed delay to make the scenario pass.

Generated Robot reports, xUnit output, traces, and screenshots belong under `results/` and are ignored by Git.

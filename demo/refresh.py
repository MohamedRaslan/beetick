"""Refresh the demo reports, metrics, history, and preview image.

Default usage runs both suites in showcase mode for local review:

    python demo/refresh.py

Use ``--skip-runs`` in CI after downloading the fresh run artifacts. That
updates the published dashboard and includes the latest generated report
snapshot. ``--summary-only`` is available when only the dashboard data is needed.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = REPO_ROOT / "demo"
ROBOT_ROOT = REPO_ROOT / "robot"
PLAYWRIGHT_ROOT = REPO_ROOT / "playwright"
INDEX_HTML = DEMO_ROOT / "index.html"
PREVIEW_IMAGE = DEMO_ROOT / "preview.png"
HISTORY_JSON = DEMO_ROOT / "runs.json"

DEFAULT_BASE_URL = "https://btech.com/en"
DEFAULT_HISTORY_LIMIT = 50


@dataclass
class RunMetrics:
    status: str
    duration: str
    steps: str
    tests: str
    duration_seconds: float | None = None
    generated: datetime | None = None


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh the B.TECH automation demo.")
    parser.add_argument(
        "--skip-runs",
        action="store_true",
        help="reuse existing report files instead of executing the suites",
    )
    parser.add_argument(
        "--only",
        choices=["all", "robot", "playwright"],
        default="all",
        help="suite selection when running tests",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="show the browser while running the suites",
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="do not regenerate demo/preview.png",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="do not update demo/runs.json",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="update metrics/history without keeping generated reports in demo/",
    )
    parser.add_argument(
        "--history-limit",
        type=int,
        default=DEFAULT_HISTORY_LIMIT,
        help=f"default: {DEFAULT_HISTORY_LIMIT}",
    )
    parser.add_argument(
        "--robot-runner",
        choices=["auto", "uv", "robot"],
        default="auto",
        help="default: auto",
    )
    parser.add_argument(
        "--playwright-runner",
        choices=["auto", "pnpm", "npm"],
        default="auto",
        help="default: auto",
    )
    args = parser.parse_args()

    failures: list[str] = []

    if not args.skip_runs:
        if args.only in {"all", "robot"} and run_robot(args) != 0:
            failures.append("Robot Framework")

        if args.only in {"all", "playwright"} and run_playwright(args) != 0:
            failures.append("Playwright TypeScript")

    if not args.summary_only:
        sync_stable_artifact_links()

    robot_metrics = read_robot_metrics() or read_existing_metrics("robot")
    playwright_metrics = read_playwright_metrics() or read_existing_metrics("pw")
    update_index(robot_metrics, playwright_metrics)

    if not args.no_history:
        update_history(robot_metrics, playwright_metrics, args.history_limit)

    if args.summary_only:
        remove_tree(DEMO_ROOT / "reports")

    if not args.no_preview:
        capture_preview(args.playwright_runner)

    if failures:
        print(f"\nDemo refreshed, but these suite(s) failed: {', '.join(failures)}")
        return 1

    print("\nDemo refreshed.")
    return 0


def run_robot(args: argparse.Namespace) -> int:
    runner = pick_runner(args.robot_runner, ["uv", "robot"])
    report_dir = DEMO_ROOT / "reports" / "robot"
    remove_tree(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    command = robot_command(runner)
    command.extend(
        [
            "--variable",
            "RECORD_VIDEO:true",
            "--outputdir",
            str(report_dir),
            "--xunit",
            "xunit.xml",
        ]
    )

    if args.headed:
        command.extend(["--variable", "HEADLESS:false"])

    command.append("tests")

    return run(command, ROBOT_ROOT)


def run_playwright(args: argparse.Namespace) -> int:
    runner = pick_runner(args.playwright_runner, ["pnpm", "npm"])
    remove_tree(PLAYWRIGHT_ROOT / "playwright-report")
    remove_tree(PLAYWRIGHT_ROOT / "test-results")

    command = playwright_command(runner)
    if args.headed:
        command.append("--headed")

    env = os.environ.copy()
    env["BEE_TICK_DEMO_REPORT"] = "true"
    env["PLAYWRIGHT_HTML_OPEN"] = "never"

    status = run(command, PLAYWRIGHT_ROOT, env=env)

    report_src = PLAYWRIGHT_ROOT / "playwright-report"
    report_dest = DEMO_ROOT / "reports" / "playwright"
    if report_src.exists():
        remove_tree(report_dest)
        shutil.copytree(report_src, report_dest)

    results_json = PLAYWRIGHT_ROOT / "test-results" / "demo-results.json"
    if results_json.exists():
        shutil.copy2(results_json, report_dest / "results.json")

    return status


def robot_command(runner: str) -> list[str]:
    if runner == "uv":
        return ["uv", "run", "robot"]

    return ["robot"]


def playwright_command(runner: str) -> list[str]:
    if runner == "pnpm":
        return ["pnpm", "exec", "playwright", "test"]

    return ["npm", "exec", "--", "playwright", "test"]


def pick_runner(requested: str, choices: Sequence[str]) -> str:
    if requested != "auto":
        if shutil.which(requested) is None:
            raise SystemExit(f"Cannot find {requested!r} on PATH.")
        return requested

    for candidate in choices:
        if shutil.which(candidate):
            return candidate

    raise SystemExit(f"Cannot find any supported runner on PATH: {', '.join(choices)}")


def run(command: Sequence[str], cwd: Path, env: dict[str, str] | None = None) -> int:
    print(f"\n> {format_command(command)}")
    print(f"  cwd: {cwd.relative_to(REPO_ROOT)}")
    completed = subprocess.run(command, cwd=cwd, env=env)
    return completed.returncode


def read_robot_metrics() -> RunMetrics | None:
    output_xml = first_existing(
        ROBOT_ROOT / "results" / "output.xml",
        DEMO_ROOT / "reports" / "robot" / "output.xml",
    )
    if output_xml is None:
        return None

    root = ET.parse(output_xml).getroot()
    tests = root.findall(".//test")
    statuses = [test.find("status") for test in tests]
    passed = sum(1 for status in statuses if status is not None and status.get("status") == "PASS")
    total = len(tests)
    elapsed = sum(float(status.get("elapsed", "0")) for status in statuses if status is not None)
    keyword_count = sum(len(test.findall(".//kw")) for test in tests)

    return RunMetrics(
        status="PASSED" if passed == total and total > 0 else "FAILED",
        duration=format_duration_seconds(elapsed),
        steps=str(keyword_count),
        tests=f"{passed}/{total}",
        duration_seconds=elapsed,
        generated=parse_robot_generated(root.get("generated")),
    )


def read_playwright_metrics() -> RunMetrics | None:
    results_json = first_existing(
        PLAYWRIGHT_ROOT / "test-results" / "demo-results.json",
        DEMO_ROOT / "reports" / "playwright" / "results.json",
    )
    if results_json is None:
        return None

    data = json.loads(results_json.read_text(encoding="utf-8"))
    stats = data.get("stats", {})
    expected = int(stats.get("expected", 0))
    unexpected = int(stats.get("unexpected", 0))
    flaky = int(stats.get("flaky", 0))
    skipped = int(stats.get("skipped", 0))
    total = expected + unexpected + flaky + skipped
    passed = expected + flaky

    generated = None
    start_time = stats.get("startTime")
    if isinstance(start_time, str):
        generated = datetime.fromisoformat(start_time.replace("Z", "+00:00")).replace(tzinfo=None)

    duration_seconds = float(stats.get("duration", 0)) / 1000

    return RunMetrics(
        status="PASSED" if unexpected == 0 and total > 0 else "FAILED",
        duration=format_duration_seconds(duration_seconds),
        steps=str(count_playwright_steps(data)),
        tests=f"{passed}/{total}",
        duration_seconds=duration_seconds,
        generated=generated,
    )


def count_playwright_steps(data: dict) -> int:
    count = 0

    for result in iter_playwright_results(data):
        count += count_steps(result.get("steps", []))

    return count


def iter_playwright_results(node: dict) -> Iterable[dict]:
    for suite in node.get("suites", []):
        yield from iter_playwright_results(suite)

    for spec in node.get("specs", []):
        for test in spec.get("tests", []):
            yield from test.get("results", [])


def count_steps(steps: Sequence[dict]) -> int:
    total = 0
    for step in steps:
        if step.get("category") == "test.step":
            total += 1
        total += count_steps(step.get("steps", []))
    return total


def read_existing_metrics(prefix: str) -> RunMetrics:
    html_text = INDEX_HTML.read_text(encoding="utf-8")
    return RunMetrics(
        status=read_metric(html_text, f"{prefix}-status") or "UNKNOWN",
        duration=read_metric(html_text, f"{prefix}-duration") or "-",
        steps=read_metric(html_text, f"{prefix}-steps") or "-",
        tests=read_metric(html_text, f"{prefix}-tests") or "-",
        duration_seconds=parse_duration_seconds(read_metric(html_text, f"{prefix}-duration")),
    )


def update_index(robot: RunMetrics, playwright: RunMetrics) -> None:
    html_text = INDEX_HTML.read_text(encoding="utf-8")
    html_text = set_status(html_text, "robot-status", robot.status)
    html_text = set_metric(html_text, "robot-duration", robot.duration)
    html_text = set_metric(html_text, "robot-steps", robot.steps)
    html_text = set_metric(html_text, "robot-tests", robot.tests)

    html_text = set_status(html_text, "pw-status", playwright.status)
    html_text = set_metric(html_text, "pw-duration", playwright.duration)
    html_text = set_metric(html_text, "pw-steps", playwright.steps)
    html_text = set_metric(html_text, "pw-tests", playwright.tests)

    generated = max_date(robot.generated, playwright.generated) or datetime.now()
    html_text = set_metric(html_text, "generated", format_report_date(generated))

    base_url = os.environ.get("BEE_TICK_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    html_text = re.sub(
        r"against <code>.*?</code>",
        f"against <code>{html.escape(base_url)}</code>",
        html_text,
        count=1,
    )

    with INDEX_HTML.open("w", encoding="utf-8", newline="\n") as file:
        file.write(html_text)


def update_history(robot: RunMetrics, playwright: RunMetrics, limit: int) -> None:
    history = read_history()
    generated = max_date(robot.generated, playwright.generated) or datetime.now(timezone.utc)
    run_id = current_run_id(generated)
    workflow_run_url = current_workflow_run_url()
    base_url = os.environ.get("BEE_TICK_BASE_URL", DEFAULT_BASE_URL).rstrip("/")

    record = {
        "id": run_id,
        "source": "github-actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "local",
        "generatedAt": iso_datetime(generated),
        "branch": os.environ.get("GITHUB_REF_NAME"),
        "commit": short_commit(os.environ.get("GITHUB_SHA")),
        "workflowRunUrl": workflow_run_url,
        "baseUrl": base_url,
        "status": "PASSED" if robot.status == "PASSED" and playwright.status == "PASSED" else "FAILED",
        "robot": metric_record(robot),
        "playwright": metric_record(playwright),
        "totalDurationSeconds": sum_seconds(robot.duration_seconds, playwright.duration_seconds),
    }

    runs = [run for run in history.get("runs", []) if run.get("id") != run_id]
    runs.append(record)
    runs.sort(key=lambda run: str(run.get("generatedAt", "")))
    if limit > 0:
        runs = runs[-limit:]

    output = {
        "version": 1,
        "updatedAt": iso_datetime(datetime.now(timezone.utc)),
        "runs": runs,
    }
    HISTORY_JSON.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


def read_history() -> dict:
    if not HISTORY_JSON.exists():
        return {"version": 1, "runs": []}

    try:
        history = json.loads(HISTORY_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "runs": []}

    if not isinstance(history, dict):
        return {"version": 1, "runs": []}

    runs = history.get("runs", [])
    if not isinstance(runs, list):
        history["runs"] = []

    return history


def metric_record(metrics: RunMetrics) -> dict[str, object]:
    return {
        "status": metrics.status,
        "duration": metrics.duration,
        "durationSeconds": metrics.duration_seconds,
        "steps": metrics.steps,
        "tests": metrics.tests,
    }


def capture_preview(requested_runner: str) -> None:
    runner = pick_runner(requested_runner, ["pnpm", "npm"])
    output = str(PREVIEW_IMAGE)
    url = f"{INDEX_HTML.resolve().as_uri()}?theme=dark"

    if runner == "pnpm":
        command = [
            "pnpm",
            "exec",
            "playwright",
            "screenshot",
            "--browser=chromium",
            "--viewport-size=1442,780",
            url,
            output,
        ]
    else:
        command = [
            "npm",
            "exec",
            "--",
            "playwright",
            "screenshot",
            "--browser=chromium",
            "--viewport-size=1442,780",
            url,
            output,
        ]

    status = run(command, PLAYWRIGHT_ROOT)
    if status != 0:
        print("Preview screenshot was not refreshed.")


def sync_stable_artifact_links() -> None:
    playwright_report = DEMO_ROOT / "reports" / "playwright"
    playwright_results = PLAYWRIGHT_ROOT / "test-results" / "demo-results.json"
    if playwright_results.exists():
        playwright_report.mkdir(parents=True, exist_ok=True)
        shutil.copy2(playwright_results, playwright_report / "results.json")

    copy_latest(playwright_report / "data", "*.webm", playwright_report / "playwright-video.webm")
    copy_latest(playwright_report / "data", "*.zip", playwright_report / "playwright-trace.zip")

    robot_report = DEMO_ROOT / "reports" / "robot"
    copy_latest(robot_report, "*.webm", robot_report / "robot-video.webm")
    copy_latest(robot_report / "browser" / "traces", "*.zip", robot_report / "robot-trace.zip")


def copy_latest(source_dir: Path, pattern: str, destination: Path) -> None:
    if not source_dir.exists():
        return

    destination_resolved = destination.resolve()
    matches = [
        path
        for path in source_dir.rglob(pattern)
        if path.is_file() and path.resolve() != destination_resolved
    ]
    if not matches:
        return

    latest = max(matches, key=lambda path: path.stat().st_mtime)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(latest, destination)


def set_metric(html_text: str, key: str, value: str) -> str:
    pattern = re.compile(
        rf'(<(?P<tag>[a-z0-9]+)\b[^>]*data-metric="{re.escape(key)}"[^>]*>)(.*?)(</(?P=tag)>)',
        re.IGNORECASE | re.DOTALL,
    )
    return pattern.sub(
        lambda match: f"{match.group(1)}{html.escape(value)}{match.group(4)}",
        html_text,
        count=1,
    )


def set_status(html_text: str, key: str, value: str) -> str:
    status = value.upper()
    css_class = "pill" if status == "PASSED" else "pill fail"
    pattern = re.compile(
        rf'(<span\b[^>]*class=")[^"]*("[^>]*data-metric="{re.escape(key)}"[^>]*>)(.*?)(</span>)',
        re.IGNORECASE | re.DOTALL,
    )
    return pattern.sub(
        lambda match: f'{match.group(1)}{css_class}{match.group(2)}{html.escape(status)}{match.group(4)}',
        html_text,
        count=1,
    )


def read_metric(html_text: str, key: str) -> str | None:
    match = re.search(
        rf'<[^>]*data-metric="{re.escape(key)}"[^>]*>(.*?)</[^>]+>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match is None:
        return None

    return re.sub(r"\s+", " ", match.group(1)).strip()


def first_existing(*paths: Path) -> Path | None:
    for path in paths:
        if path.exists():
            return path

    return None


def remove_tree(path: Path) -> None:
    if not path.exists():
        return

    resolved = path.resolve()
    if REPO_ROOT.resolve() not in resolved.parents:
        raise RuntimeError(f"Refusing to remove a path outside this repository: {path}")

    shutil.rmtree(path)


def parse_robot_generated(value: str | None) -> datetime | None:
    if not value:
        return None

    return datetime.fromisoformat(value)


def parse_duration_seconds(value: str | None) -> float | None:
    if not value:
        return None

    minute_match = re.fullmatch(r"(\d+)m\s+([0-9.]+)s", value.strip())
    if minute_match:
        return int(minute_match.group(1)) * 60 + float(minute_match.group(2))

    second_match = re.fullmatch(r"([0-9.]+)s", value.strip())
    if second_match:
        return float(second_match.group(1))

    return None


def current_run_id(generated: datetime) -> str:
    github_run_id = os.environ.get("GITHUB_RUN_ID")
    github_attempt = os.environ.get("GITHUB_RUN_ATTEMPT")
    if github_run_id:
        return f"github-{github_run_id}-{github_attempt or '1'}"

    return f"local-{iso_datetime(generated)}"


def current_workflow_run_url() -> str | None:
    server_url = os.environ.get("GITHUB_SERVER_URL")
    repository = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")

    if server_url and repository and run_id:
        return f"{server_url}/{repository}/actions/runs/{run_id}"

    return None


def short_commit(value: str | None) -> str | None:
    return value[:7] if value else None


def sum_seconds(*values: float | None) -> float | None:
    available = [value for value in values if value is not None]
    if not available:
        return None

    return round(sum(available), 3)


def iso_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        return value.isoformat(timespec="seconds")

    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def max_date(*values: datetime | None) -> datetime | None:
    available = [value for value in values if value is not None]
    return max(available) if available else None


def format_report_date(value: datetime) -> str:
    return f"{value.day} {value.strftime('%B %Y')}"


def format_duration_seconds(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes}m {remainder:04.1f}s"


def format_command(command: Sequence[str]) -> str:
    return " ".join(shlex_quote(part) for part in command)


def shlex_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./:=+-]+", value):
        return value

    return '"' + value.replace('"', '\\"') + '"'


if __name__ == "__main__":
    sys.exit(main())

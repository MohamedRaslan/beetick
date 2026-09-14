async function loadHistory() {
  const body = document.querySelector("[data-history-body]");
  if (!body) return;

  try {
    const response = await fetch("runs.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`History request failed: ${response.status}`);

    const history = await response.json();
    renderHistory(Array.isArray(history.runs) ? history.runs : []);
  } catch {
    body.innerHTML = `<tr><td colspan="7">Run the CI workflow once to publish execution history.</td></tr>`;
  }
}

function renderHistory(runs) {
  const newestFirst = [...runs].sort((left, right) => {
    return String(right.generatedAt).localeCompare(String(left.generatedAt));
  });

  const body = document.querySelector("[data-history-body]");
  setText("[data-history-count]", newestFirst.length || "-");
  setText("[data-history-pass-rate]", passRate(newestFirst));
  setText("[data-history-robot-average]", averageDuration(newestFirst, "robot"));
  setText("[data-history-playwright-average]", averageDuration(newestFirst, "playwright"));

  const latestRun = newestFirst.find((run) => run.workflowRunUrl);
  if (latestRun) {
    document.querySelectorAll("[data-latest-run-link]").forEach((link) => {
      link.href = latestRun.workflowRunUrl;
    });
    setText("[data-latest-run-title]", `Latest run - ${latestRun.status === "PASSED" ? "both jobs green" : "needs review"}`);
    setStatus("[data-latest-run-status]", latestRun.status);
  }

  if (!newestFirst.length) {
    body.innerHTML = `<tr><td colspan="7">No executions have been published yet.</td></tr>`;
    return;
  }

  body.innerHTML = newestFirst.slice(0, 12).map((run) => {
    const runLabel = run.workflowRunUrl
      ? `<a href="${escapeAttribute(run.workflowRunUrl)}">#${escapeHtml(run.id.replace(/^github-/, ""))}</a>`
      : escapeHtml(run.id);

    return `
      <tr>
        <td>${formatDate(run.generatedAt)}</td>
        <td>${runLabel}</td>
        <td>${statusPill(run.status)}</td>
        <td>${escapeHtml(run.robot?.duration ?? "-")}</td>
        <td>${escapeHtml(run.playwright?.duration ?? "-")}</td>
        <td>${formatSeconds(run.totalDurationSeconds)}</td>
        <td>${escapeHtml(run.commit ?? "-")}</td>
      </tr>
    `;
  }).join("");
}

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
}

function setStatus(selector, status) {
  const element = document.querySelector(selector);
  if (!element) return;

  const normalized = status === "PASSED" ? "PASSED" : "FAILED";
  element.textContent = normalized;
  element.className = normalized === "PASSED" ? "pill" : "pill fail";
}

function passRate(runs) {
  if (!runs.length) return "-";

  const passed = runs.filter((run) => run.status === "PASSED").length;
  return `${Math.round((passed / runs.length) * 100)}%`;
}

function averageDuration(runs, key) {
  const values = runs
    .map((run) => run[key]?.durationSeconds)
    .filter((value) => Number.isFinite(value));

  if (!values.length) return "-";

  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  return formatSeconds(average);
}

function statusPill(status) {
  const normalized = status === "PASSED" ? "PASSED" : "FAILED";
  const className = normalized === "PASSED" ? "pill mini" : "pill mini fail";
  return `<span class="${className}">${normalized}</span>`;
}

function formatDate(value) {
  if (!value) return "-";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatSeconds(value) {
  if (!Number.isFinite(value)) return "-";

  if (value < 60) return `${value.toFixed(1)}s`;

  const minutes = Math.floor(value / 60);
  const seconds = value - minutes * 60;
  return `${minutes}m ${seconds.toFixed(1).padStart(4, "0")}s`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("'", "&#39;");
}

loadHistory();

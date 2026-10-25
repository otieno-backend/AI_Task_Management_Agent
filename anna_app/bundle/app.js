import { AnnaAppRuntime } from "/static/anna-apps/_sdk/latest/index.js";

const TOOL_ID =
  window.__ANNA_TOOL_IDS__?.["task-manager"] || "tool-dev-task-manager";

const $ = (selector) => document.querySelector(selector);

const status = $("#status");
const form = $("#task-form");
const listButton = $("#list-btn");
const summaryButton = $("#summary-btn");
const planButton = $("#plan-btn");
const createButton = $("#create-btn");
const connectionLabel = $("#connection-label");

let anna;
let busy = false;

const actionButtons = [
  listButton,
  summaryButton,
  planButton,
  createButton,
];

function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

function unwrapResponse(response) {
  let value = response;

  // Anna may wrap the Executa response in a result property.
  if (value?.result && typeof value.result === "object") {
    value = value.result;
  }

  if (value?.success === false) {
    throw new Error(value.error || "The task request failed.");
  }

  if (value?.data !== undefined) {
    return value.data;
  }

  return value;
}

function setBusy(value) {
  busy = value;

  for (const button of actionButtons) {
    button.disabled = value;
  }
}

function showMessage(message, type = "info", icon = "✦") {
  const className = type === "error"
    ? "error"
    : type === "success"
      ? "success"
      : "";

  status.innerHTML = `
    <div class="result-message ${className}">
      <span class="result-icon" aria-hidden="true">${icon}</span>
      <span>${escapeHTML(message)}</span>
    </div>
  `;
}

function renderRawDetails(raw) {
  return `
    <details class="json-toggle">
      <summary>View technical details</summary>
      <pre>${escapeHTML(JSON.stringify(raw, null, 2))}</pre>
    </details>
  `;
}

function renderTaskCard(task, reason = "") {
  const priority = String(task.priority || "MEDIUM").toLowerCase();
  const taskStatus = String(task.status || "PENDING").toLowerCase();
  const description = task.description
    ? `<p class="task-description">${escapeHTML(task.description)}</p>`
    : "";

  const dueDate = task.due_date
    ? `<span class="pill">Due ${escapeHTML(task.due_date)}</span>`
    : "";

  const reasonPill = reason
    ? `<span class="pill">${escapeHTML(reason.replaceAll("_", " "))}</span>`
    : "";

  return `
    <article class="task-row">
      <div>
        <h3>${escapeHTML(task.title || `Task ${task.id ?? ""}`)}</h3>
        ${description}
        <div class="task-meta">
          <span class="pill priority-${escapeHTML(priority)}">
            ${escapeHTML(priority)} priority
          </span>
          <span class="pill status-${escapeHTML(taskStatus)}">
            ${escapeHTML(String(task.status || "PENDING").replaceAll("_", " "))}
          </span>
          ${dueDate}
          ${reasonPill}
        </div>
      </div>
      <span class="stat-icon" aria-hidden="true">${
        taskStatus === "completed" ? "✓" : "•"
      }</span>
    </article>
  `;
}

function updateStats(summary) {
  if (!summary || typeof summary !== "object") return;

  const fields = {
    total: ["total", "count"],
    pending: ["pending"],
    completed: ["completed"],
    overdue: ["overdue"],
  };

  for (const [id, keys] of Object.entries(fields)) {
    const element = $(`#stat-${id}`);
    if (!element) continue;

    const key = keys.find((candidate) => summary[candidate] !== undefined);
    if (key !== undefined) {
      element.textContent = String(summary[key]);
    }
  }
}

function renderTaskList(data, raw) {
  const tasks = Array.isArray(data)
    ? data
    : Array.isArray(data?.results)
      ? data.results
      : Array.isArray(data?.tasks)
        ? data.tasks
        : [];

  if (data?.count !== undefined) {
    $("#stat-total").textContent = String(data.count);
  }

  $("#results-title").textContent = "My tasks";
  $("#result-subtitle").textContent =
    `${tasks.length} task${tasks.length === 1 ? "" : "s"} retrieved from your workspace.`;

  if (!tasks.length) {
    status.innerHTML = `
      <div class="result-message">
        <span class="result-icon" aria-hidden="true">✦</span>
        <span>No tasks to show yet. Create your first task to get started.</span>
      </div>
      ${renderRawDetails(raw)}
    `;
    return;
  }

  status.innerHTML = `
    <div class="result-list">
      ${tasks.map((task) => renderTaskCard(task)).join("")}
    </div>
    ${renderRawDetails(raw)}
  `;
}

function renderSummary(data, raw) {
  if (!data || typeof data !== "object") {
    showMessage("The API returned an unexpected summary format.", "error", "!");
    status.insertAdjacentHTML("beforeend", renderRawDetails(raw));
    return;
  }

  updateStats(data);

  const items = [
    ["Total tasks", data.total ?? data.count ?? 0],
    ["Pending", data.pending ?? 0],
    ["Completed", data.completed ?? 0],
    ["In progress", data.in_progress ?? 0],
    ["Cancelled", data.cancelled ?? 0],
    ["Overdue", data.overdue ?? 0],
  ];

  $("#results-title").textContent = "Your task summary";
  $("#result-subtitle").textContent =
    "A quick look at your workload and progress.";

  status.innerHTML = `
    <div class="summary-grid">
      ${items.map(([label, value]) => `
        <div class="summary-item">
          <span>${escapeHTML(label)}</span>
          <strong>${escapeHTML(value)}</strong>
        </div>
      `).join("")}
    </div>
    ${renderRawDetails(raw)}
  `;
}

function renderDailyPlan(data, raw) {
  const tasks = Array.isArray(data)
    ? data
    : Array.isArray(data?.tasks)
      ? data.tasks
      : Array.isArray(data?.results)
        ? data.results
        : [];

  $("#results-title").textContent = "Your daily plan";
  $("#result-subtitle").textContent =
    tasks.length
      ? `${tasks.length} task${tasks.length === 1 ? "" : "s"} to help you focus.`
      : "Your plan is ready.";

  if (!tasks.length) {
    status.innerHTML = `
      <div class="result-message">
        <span class="result-icon" aria-hidden="true">✓</span>
        <span>No tasks are scheduled in this plan. Enjoy the breathing room or add a new task.</span>
      </div>
      ${renderRawDetails(raw)}
    `;
    return;
  }

  status.innerHTML = `
    <div class="result-list">
      ${tasks.map((task) => renderTaskCard(task, task.reason || "")).join("")}
    </div>
    ${renderRawDetails(raw)}
  `;
}

function renderCreatedTask(data, raw) {
  const task = data?.task || data;

  $("#results-title").textContent = "Task created!";
  $("#result-subtitle").textContent =
    "Your new task has been saved to your workspace.";

  status.innerHTML = `
    <div class="result-message success">
      <span class="result-icon" aria-hidden="true">✓</span>
      <span>Success! Your task has been created.</span>
    </div>
    <div class="result-list" style="margin-top:14px">
      ${renderTaskCard(task)}
    </div>
    ${renderRawDetails(raw)}
  `;
}

async function callTool(method, args = {}) {
  if (busy) return null;

  setBusy(true);
  showMessage("Working on it…", "info", "◷");

  try {
    const raw = await anna.tools.invoke({
      tool_id: TOOL_ID,
      method,
      args,
    });

    const data = unwrapResponse(raw);

    await anna.storage.set({
      key: "task-manager:last-action",
      value: method,
    });

    connectionLabel.textContent = "Connected to your workspace";

    if (method === "list_tasks") {
      renderTaskList(data, raw);
    } else if (method === "get_task_summary") {
      renderSummary(data, raw);
    } else if (method === "get_daily_plan") {
      renderDailyPlan(data, raw);
    } else if (method === "create_task") {
      renderCreatedTask(data, raw);
    } else {
      showMessage("Action completed successfully.", "success", "✓");
      status.insertAdjacentHTML("beforeend", renderRawDetails(raw));
    }

    return { data, raw };
  } catch (error) {
    const message = error?.message || "Something went wrong. Please try again.";
    $("#results-title").textContent = "Something needs attention";
    $("#result-subtitle").textContent = "Your request could not be completed.";
    showMessage(message, "error", "!");
    connectionLabel.textContent = "Request failed — check the error above";
    return null;
  } finally {
    setBusy(false);
  }
}

function setActiveView(view) {
  document.querySelectorAll("[data-view]").forEach((button) => {
    const active = button.dataset.view === view;
    button.classList.toggle("active", active);

    if (active) {
      button.setAttribute("aria-current", "page");
    } else {
      button.removeAttribute("aria-current");
    }
  });

  const titles = {
    overview: [
      "Good to see you!",
      "Organize your work, focus on what matters, and make progress.",
    ],
    tasks: ["My tasks", "Everything you're working on, all in one place."],
    summary: ["Your progress", "A clear overview of how your tasks are going."],
    plan: ["Your daily plan", "Decide what deserves your attention today."],
  };

  const [title, subtitle] = titles[view] || titles.overview;
  $("#page-title").textContent = title;
  $("#page-subtitle").textContent = subtitle;

  if (view === "tasks") {
    callTool("list_tasks");
  } else if (view === "summary") {
    callTool("get_task_summary");
  } else if (view === "plan") {
    callTool("get_daily_plan");
  } else {
    $("#create-section").classList.remove("section-hidden");
    $("#results-section").classList.remove("section-hidden");
  }
}

async function main() {
  try {
    anna = await AnnaAppRuntime.connect();
  } catch {
    connectionLabel.textContent = "Anna host unavailable";
    showMessage(
      "Anna host unavailable. Open this app through the Anna development harness.",
      "error",
      "!"
    );
    return;
  }

  await anna.window.set_title({ title: "Task Manager" });

  listButton.addEventListener("click", () => callTool("list_tasks"));
  summaryButton.addEventListener("click", () => callTool("get_task_summary"));
  planButton.addEventListener("click", () => callTool("get_daily_plan"));

  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      setActiveView(button.dataset.view);
    });
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const title = $("#task-title").value.trim();
    const description = $("#task-description").value.trim();
    const priority = $("#task-priority").value;

    if (!title) {
      showMessage("Please enter a title for your task.", "error", "!");
      $("#task-title").focus();
      return;
    }

    const result = await callTool("create_task", {
      title,
      description,
      priority,
    });

    if (result) {
      form.reset();
      $("#task-priority").value = "MEDIUM";
    }
  });

  await anna.window.ready();

  connectionLabel.textContent = "Connected to your workspace";
  showMessage(
    "You're all set. Create a task or choose a quick action to get started.",
    "success",
    "✓"
  );
}

main();

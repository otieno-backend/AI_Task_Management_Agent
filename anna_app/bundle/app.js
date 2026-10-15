import { AnnaAppRuntime } from "/static/anna-apps/_sdk/latest/index.js";

const TOOL_ID = window.__ANNA_TOOL_IDS__?.["task-manager"] || "tool-dev-task-manager";

async function main() {
  const status = document.getElementById("status");
  const listButton = document.getElementById("list-btn");
  const summaryButton = document.getElementById("summary-btn");
  const planButton = document.getElementById("plan-btn");
  const form = document.getElementById("task-form");

  let anna;

  try {
    anna = await AnnaAppRuntime.connect();
  } catch {
    status.textContent =
      "Anna host unavailable. Open this app through the Anna development harness.";
    return;
  }

  await anna.window.set_title({ title: "Task Manager" });

  async function callTool(method, args = {}) {
    status.textContent = "Working…";

    try {
      const result = await anna.tools.invoke({
        tool_id: TOOL_ID,
        method,
        args,
      });

      await anna.storage.set({
        key: "task-manager:last-action",
        value: method,
      });

      status.textContent = JSON.stringify(result, null, 2);
      return result;
    } catch (error) {
      status.textContent = `Error: ${error.message}`;
      return null;
    }
  }

  listButton.addEventListener("click", () => callTool("list_tasks"));
  summaryButton.addEventListener("click", () => callTool("get_task_summary"));
  planButton.addEventListener("click", () => callTool("get_daily_plan"));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const title = document.getElementById("task-title").value.trim();
    const description =
      document.getElementById("task-description").value.trim();
    const priority = document.getElementById("task-priority").value;

    if (!title) {
      status.textContent = "Please enter a task title.";
      return;
    }

    const result = await callTool("create_task", {
      title,
      description,
      priority,
    });

    if (result?.result?.success || result?.success) {
      form.reset();
      document.getElementById("task-priority").value = "MEDIUM";
    }
  });

  await anna.window.ready();
  status.textContent = "Task Manager is ready.";
}

main();

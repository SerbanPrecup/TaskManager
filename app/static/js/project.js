function getCSRF() {
  const el = document.querySelector('meta[name="csrf-token"]');
  return el ? el.getAttribute("content") : "";
}
function jsonHeaders() {
  return {
    "Content-Type": "application/json",
    "X-CSRFToken": getCSRF(),
  };
}
function reload() {
  window.location.reload();
}

// DELETE PROJECT
window.deleteProject = function () {
  Swal.fire({
    title: "Are you sure?",
    text: "This will permanently delete the project and all related tasks.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Yes, delete it!",
    cancelButtonText: "Cancel",
    confirmButtonColor: "#d33",
  }).then((result) => {
    if (!result.isConfirmed) return;

    fetch(window.location.pathname + "/delete", {
      method: "POST",
      headers: jsonHeaders(),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          Swal.fire(
            "Deleted!",
            data.message || "The project has been deleted.",
            "success"
          ).then(() => (window.location.href = "/dashboard"));
        } else {
          Swal.fire(
            "Error",
            data.message || "Could not delete project.",
            "error"
          );
        }
      })
      .catch(() => Swal.fire("Error", "Request failed.", "error"));
  });
};

// ADD CONTRIBUTOR (by username)
window.addContributor = function () {
  Swal.fire({
    title: "Add Contributor",
    input: "text",
    inputLabel: "Username",
    inputPlaceholder: "Enter username to add",
    showCancelButton: true,
    confirmButtonText: "Add",
    preConfirm: (username) => {
      if (!username) {
        Swal.showValidationMessage("Please enter a username");
        return false;
      }
      return fetch(window.location.pathname + "/add-contributor", {
        method: "POST",
        headers: jsonHeaders(),
        body: JSON.stringify({ username: username.trim() }),
      })
        .then((response) => response.json())
        .catch(() => {
          Swal.showValidationMessage("Request failed. Try again.");
        });
    },
  }).then((result) => {
    if (result.isConfirmed && result.value) {
      const data = result.value;
      if (data.success) {
        Swal.fire("Success", data.message, "success").then(reload);
      } else {
        Swal.fire(
          "Error",
          data.message || "Could not add contributor.",
          "error"
        );
      }
    }
  });
};

// DELETE TASK
window.deleteTask = function (taskId) {
  Swal.fire({
    title: "Delete Task?",
    text: "This action cannot be undone.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Yes, delete it",
    cancelButtonText: "Cancel",
    confirmButtonColor: "#d33",
  }).then((result) => {
    if (!result.isConfirmed) return;

    fetch(`/task/${taskId}/delete`, {
      method: "POST",
      headers: jsonHeaders(),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) {
          Swal.fire(
            "Deleted!",
            data.message || "Task deleted.",
            "success"
          ).then(reload);
        } else {
          Swal.fire("Error", data.message || "Could not delete task.", "error");
        }
      })
      .catch(() => Swal.fire("Error", "Request failed.", "error"));
  });
};

// CHANGE PROJECT STATUS
window.changeProjectStatus = function () {
  Swal.fire({
    title: "Change Project Status",
    input: "select",
    inputOptions: {
      "Not Started": "Not Started",
      "In Progress": "In Progress",
      "On Hold": "On Hold",
      "Needs Review": "Needs Review",
      Completed: "Completed",
      Cancelled: "Cancelled",
      Delayed: "Delayed",
    },
    inputPlaceholder: "Select a new status",
    showCancelButton: true,
    confirmButtonText: "Update",
    preConfirm: (newStatus) => {
      return fetch(window.location.pathname + "/update-status", {
        method: "POST",
        headers: jsonHeaders(),
        body: JSON.stringify({ status: newStatus }),
      })
        .then((response) => response.json())
        .catch(() => {
          Swal.showValidationMessage("Failed to update project status.");
        });
    },
  }).then((result) => {
    if (result.isConfirmed && result.value && result.value.success) {
      Swal.fire("Updated", result.value.message, "success").then(reload);
    } else if (result.value && !result.value.success) {
      Swal.fire("Error", result.value.message, "error");
    }
  });
};

// DRAG & DROP TASK STATUS
window.allowDrop = function (ev) {
  ev.preventDefault();
};
window.drag = function (ev) {
  ev.dataTransfer.setData("text", ev.target.id);
};
window.drop = function (ev, newStatus) {
  ev.preventDefault();
  const taskCardId = ev.dataTransfer.getData("text");
  const taskId = taskCardId.split("-")[1];

  fetch(`/task/${taskId}/update-status`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify({ status: newStatus }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        reload();
      } else {
        Swal.fire("Error", data.message, "error");
      }
    })
    .catch(() => Swal.fire("Error", "Could not update task.", "error"));
};

// ADD TASK
window.addTask = function () {
  const tpl = document.getElementById("tpl-task-contributors");
  const contributorsHTML = tpl ? tpl.innerHTML : "";

  Swal.fire({
    title: "Add Task",
    html: `
      <input type="text" id="task-name" class="swal2-input" placeholder="Task Name" required>
      <textarea id="task-desc" class="swal2-textarea" placeholder="Description" required></textarea>

      <select id="task-status" class="swal2-select">
        <option value="To Do">To Do</option>
        <option value="In Progress">In Progress</option>
        <option value="Done">Done</option>
      </select>

      <select id="task-priority" class="swal2-select">
        <option value="1">Priority 1 (Low)</option>
        <option value="2">Priority 2 (Medium)</option>
        <option value="3">Priority 3 (High)</option>
      </select>
      <br>
      <label class="swal2-label mt-2">Deadline</label><br>
      <input type="date" id="task-deadline" class="swal2-input">
      <br>
      <label class="swal2-label mt-3">Contributors</label><br>
      <div id="task-contributors" class="contributor-box">
        ${contributorsHTML}
      </div>
    `,
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: "Create",
    preConfirm: () => {
      const name = document.getElementById("task-name").value.trim();
      const desc = document.getElementById("task-desc").value.trim();
      const status = document.getElementById("task-status").value;
      const priority = document.getElementById("task-priority").value;
      const deadline = document.getElementById("task-deadline").value;
      const contributorCheckboxes = document.querySelectorAll(
        '#task-contributors input[type="checkbox"]'
      );
      const contributorIds = Array.from(contributorCheckboxes)
        .filter((cb) => cb.checked)
        .map((cb) => cb.value);

      if (!name || !desc) {
        Swal.showValidationMessage("Name and Description are required");
        return false;
      }

      return {
        name,
        description: desc,
        status,
        priority,
        deadline,
        contributors: contributorIds,
      };
    },
  }).then((result) => {
    if (result.isConfirmed && result.value) {
      fetch(window.location.pathname + "/add-task", {
        method: "POST",
        headers: jsonHeaders(),
        body: JSON.stringify(result.value),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            Swal.fire("Success", data.message, "success").then(reload);
          } else {
            Swal.fire("Error", data.message || "Could not add task.", "error");
          }
        })
        .catch(() => Swal.fire("Error", "Request failed.", "error"));
    }
  });
};

// SET TASK CONTRIBUTORS
window.openSetTaskContributors = function (taskId) {
  fetch(`/task/${taskId}/contributors`, {
    headers: { "X-CSRFToken": getCSRF() },
  })
    .then((r) => r.json())
    .then((payload) => {
      if (!payload.success) {
        Swal.fire(
          "Error",
          payload.message || "Could not load contributors.",
          "error"
        );
        return;
      }

      const users = payload.users || [];
      if (!users.length) {
        Swal.fire(
          "Info",
          "No eligible contributors found for this project.",
          "info"
        );
        return;
      }

      const list = users
        .map(
          (u) => `
        <div class="form-check d-flex align-items-center mb-2">
          <input class="form-check-input me-2" type="checkbox" value="${
            u.id
          }" id="task-${taskId}-u-${u.id}" ${u.checked ? "checked" : ""}>
          <img src="${
            u.avatar
          }" alt="Pic" class="rounded-circle me-2" style="width:30px;height:30px;object-fit:cover;">
          <label class="form-check-label" for="task-${taskId}-u-${u.id}">
            ${u.fullname} (${u.username})
          </label>
        </div>
      `
        )
        .join("");

      const html = `
        <div style="margin-bottom:8px; display:flex; gap:8px; align-items:center;">
          <input type="text" id="filter-users" class="swal2-input" placeholder="Filter users..."
                style="flex:1; min-width:0; margin:0;">
          <button type="button" id="btn-select-all"
                  class="swal2-confirm swal2-styled"
                  style="padding:6px 12px; white-space:nowrap; flex:0 0 auto;">Select all</button>
          <button type="button" id="btn-deselect-all"
                  class="swal2-cancel swal2-styled"
                  style="padding:6px 12px; white-space:nowrap; flex:0 0 auto;">None</button>
        </div>
        <div class="contributor-box" style="max-height:260px;overflow:auto;">${list}</div>
      `;

      Swal.fire({
        title: "Set Task Contributors",
        html: html,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: "Save",
        didOpen: () => {
          const input = document.getElementById("filter-users");
          input.addEventListener("input", () => {
            const q = input.value.toLowerCase();
            document
              .querySelectorAll("#swal2-html-container .form-check")
              .forEach((row) => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(q) ? "" : "none";
              });
          });
          document
            .getElementById("btn-select-all")
            .addEventListener("click", () => {
              document
                .querySelectorAll(
                  '#swal2-html-container input[type="checkbox"]'
                )
                .forEach((cb) => (cb.checked = true));
            });
          document
            .getElementById("btn-deselect-all")
            .addEventListener("click", () => {
              document
                .querySelectorAll(
                  '#swal2-html-container input[type="checkbox"]'
                )
                .forEach((cb) => (cb.checked = false));
            });
        },
        preConfirm: () => {
          const checked = Array.from(
            document.querySelectorAll(
              '#swal2-html-container input[type="checkbox"]:checked'
            )
          ).map((cb) => parseInt(cb.value, 10));
          return checked;
        },
      }).then((res) => {
        if (!res.isConfirmed || res.value === undefined) return;

        fetch(`/task/${taskId}/set-contributors`, {
          method: "POST",
          headers: jsonHeaders(),
          body: JSON.stringify({ user_ids: res.value }),
        })
          .then((r) => r.json())
          .then((data) => {
            if (data.success) {
              Swal.fire("Saved", "Contributors updated.", "success").then(
                reload
              );
            } else {
              Swal.fire(
                "Error",
                data.message || "Could not update contributors.",
                "error"
              );
            }
          })
          .catch(() => Swal.fire("Error", "Request failed.", "error"));
      });
    })
    .catch(() => Swal.fire("Error", "Request failed.", "error"));
};

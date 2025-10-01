(function () {
  function getCSRF() {
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.getAttribute("content") : "";
  }

  window.createProject = function (options = {}) {
    const endpoint = options.endpoint || "/create-project";

    Swal.fire({
      title: "Create a New Project",
      html: `
        <form id="project-form" enctype="multipart/form-data">
          <input type="text" id="project-name" class="swal2-input" placeholder="Project Name" required>
          <textarea id="project-description" class="swal2-textarea" placeholder="Project Description" required></textarea>
          <input type="file" id="background-picture" class="swal2-file" accept="image/*">
          <div style="margin-top: 15px;">
            <label class="switch">
              <input type="checkbox" id="project-public" checked>
              <span class="slider"></span>
            </label>
            <span class="toggle-label">Public</span>
          </div>
        </form>
      `,
      focusConfirm: false,
      confirmButtonText: "Create",
      showCancelButton: true,
      preConfirm: () => {
        const name = document.getElementById("project-name").value.trim();
        const description = document
          .getElementById("project-description")
          .value.trim();
        const file = document.getElementById("background-picture").files[0];
        const isPublic = document.getElementById("project-public").checked;

        if (!name || !description) {
          Swal.showValidationMessage(
            "Please fill out the name and description."
          );
          return false;
        }

        const formData = new FormData();
        formData.append("name", name);
        formData.append("description", description);
        formData.append("is_public", isPublic ? "true" : "false");
        if (file) formData.append("background_picture", file);
        return formData;
      },
    })
      .then((res) => {
        if (!res.isConfirmed) return;

        fetch(endpoint, {
          method: "POST",
          headers: { "X-CSRFToken": getCSRF() },
          body: res.value,
        })
          .then((r) => r.json())
          .then((data) => {
            if (data.success) {
              Swal.fire(
                "Success",
                "Project created successfully!",
                "success"
              ).then(() => {
                if (typeof options.onSuccess === "function") {
                  options.onSuccess(data);
                } else {
                  location.reload();
                }
              });
            } else {
              Swal.fire(
                "Error",
                data.message || "Failed to create project.",
                "error"
              ).then(() => {
                if (typeof options.onError === "function")
                  options.onError(data);
              });
            }
          })
          .catch(() =>
            Swal.fire("Error", "An unexpected error occurred.", "error")
          );
      })
      .finally(() => {
        if (typeof options.afterClose === "function") options.afterClose();
      });
  };
})();

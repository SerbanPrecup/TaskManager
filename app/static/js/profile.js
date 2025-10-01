(function () {
  function getCSRF() {
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.getAttribute("content") : "";
  }

  // Change password
  $(document).on("click", ".btn-change-password", function (e) {
    e.preventDefault();
    const actionUrl = $(this).data("action");

    Swal.fire({
      title: "Change Password",
      html: `
        <input type="password" id="currentPassword" class="swal2-input" placeholder="Current Password">
        <input type="password" id="newPassword" class="swal2-input" placeholder="New Password">
        <input type="password" id="confirmPassword" class="swal2-input" placeholder="Confirm New Password">
      `,
      showCancelButton: true,
      preConfirm: () => {
        const currentPassword = $("#currentPassword").val();
        const newPassword = $("#newPassword").val();
        const confirmPassword = $("#confirmPassword").val();
        const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

        if (!currentPassword || !newPassword || !confirmPassword) {
          return Swal.showValidationMessage("All fields are required");
        }
        if (newPassword !== confirmPassword) {
          return Swal.showValidationMessage("New passwords do not match");
        }
        if (!regex.test(newPassword)) {
          return Swal.showValidationMessage(
            "Password must have min 8 chars, at least 1 uppercase, 1 lowercase and 1 number"
          );
        }
        return { currentPassword, newPassword };
      },
    }).then((result) => {
      if (!result.isConfirmed) return;

      $.ajax({
        url: actionUrl,
        type: "POST",
        headers: { "X-CSRFToken": getCSRF() },
        contentType: "application/json",
        data: JSON.stringify({
          currentPassword: result.value.currentPassword,
          newPassword: result.value.newPassword,
        }),
        success: (res) =>
          Swal.fire("Success", res.message || "Password changed.", "success"),
        error: (res) =>
          Swal.fire(
            "Error",
            res.responseJSON?.error || "Failed to change password.",
            "error"
          ),
      });
    });
  });

  // Inline edit: username / fullname / email
  $(document).on("click", "[data-edit]", function () {
    const field = $(this).data("edit");
    const $span = $(`#text-${field}`);
    const oldValue = ($span.text() || "").trim();

    Swal.fire({
      title: `Edit ${field}`,
      input: "text",
      inputValue: oldValue,
      showCancelButton: true,
      confirmButtonText: "Save Changes",
      preConfirm: (value) => {
        const v = (value || "").trim();
        if (!v) return Swal.showValidationMessage("Field cannot be empty");
        return v;
      },
    }).then((result) => {
      if (!result.isConfirmed) return;

      $.ajax({
        url: `/edit-${field}`,
        type: "POST",
        headers: { "X-CSRFToken": getCSRF() },
        contentType: "application/json",
        data: JSON.stringify({ [field]: result.value }),
        success: (res) => {
          Swal.fire("Updated!", res.message || "Saved", "success");
          $span.text(result.value);
        },
        error: (res) => {
          Swal.fire(
            "Error",
            res.responseJSON?.error || `Error updating ${field}`,
            "error"
          );
        },
      });
    });
  });
})();

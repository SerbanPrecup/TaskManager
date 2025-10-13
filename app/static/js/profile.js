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
      <div id="password-hint" class="text-start small mt-2 text-muted"></div>
    `,
      showCancelButton: true,
      confirmButtonText: "Change",
      didOpen: () => {
        const newPwInput = document.getElementById("newPassword");
        const hint = document.getElementById("password-hint");

        newPwInput.addEventListener("input", async () => {
          const newPassword = newPwInput.value;
          const csrf = getCSRF();
          if (!newPassword) {
            hint.innerHTML = "";
            return;
          }

          try {
            const res = await fetch(window.passwordCheckUrl, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf,
              },
              body: JSON.stringify({
                username: window.currentUsername || "",
                email: window.currentEmail || "",
                password: newPassword,
              }),
            });

            const data = await res.json();
            let output = "";

            output += data.length
              ? "✅ Minimum 8 characters<br>"
              : "❌ Minimum 8 characters<br>";
            output += data.uppercase
              ? "✅ At least one uppercase letter<br>"
              : "❌ At least one uppercase letter<br>";
            output += data.lowercase
              ? "✅ At least one lowercase letter<br>"
              : "❌ At least one lowercase letter<br>";
            output +=
              data.digit || data.special
                ? "✅ At least one number or special character<br>"
                : "❌ At least one number or special character<br>";
            output += data.username_in_password
              ? "❌ Must not contain your username<br>"
              : "✅ Does not contain your username<br>";
            output += data.email_in_password
              ? "❌ Must not contain part of your email<br>"
              : "✅ Does not contain part of your email<br>";
            output += data.simple_sequences
              ? "❌ Avoid simple patterns (123, abc, qwe)<br>"
              : "✅ No simple patterns detected<br>";

            hint.innerHTML = output;
          } catch {
            hint.innerHTML =
              "<span class='text-danger'>Error checking password strength.</span>";
          }
        });
      },
      preConfirm: () => {
        const currentPassword = $("#currentPassword").val();
        const newPassword = $("#newPassword").val();
        const confirmPassword = $("#confirmPassword").val();

        if (!currentPassword || !newPassword || !confirmPassword) {
          return Swal.showValidationMessage("All fields are required");
        }
        if (newPassword !== confirmPassword) {
          return Swal.showValidationMessage("New passwords do not match");
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

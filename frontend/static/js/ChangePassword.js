// Change-password card shared by the client and technician account settings pages.
document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("btnChangePassword");
  if (!button) return;

  button.addEventListener("click", async () => {
    const current = document.getElementById("currentPassword").value;
    const next = document.getElementById("newPassword").value;
    const confirm = document.getElementById("confirmPassword").value;

    if (!current || !next) {
      showToast("Fill in your current and new password.", "warning");
      return;
    }
    if (next !== confirm) {
      showToast("The new passwords do not match.", "warning");
      return;
    }
    if (next.length < 8 || !/\d/.test(next)) {
      showToast("The new password must have at least 8 characters and one number.", "warning");
      return;
    }

    try {
      const response = await fetch("/api/me/password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("authToken"),
        },
        body: JSON.stringify({ current_password: current, new_password: next }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = Array.isArray(data.detail) ? data.detail.map((e) => e.msg).join(" ") : data.detail;
        throw new Error(detail || "Could not change the password");
      }
      showToast("Password updated successfully!", "success");
      ["currentPassword", "newPassword", "confirmPassword"].forEach((id) => (document.getElementById(id).value = ""));
    } catch (err) {
      showToast(err.message, "error");
    }
  });
});

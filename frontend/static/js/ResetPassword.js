document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");
  const form = document.getElementById("resetForm");
  const emailField = document.getElementById("emailField");
  const requestButton = document.getElementById("requestButton");
  const passwordFields = document.getElementById("passwordFields");
  const newPassword = document.getElementById("newPassword");
  const confirmPassword = document.getElementById("confirmPassword");
  const confirmButton = document.getElementById("confirmButton");
  const message = document.getElementById("message");

  passwordFields.hidden = !token;
  passwordFields.style.display = token ? "flex" : "none";
  newPassword.required = Boolean(token);
  confirmPassword.required = Boolean(token);

  if (token) {
    emailField.hidden = true;
    emailField.style.display = "none";
    requestButton.hidden = true;
    requestButton.style.display = "none";
    passwordFields.hidden = false;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const response = await fetch("/api/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: document.getElementById("email").value }),
    });
    const data = await response.json();
    message.textContent = data.message || "Unable to process request.";
  });

  confirmButton.addEventListener("click", async () => {
    const newPasswordValue = newPassword.value;
    const confirmPasswordValue = confirmPassword.value;
    if (!newPassword.checkValidity() || !confirmPassword.checkValidity()) {
      message.textContent = "The password must contain at least 8 characters and one number.";
      return;
    }
    if (newPasswordValue !== confirmPasswordValue) {
      message.textContent = "Passwords do not match.";
      return;
    }
    const response = await fetch("/api/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, new_password: newPasswordValue }),
    });
    const data = await response.json();
    message.textContent = data.message || data.detail || "Unable to reset password.";
    if (response.ok) {
      confirmButton.disabled = true;
    }
  });
});
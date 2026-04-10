const selectEntity = document.getElementById("entity");
const extraFields = document.getElementById("extraFields");
const extraInputs = extraFields.querySelectorAll("input, select");
const registrationForm = document.getElementById("registrationForm");
const passwordInput = document.getElementById("password");
const passwordStrengthMsg = document.getElementById("passwordMessage");

// Manage visibility of internal fields
selectEntity.addEventListener("change", function () {
  if (this.value === "mina") {
    extraFields.style.display = "flex";
    extraInputs.forEach((input) => (input.required = true));
  } else {
    extraFields.style.display = "none";
    extraInputs.forEach((input) => (input.required = false));
  }
});

// Visual password strength indicator
passwordInput.addEventListener("input", function () {
  const pass = this.value;
  const hasLetters = /[a-zA-Z]/.test(pass);
  const hasNumbers = /\d/.test(pass);
  if (pass.length > 9 && hasLetters && hasNumbers) {
    passwordStrengthMsg.textContent = "Strength: High";
    passwordStrengthMsg.style.color = "green";
  } else if (pass.length > 6) {
    passwordStrengthMsg.textContent = "Strength: Medium";
    passwordStrengthMsg.style.color = "orange";
  } else {
    passwordStrengthMsg.textContent = "Strength: Low";
    passwordStrengthMsg.style.color = "red";
  }
});

// Form submission handler
registrationForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  // Field mapping to Pydantic schema attributes
  const newClient = {
    first_name: document.getElementById("name").value,
    last_name: document.getElementById("lastName").value,
    email: document.getElementById("email").value,
    password: passwordInput.value,
    entity: selectEntity.value,
    internal_account: document.getElementById("account")?.value || null,
    ip_address: document.getElementById("ip")?.value || null,
    group_name: document.getElementById("group")?.value || null,
    project_id: document.getElementById("project")?.value || null,
  };

  try {
    const response = await fetch("/api/client/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newClient),
    });

    const data = await response.json();

    if (response.ok) {
      alert(data.message || "Account created successfully");
      // Redirect to login on success
      window.location.href = "/login";
    } else {
      // Handle validation or duplicate errors
      if (Array.isArray(data.detail)) {
        const errorMsg = data.detail
          .map((err) => `${err.loc[1]}: ${err.msg}`)
          .join("\n");
        alert("Validation Error:\n" + errorMsg);
      } else {
        alert("Error: " + (data.detail || "Registration failed"));
      }
    }
  } catch (error) {
    console.error("Connection error:", error);
    alert(
      "Could not connect to the server. Please ensure the backend is running.",
    );
  }
});

const selectEntity = document.getElementById("entity");
const extraFields = document.getElementById("extraFields");
const extraInputs = extraFields.querySelectorAll("input, select");
const registrationForm = document.getElementById("registrationForm");
const passwordInput = document.getElementById("password");
const passwordStrengthMsg = document.getElementById("passwordMessage");
const togglePassword = document.getElementById("togglePassword");

const SVG_EYE_OPEN = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>`;
const SVG_EYE_OFF  = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.82l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.74-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/></svg>`;

// --- Password visibility toggle ---
if (togglePassword && passwordInput) {
  togglePassword.addEventListener("click", () => {
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      togglePassword.innerHTML = SVG_EYE_OFF;
    } else {
      passwordInput.type = "password";
      togglePassword.innerHTML = SVG_EYE_OPEN;
    }
  });
}



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

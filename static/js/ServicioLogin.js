document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const techModeBtn = document.getElementById("techModeBtn");
  const loginTitle = document.getElementById("title"); // ID corregido

  let isStaffMode = false;

  if (techModeBtn) {
    techModeBtn.addEventListener("click", () => {
      isStaffMode = !isStaffMode;
      loginTitle.textContent = isStaffMode ? "Staff Login" : "Client Login";
      techModeBtn.textContent = isStaffMode
        ? "Back to Client Login"
        : "Staff Access";

      // Opcional: un cambio de color para que se note
      techModeBtn.style.color = isStaffMode ? "var(--color-csic)" : "black";
    });
  }

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault(); // CRÍTICO: Evita que la página se recargue

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const endpoint = isStaffMode
      ? "/api/technician/login"
      : "/api/client/login";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("currentUser", JSON.stringify(data));
        window.location.href = isStaffMode
          ? "ServicioTecnico.html"
          : "ServicioUsuario.html";
      } else {
        alert(data.detail || "Invalid credentials");
      }
    } catch (error) {
      alert("Connection error. Is the server running?");
    }
  });
});

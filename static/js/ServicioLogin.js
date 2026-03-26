document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      try {
        // Ahora atacamos a la ruta unificada
        const response = await fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
          localStorage.setItem("currentUser", JSON.stringify(data));

          // El propio backend nos dice si es client o technician
          if (data.role === "technician") {
            window.location.href = "/static/html/ServicioTecnico.html";
          } else {
            window.location.href = "/static/html/ServicioCliente.html";
          }
        } else {
          let errorMsg = data.detail;
          if (Array.isArray(errorMsg))
            errorMsg = "Formato de datos incorrecto.";
          alert("Error: " + errorMsg);
        }
      } catch (err) {
        console.error("Error de conexión:", err);
        alert("No se pudo conectar con el servidor backend.");
      }
    });
  }
});

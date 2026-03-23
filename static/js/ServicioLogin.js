document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const techModeBtn = document.getElementById('techModeBtn');
    const loginTitle = document.getElementById('title');
    
    let isStaffMode = false;

    if (techModeBtn) {
        techModeBtn.addEventListener('click', () => {
            isStaffMode = !isStaffMode;
            if (loginTitle) {
                loginTitle.textContent = isStaffMode ? "Staff Login" : "Log in";
            }
            techModeBtn.textContent = isStaffMode ? "Back to Client" : "Staff Access";
            techModeBtn.style.backgroundColor = isStaffMode ? "var(--color-csic)" : "#555";
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log("Intentando hacer login. Modo Staff:", isStaffMode);

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const endpoint = isStaffMode ? '/api/technician/login' : '/api/client/login';

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();
                console.log("Respuesta del servidor:", data);

                if (response.ok) {
                    localStorage.setItem('currentUser', JSON.stringify(data));
                    window.location.href = isStaffMode ? "/static/html/ServicioTecnico.html" : "/static/html/ServicioUsuario.html";
                } else {
                    // Controlamos si el error es de FastAPI (Array de validación 422)
                    let errorMsg = data.detail;
                    if (Array.isArray(errorMsg)) {
                        errorMsg = "Formato de datos incorrecto. Revisa el email.";
                    }
                    alert("Error: " + errorMsg);
                }
            } catch (err) {
                console.error("Error de conexión:", err);
                alert("No se pudo conectar con el servidor backend.");
            }
        });
    }
});
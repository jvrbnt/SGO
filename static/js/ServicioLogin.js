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

                if (response.ok) {
                    localStorage.setItem('currentUser', JSON.stringify(data));
                    window.location.href = isStaffMode ? "/static/html/ServicioTecnico.html" : "/static/html/ServicioUsuario.html";
                } else {
                    alert(data.detail || "Invalid credentials. Please try again.");
                }
            } catch (err) {
                console.error("Connection error:", err);
                alert("Could not connect to the server.");
            }
        });
    }
});
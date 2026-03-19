const loginForm = document.getElementById('loginForm');
const techModeBtn = document.getElementById('techModeBtn');
const submitBtn = document.getElementById('submitBtn');
const signupLink = document.getElementById('signupLink');
const loginTitle = document.querySelector('#login h2');

let isTechMode = false;

// Alternar entre modo Cliente y modo Técnico
techModeBtn.addEventListener('click', (e) => {
    e.preventDefault();
    isTechMode = !isTechMode;

    if (isTechMode) {
        loginTitle.textContent = "Technician Login";
        submitBtn.textContent = "Log in as Staff";
        techModeBtn.textContent = "Back to Client Login";
        signupLink.style.display = "none"; // Los técnicos no se registran aquí
        document.querySelector('.separator').style.display = "none";
    } else {
        loginTitle.textContent = "Log in";
        submitBtn.textContent = "Log in";
        techModeBtn.textContent = "Staff Access";
        signupLink.style.display = "inline";
        document.querySelector('.separator').style.display = "inline";
    }
});

loginForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const credentials = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    // Seleccionamos el endpoint según el modo
    const loginUrl = isTechMode ? '/api/technician/login' : '/api/client/login';

    try {
        const response = await fetch(loginUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });

        const data = await response.json();

        if (response.ok) {
            // Guardamos el usuario con su rol
            const activeUser = {
                role: data.role,
                firstName: data.first_name,
                lastName: data.last_name,
                email: data.email,
                profilePicture: data.profile_picture,
                entity: data.entity || "IMN-Staff"
            };

            localStorage.setItem('activeUser', JSON.stringify(activeUser));

            // Redirección según el rol que devuelve el backend
            if (data.role === 'technician') {
                window.location.href = "/static/html/ServicioTecnico.html";
            } else {
                window.location.href = "/static/html/ServicioUsuario.html";
            }
        } else {
            alert(data.detail || "Invalid credentials");
        }
    } catch (error) {
        console.error("Connection error:", error);
        alert("Server is not responding. Check your connection.");
    }
});
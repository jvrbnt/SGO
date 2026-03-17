const selectEntidad = document.getElementById('entidad');
const camposExtra = document.getElementById('camposExtra');
const inputsExtra = camposExtra.querySelectorAll('input, select');
const registroForm = document.getElementById('registroForm');
const passwordInput = document.getElementById('contraseña');
const mensaje = document.getElementById('mensajePassword');

// Mostrar/Ocultar campos extra si es interno
selectEntidad.addEventListener('change', function() {
    if (this.value === "mina") {
        camposExtra.style.display = "flex"; 
        inputsExtra.forEach(input => input.required = true);
    } else {
        camposExtra.style.display = "none";
        inputsExtra.forEach(input => input.required = false);
    }
});

// Medidor de seguridad de contraseña
passwordInput.addEventListener('input', function() {
    const pass = this.value;
    const tieneLetras = /[a-zA-Z]/.test(pass);
    const tieneNumeros = /\d/.test(pass);
    if (pass.length > 9 && tieneLetras && tieneNumeros) {
        mensaje.textContent = "Seguridad: Alta"; mensaje.style.color = "green";
    } else if (pass.length > 6) {
        mensaje.textContent = "Seguridad: Media"; mensaje.style.color = "orange";
    } else {
        mensaje.textContent = "Seguridad: Baja"; mensaje.style.color = "red";
    }
});

// Enviar datos al Backend (PostgreSQL)
registroForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    
    // IMPORTANTE: Las llaves (keys) ahora están en INGLÉS para el Backend
    const nuevoUsuario = {
        first_name: document.getElementById('nombre').value,
        last_name: document.getElementById('apellidos').value,
        email: document.getElementById('email').value,
        password: passwordInput.value,
        entity: selectEntidad.value,
        // Campos extra MiNa
        research_group: document.getElementById('group').value || null,
        principal_investigator: document.getElementById('ip').value || null,
        internal_account: document.getElementById('cuenta').value || null,
        project_code: document.getElementById('proyecto').value || null
    };

    try {
        const response = await fetch('/api/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nuevoUsuario)
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.mensaje); 
            window.location.href = "/static/html/ServicioLogin.html";
        } else {
            alert(data.detail); 
        }
    } catch (error) {
        console.error("Error al conectar con el backend:", error);
        alert("Error de conexión.");
    }
});
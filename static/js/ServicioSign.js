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
    
    // Capturamos todos los valores, incluidos los campos de MiNa
    // Usamos || null para que si están vacíos se envíen como nulos al backend
    const nuevoUsuario = {
        nombre: document.getElementById('nombre').value,
        apellidos: document.getElementById('apellidos').value,
        email: document.getElementById('email').value,
        password: passwordInput.value,
        entidad: selectEntidad.value,
        // --- CAMPOS EXTRA PARA LA TABLA USUARIOS ---
        grupo: document.getElementById('group').value || null,
        ip: document.getElementById('ip').value || null,
        cuenta: document.getElementById('cuenta').value || null,
        proyecto: document.getElementById('proyecto').value || null
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
        alert("Error de conexión. Asegúrate de que tu servidor FastAPI está encendido.");
    }
});
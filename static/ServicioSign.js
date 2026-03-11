// 1. Selección de elementos
const selectEntidad = document.getElementById('entidad');
const camposExtra = document.getElementById('camposExtra');
const inputsExtra = camposExtra.querySelectorAll('input');
const registroForm = document.getElementById('registroForm');
const passwordInput = document.getElementById('contraseña'); // Aseguramos que esta variable sea global en el script
const mensaje = document.getElementById('mensajePassword');
const togglePassword = document.getElementById('togglePassword');

// 2. Lógica de campos extras (Mina, CSIC, UAM)
selectEntidad.addEventListener('change', function() {
    const seleccion = selectEntidad.value;
    if (seleccion === "mina" || seleccion === "csic" || seleccion === "uam") {
        camposExtra.style.display = "flex";
        inputsExtra.forEach(input => input.required = true);
    } else {
        camposExtra.style.display = "none";
        inputsExtra.forEach(input => input.required = false);
    }
});

// 4. Lógica de seguridad de contraseña
passwordInput.addEventListener('input', function() {
    const pass = passwordInput.value;
    const tieneLetras = /[a-zA-Z]/.test(pass);
    const tieneNumeros = /\d/.test(pass);
    const longitud = pass.length;

    if (longitud === 0) {
        mensaje.textContent = "";
        return;
    }

    if (longitud > 9 && tieneLetras && tieneNumeros) {
        mensaje.textContent = "Es muy segura";
        mensaje.style.color = "green";
    } else if ((longitud > 6 && tieneLetras && tieneNumeros) || (longitud > 8 && (tieneLetras || tieneNumeros))) {
        mensaje.textContent = "Es segura";
        mensaje.style.color = "orange";
    } else {
        mensaje.textContent = "No es segura";
        mensaje.style.color = "red";
    }
});

// 5. Envío del formulario (SOLO UNO)
registroForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const emailValue = document.getElementById('email').value;
    alert("Cuenta creada con el correo: " + emailValue);
    window.location.href = "ServicioLogin.html";
});
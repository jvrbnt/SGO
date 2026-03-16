const selectEntidad = document.getElementById('entidad');
const camposExtra = document.getElementById('camposExtra');
const inputsExtra = camposExtra.querySelectorAll('input, select');
const registroForm = document.getElementById('registroForm');
const passwordInput = document.getElementById('contraseña');
const mensaje = document.getElementById('mensajePassword');

selectEntidad.addEventListener('change', function() {
    if (this.value === "mina") {
        camposExtra.style.display = "flex"; 
        inputsExtra.forEach(input => input.required = true);
    } else {
        camposExtra.style.display = "none";
        inputsExtra.forEach(input => input.required = false);
    }
});

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

registroForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const nuevoUsuario = {
        nombre: document.getElementById('nombre').value,
        apellidos: document.getElementById('apellidos').value,
        email: document.getElementById('email').value,
        password: passwordInput.value,
        entidad: selectEntidad.value,
        fotoPerfil: "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png",
        peticiones: [],
        grupo: document.getElementById('group').value || null,
        ip: document.getElementById('ip').value || null,
        cuenta: document.getElementById('cuenta').value || null,
        proyecto: document.getElementById('proyecto').value || null
    };
    let usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];
    if (usuarios.some(u => u.email === nuevoUsuario.email)) {
        alert("Este correo ya está registrado.");
        return;
    }
    usuarios.push(nuevoUsuario);
    localStorage.setItem('usuarios', JSON.stringify(usuarios));
    alert("Cuenta creada con éxito");
    window.location.href = "/static/html/ServicioLogin.html";
});
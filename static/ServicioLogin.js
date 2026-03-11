const loginForm = document.getElementById('loginForm');
const passwordInput = document.getElementById('password');
const togglePassword = document.getElementById('togglePassword');

// Lógica para ver/ocultar contraseña
togglePassword.addEventListener('click', function () {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    
    // Cambiamos la imagen del ojo
    if (type === 'password') {
        this.src = 'https://images.icon-icons.com/3252/PNG/96/eye_show_regular_icon_205294.png';
    } else {
        this.src = 'https://images.icon-icons.com/3250/PNG/96/eye_show_filled_icon_201405.png';
    }
});

// Lógica al pulsar el botón de Login
loginForm.addEventListener('submit', function(event) {
    event.preventDefault(); // Evita que se recargue la página
    const email = document.getElementById('email').value;
    alert("Iniciando sesión con: " + email);
    // Aquí podrías redirigir a una página de "Bienvenida"
    // window.location.href = "PaginaPrincipal.html";
});
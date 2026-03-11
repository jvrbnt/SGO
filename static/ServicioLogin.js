const loginForm = document.getElementById('loginForm');

loginForm.addEventListener('submit', function(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Obtener "base de datos" de usuarios
    const usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];

    // Buscar coincidencia
    const usuarioValido = usuarios.find(u => u.email === email && u.password === password);

    if (usuarioValido) {
        // Guardamos el usuario actual en la sesión
        localStorage.setItem('usuarioActivo', JSON.stringify(usuarioValido));
        window.location.href = "ServicioUsuario.html";
    } else {
        alert("Usuario no encontrado o contraseña incorrecta. Por favor, regístrate.");
    }
});
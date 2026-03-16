const loginForm = document.getElementById('loginForm');

loginForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const credenciales = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credenciales)
        });

        const data = await response.json();

        if (response.ok) {
            // Reconstruimos el objeto que tu frontend espera para que ServicioUsuario.js no falle
            const usuarioActivo = {
                nombre: data.nombre,
                apellidos: data.apellidos,
                email: data.email,
                entidad: data.entidad,
                fotoPerfil: "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png",
                peticiones: [],
                grupo: null,
                ip: null,
                cuenta: null,
                proyecto: null
            };

            // Guardamos el usuario en la sesión
            localStorage.setItem('usuarioActivo', JSON.stringify(usuarioActivo));
            window.location.href = "ServicioUsuario.html";
        } else {
            // Error de credenciales incorrectas desde el backend
            alert(data.detail);
        }
    } catch (error) {
        console.error("Error al conectar con el backend:", error);
        alert("Error de conexión. Asegúrate de que tu servidor FastAPI está encendido.");
    }
});
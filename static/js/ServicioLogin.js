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
            // Mapeamos la respuesta del backend (Inglés) al objeto de sesión
            const usuarioActivo = {
                first_name: data.first_name,
                last_name: data.last_name,
                email: data.email,
                entity: data.entity,
                role: data.role,
                profile_picture: data.profile_picture || "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png",
                research_group: data.research_group,
                principal_investigator: data.principal_investigator,
                internal_account: data.internal_account,
                project_code: data.project_code,
                requests: data.requests || [] // Cambiado de 'peticiones' a 'requests'
            };

            localStorage.setItem('usuarioActivo', JSON.stringify(usuarioActivo));
            window.location.href = "/static/html/ServicioUsuario.html";
        } else {
            alert(data.detail);
        }
    } catch (error) {
        console.error("Error al conectar con el backend:", error);
        alert("Error de conexión.");
    }
});
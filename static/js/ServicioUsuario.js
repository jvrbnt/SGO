document.addEventListener("DOMContentLoaded", () => {
    // Recuperamos el usuario (ahora con nombres en inglés tras el login)
    const usuarioActivo = JSON.parse(localStorage.getItem('usuarioActivo'));
    
    // 1. Redirección de seguridad
    if (!usuarioActivo) {
        window.location.href = "/static/html/ServicioLogin.html";
        return;
    }

    // 2. Lógica de Nombre + Apellidos (Adaptado a first_name / last_name)
    let nombreAMostrar = "";
    // Mantenemos la lógica de apodo/nickname por si lo incluyes en el modelo
    if (usuarioActivo.nickname && usuarioActivo.nickname.trim() !== "") {
        nombreAMostrar = usuarioActivo.nickname;
    } else {
        const nombreCompleto = `${usuarioActivo.first_name || ""} ${usuarioActivo.last_name || ""}`.trim();
        nombreAMostrar = nombreCompleto !== "" ? nombreCompleto : "Usuario";
    }
    
    document.getElementById("nombreUsuarioBarra").textContent = nombreAMostrar;
    // Adaptado a profile_picture
    document.getElementById("iconoUsuario").src = usuarioActivo.profile_picture || "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";

    // 3. Renderizar Peticiones (Adaptado a 'requests')
    const contenedorLista = document.getElementById("listaPeticiones");
    function renderPeticiones() {
        contenedorLista.innerHTML = "";
        // Ahora usamos usuarioActivo.requests en lugar de peticiones
        if (usuarioActivo.requests) {
            usuarioActivo.requests.forEach(r => {
                const div = document.createElement("div");
                div.className = "peticion-card";
                div.innerHTML = `
                    <strong style="color: var(--azul-csic);">${r.service_name}</strong><br>
                    <small>Horas: ${r.hours} | Fecha: ${r.request_date}</small><br>
                    <p style="font-size:12px; margin-top:5px; color:#555;">${r.comment || 'Sin comentarios'}</p>
                `;
                contenedorLista.appendChild(div);
            });
        }
    }
    renderPeticiones();

    // 4. Menú Desplegable (Sin cambios)
    const perfilContainer = document.getElementById("perfilContainer");
    const menuDesplegable = document.getElementById("menuDesplegable");
    
    perfilContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        menuDesplegable.classList.toggle("oculto");
    });
    document.addEventListener("click", () => menuDesplegable.classList.add("oculto"));

    // 5. Acordeón de Servicios (Sin cambios)
    const botonesOferta = document.querySelectorAll(".botonOferta");
    botonesOferta.forEach(boton => {
        boton.addEventListener("click", function(e) {
            e.stopPropagation();
            this.nextElementSibling.classList.toggle("abierto");
        });
    });

    // 6. Enviar Peticiones (Actualizado con llaves en inglés para el futuro fetch)
    const btnEnviar = document.getElementById("btnEnviarPeticion");
    btnEnviar.addEventListener("click", () => {
        const formularios = document.querySelectorAll(".formulario-oferta");
        let algunaPeticion = false;

        formularios.forEach(form => {
            const horasInput = form.querySelector("input[type='number']");
            const comentarioInput = form.querySelector("input[type='text']");
            const horas = horasInput.value;
            const servicio = form.previousElementSibling.textContent;

            if (horas > 0) {
                if (!usuarioActivo.requests) usuarioActivo.requests = [];
                // Guardamos con las llaves que espera nuestro nuevo modelo Request
                usuarioActivo.requests.push({
                    service_name: servicio,
                    hours: parseFloat(horas),
                    comment: comentarioInput.value,
                    request_date: new Date().toLocaleDateString()
                });
                algunaPeticion = true;
                horasInput.value = "";
                comentarioInput.value = "";
                form.classList.remove("abierto");
            }
        });

        if (algunaPeticion) {
            // Guardamos localmente (más adelante haremos el fetch a /api/requests)
            localStorage.setItem('usuarioActivo', JSON.stringify(usuarioActivo));
            renderPeticiones();
            alert("Petición guardada localmente. Lista para ser sincronizada.");
        }
    });

    // 7. Navegación
    document.getElementById("cerrarSesion").addEventListener("click", () => {
        localStorage.removeItem('usuarioActivo');
        window.location.href = "/static/html/ServicioLogin.html";
    });

    document.getElementById("editarPerfil").addEventListener("click", () => {
        window.location.href = "/static/html/ServicioEdit.html";
    });
});
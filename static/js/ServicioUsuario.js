document.addEventListener("DOMContentLoaded", () => {
    const usuarioActivo = JSON.parse(localStorage.getItem('usuarioActivo'));
    
    // 1. Redirección de seguridad
    if (!usuarioActivo) {
        window.location.href = "/static/html/ServicioLogin.html";
        return;
    }

    // 2. Lógica de Nombre + Apellidos o Apodo
    let nombreAMostrar = "";
    if (usuarioActivo.apodo && usuarioActivo.apodo.trim() !== "") {
        nombreAMostrar = usuarioActivo.apodo;
    } else {
        // Combina nombre y apellidos si existen
        const nombreCompleto = `${usuarioActivo.nombre || ""} ${usuarioActivo.apellidos || ""}`.trim();
        nombreAMostrar = nombreCompleto !== "" ? nombreCompleto : "Usuario";
    }
    
    document.getElementById("nombreUsuarioBarra").textContent = nombreAMostrar;
    document.getElementById("iconoUsuario").src = usuarioActivo.fotoPerfil;

    // 3. Renderizar Peticiones existentes
    const contenedorLista = document.getElementById("listaPeticiones");
    function renderPeticiones() {
        contenedorLista.innerHTML = "";
        if (usuarioActivo.peticiones) {
            usuarioActivo.peticiones.forEach(p => {
                const div = document.createElement("div");
                div.className = "peticion-card";
                div.innerHTML = `
                    <strong style="color: var(--azul-csic);">${p.servicio}</strong><br>
                    <small>Horas: ${p.horas} | Fecha: ${p.fecha}</small><br>
                    <p style="font-size:12px; margin-top:5px; color:#555;">${p.comentario || 'Sin comentarios'}</p>
                `;
                contenedorLista.appendChild(div);
            });
        }
    }
    renderPeticiones();

    // 4. Menú Desplegable
    const perfilContainer = document.getElementById("perfilContainer");
    const menuDesplegable = document.getElementById("menuDesplegable");
    
    perfilContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        menuDesplegable.classList.toggle("oculto");
    });
    document.addEventListener("click", () => menuDesplegable.classList.add("oculto"));

    // 5. Acordeón de Servicios
    const botonesOferta = document.querySelectorAll(".botonOferta");
    botonesOferta.forEach(boton => {
        boton.addEventListener("click", function(e) {
            e.stopPropagation();
            this.nextElementSibling.classList.toggle("abierto");
        });
    });

    // 6. Enviar Peticiones
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
                if (!usuarioActivo.peticiones) usuarioActivo.peticiones = [];
                usuarioActivo.peticiones.push({
                    servicio: servicio,
                    horas: horas,
                    comentario: comentarioInput.value,
                    fecha: new Date().toLocaleDateString()
                });
                algunaPeticion = true;
                horasInput.value = "";
                comentarioInput.value = "";
                form.classList.remove("abierto");
            }
        });

        if (algunaPeticion) {
            localStorage.setItem('usuarioActivo', JSON.stringify(usuarioActivo));
            let usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];
            const index = usuarios.findIndex(u => u.email === usuarioActivo.email);
            if (index !== -1) {
                usuarios[index] = usuarioActivo;
                localStorage.setItem('usuarios', JSON.stringify(usuarios));
            }
            renderPeticiones();
            alert("Petición enviada correctamente.");
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
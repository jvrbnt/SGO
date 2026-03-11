document.addEventListener("DOMContentLoaded", () => {
    // 1. Verificar sesión y cargar datos del usuario
    const usuarioActivo = JSON.parse(localStorage.getItem('usuarioActivo'));
    if (!usuarioActivo) {
        window.location.href = "ServicioLogin.html";
        return;
    }

    // Actualizar foto de perfil con la del JSON
    const iconoUsuario = document.getElementById("iconoUsuario");
    iconoUsuario.src = usuarioActivo.fotoPerfil;

    // 2. Cargar peticiones previas del usuario en la interfaz
    const contenedorPeticiones = document.getElementById("peticiones");
    function renderPeticiones() {
        // Limpiar excepto el H2
        const h2 = contenedorPeticiones.querySelector("h2");
        contenedorPeticiones.innerHTML = "";
        contenedorPeticiones.appendChild(h2);

        usuarioActivo.peticiones.forEach(p => {
            const div = document.createElement("div");
            div.style.borderBottom = "1px solid #ccc";
            div.style.padding = "10px";
            div.innerHTML = `<strong>${p.servicio}</strong><br>Horas: ${p.horas}<br><small>${p.comentario}</small>`;
            contenedorPeticiones.appendChild(div);
        });
    }
    renderPeticiones();

    // 3. Lógica Menú Perfil
    const perfilContainer = document.getElementById("perfilContainer");
    const menuDesplegable = document.getElementById("menuDesplegable");
    perfilContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        menuDesplegable.classList.toggle("oculto");
    });
    document.addEventListener("click", () => menuDesplegable.classList.add("oculto"));

    // 4. Lógica expansión servicios
    const botonesOferta = document.querySelectorAll(".botonOferta");
    botonesOferta.forEach(boton => {
        boton.addEventListener("click", function(e) {
            e.stopPropagation();
            this.nextElementSibling.classList.toggle("abierto");
        });
    });

    // 5. ENVIAR PETICIÓN Y GUARDAR EN JSON
    const btnEnviar = document.getElementById("btnEnviarPeticion");
    btnEnviar.addEventListener("click", () => {
        const formularios = document.querySelectorAll(".formulario-oferta");
        let algunaPeticion = false;

        formularios.forEach(form => {
            const horas = form.querySelector("input[type='number']").value;
            const comentario = form.querySelector("input[type='text']").value;
            const servicio = form.previousElementSibling.textContent;

            if (horas > 0) {
                const nuevaPeticion = {
                    servicio: servicio,
                    horas: horas,
                    comentario: comentario,
                    fecha: new Date().toLocaleDateString()
                };
                usuarioActivo.peticiones.push(nuevaPeticion);
                algunaPeticion = true;
                // Limpiar campos
                form.querySelector("input[type='number']").value = "";
                form.querySelector("input[type='text']").value = "";
                form.classList.remove("abierto");
            }
        });

        if (algunaPeticion) {
            // Actualizar usuario activo en sesión
            localStorage.setItem('usuarioActivo', JSON.stringify(usuarioActivo));
            
            // Actualizar en la "base de datos" global de usuarios
            let usuarios = JSON.parse(localStorage.getItem('usuarios'));
            const index = usuarios.findIndex(u => u.email === usuarioActivo.email);
            usuarios[index] = usuarioActivo;
            localStorage.setItem('usuarios', JSON.stringify(usuarios));

            renderPeticiones();
            alert("Peticiones guardadas en tu perfil");
        } else {
            alert("Por favor, introduce horas en al menos un servicio.");
        }
    });

    // 6. Cerrar Sesión
    document.getElementById("cerrarSesion").addEventListener("click", () => {
        if(confirm("¿Cerrar sesión?")) {
            localStorage.removeItem('usuarioActivo');
            window.location.href = "ServicioLogin.html";
        }
    });
});
document.addEventListener("DOMContentLoaded", () => {
    const usuarioActivo = JSON.parse(localStorage.getItem('usuarioActivo'));
    const listaGlobal = document.getElementById("listaPeticionesGlobales");
    
    // Selectores de filtros
    const filtroEstado = document.getElementById("filtroEstado");
    const filtroTecnico = document.getElementById("filtroTecnico");
    const filtroServicio = document.getElementById("filtroServicio");
    if (!usuarioActivo) {
        window.location.href = "/SGO/static/html/ServicioLogin.html";
        return;
    }

    document.getElementById("nombreUsuarioBarra").textContent = usuarioActivo.apodo || usuarioActivo.nombre || "Técnico";
    document.getElementById("iconoUsuario").src = usuarioActivo.fotoPerfil || "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";

    function renderPeticiones() {
        listaGlobal.innerHTML = "";
        const usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];
        
        // Valores actuales de los filtros
        const valEstado = filtroEstado.value;
        const valTecnico = filtroTecnico.value;
        const valServicio = filtroServicio.value;

        usuarios.forEach(u => {
            if (u.peticiones) {
                u.peticiones.forEach((p, index) => {
                    const estado = p.estado || "Requested";
                    const tecnico = p.tecnico || null;
                    const servicio = p.servicio;

                    // APLICAR FILTROS
                    let cumpleEstado = (valEstado === "todos" || estado === valEstado);
                    let cumpleServicio = (valServicio === "todos" || servicio === valServicio);
                    let cumpleTecnico = true;

                    if (valTecnico === "sin_asignar") {
                        cumpleTecnico = (tecnico === null);
                    } else if (valTecnico === "mis_peticiones") {
                        cumpleTecnico = (tecnico === usuarioActivo.nombre);
                    }

                    // Si cumple con los 3 filtros, se dibuja
                    if (cumpleEstado && cumpleServicio && cumpleTecnico) {
                        const card = document.createElement("div");
                        card.className = `peticion-card ${tecnico ? 'reservada' : ''}`;
                        
                        card.innerHTML = `
                            <div>
                                <span class="badge-estado">${estado}</span>
                                <strong style="color: var(--azul-csic); font-size: 16px;">${servicio}</strong><br>
                                <p style="margin: 5px 0; font-size: 13px; color: #666;">
                                    👤 <b>Usuario:</b> ${u.nombre} ${u.apellidos}<br>
                                    📅 <b>Fecha:</b> ${p.fecha}<br>
                                    ⏱️ <b>Horas:</b> ${p.horas}h
                                </p>
                                <p style="font-size: 12px; color: #444; background: #f9f9f9; padding: 5px; border-radius: 4px;">
                                    💬 ${p.comentario || 'Sin comentarios'}
                                </p>
                            </div>
                            ${tecnico 
                                ? `<div class="tecnico-asignado">✅ Reservado por: ${tecnico}</div>`
                                : `<button class="btn-reservar" data-email="${u.email}" data-idx="${index}">Reservar Oferta</button>`
                            }
                        `;
                        listaGlobal.appendChild(card);
                    }
                });
            }
        });

        // Eventos de botones de reserva
        document.querySelectorAll(".btn-reservar").forEach(btn => {
            btn.addEventListener("click", function() {
                asignarPeticion(this.dataset.email, this.dataset.idx);
            });
        });
    }

    function asignarPeticion(email, idx) {
        let usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];
        const uIdx = usuarios.findIndex(u => u.email === email);

        if (uIdx !== -1) {
            usuarios[uIdx].peticiones[idx].estado = "Accepted";
            usuarios[uIdx].peticiones[idx].tecnico = usuarioActivo.nombre;
            localStorage.setItem('usuarios', JSON.stringify(usuarios));
            renderPeticiones();
        }
    }

    // Escuchar cambios en los filtros
    filtroEstado.addEventListener("change", renderPeticiones);
    filtroTecnico.addEventListener("change", renderPeticiones);
    filtroServicio.addEventListener("change", renderPeticiones);

    // Menú desplegable y navegación
    const perfilContainer = document.getElementById("perfilContainer");
    const menu = document.getElementById("menuDesplegable");
    perfilContainer.addEventListener("click", (e) => { e.stopPropagation(); menu.classList.toggle("oculto"); });
    document.addEventListener("click", () => menu.classList.add("oculto"));

    document.getElementById("cerrarSesion").addEventListener("click", () => {
        localStorage.removeItem('usuarioActivo');
        window.location.href = "/SGO/static/html/ServicioLogin.html";
    });

    document.getElementById("editarPerfil").addEventListener("click", () => {
        window.location.href = "/SGO/static/html/ServicioEdit.html";
    });

    renderPeticiones();
});
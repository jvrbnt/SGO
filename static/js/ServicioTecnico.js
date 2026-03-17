document.addEventListener("DOMContentLoaded", () => {
    const usuarioActivo = JSON.parse(localStorage.getItem('usuarioActivo'));
    const listaGlobal = document.getElementById("listaPeticionesGlobales");
    
    // Selectores de filtros
    const filtroEstado = document.getElementById("filtroEstado");
    const filtroTecnico = document.getElementById("filtroTecnico");
    const filtroServicio = document.getElementById("filtroServicio");

    if (!usuarioActivo) {
        window.location.href = "/static/html/ServicioLogin.html";
        return;
    }

    // Actualizado a first_name y profile_picture
    document.getElementById("nombreUsuarioBarra").textContent = usuarioActivo.nickname || usuarioActivo.first_name || "Técnico";
    document.getElementById("iconoUsuario").src = usuarioActivo.profile_picture || "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";

    function renderPeticiones() {
        listaGlobal.innerHTML = "";
        // Nota: Esto sigue usando localStorage para 'usuarios'. 
        // En casa, tras el login, este array 'usuarios' también debería estar en inglés.
        const usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];
        
        const valEstado = filtroEstado.value;
        const valTecnico = filtroTecnico.value;
        const valServicio = filtroServicio.value;

        usuarios.forEach(u => {
            // Cambiado de u.peticiones a u.requests
            if (u.requests) {
                u.requests.forEach((r, index) => {
                    // Adaptado a los nombres del modelo Request (status, technician_name, etc.)
                    const estado = r.status || "requested";
                    const tecnico = r.technician_name || null;
                    const servicio = r.service_name;

                    // APLICAR FILTROS (Mapeo de valores de los filtros a los estados en inglés)
                    // Nota: Si el <select> en HTML tiene value="Requested", debe coincidir con el status
                    let cumpleEstado = (valEstado === "todos" || estado.toLowerCase() === valEstado.toLowerCase());
                    let cumpleServicio = (valServicio === "todos" || servicio === valServicio);
                    let cumpleTecnico = true;

                    if (valTecnico === "sin_asignar") {
                        cumpleTecnico = (tecnico === null);
                    } else if (valTecnico === "mis_peticiones") {
                        // Comparación con el nombre del técnico logueado
                        cumpleTecnico = (tecnico === usuarioActivo.first_name);
                    }

                    if (cumpleEstado && cumpleServicio && cumpleTecnico) {
                        const card = document.createElement("div");
                        card.className = `peticion-card ${tecnico ? 'reservada' : ''}`;
                        
                        card.innerHTML = `
                            <div>
                                <span class="badge-estado">${estado}</span>
                                <strong style="color: var(--azul-csic); font-size: 16px;">${servicio}</strong><br>
                                <p style="margin: 5px 0; font-size: 13px; color: #666;">
                                    👤 <b>Usuario:</b> ${u.first_name} ${u.last_name}<br>
                                    📅 <b>Fecha:</b> ${r.request_date}<br>
                                    ⏱️ <b>Horas:</b> ${r.hours}h
                                </p>
                                <p style="font-size: 12px; color: #444; background: #f9f9f9; padding: 5px; border-radius: 4px;">
                                    💬 ${r.comment || 'Sin comentarios'}
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
            // Actualización a nombres en inglés: status y technician_name
            usuarios[uIdx].requests[idx].status = "offered"; // O "accepted" según tu flujo
            usuarios[uIdx].requests[idx].technician_name = usuarioActivo.first_name;
            localStorage.setItem('usuarios', JSON.stringify(usuarios));
            renderPeticiones();
        }
    }

    filtroEstado.addEventListener("change", renderPeticiones);
    filtroTecnico.addEventListener("change", renderPeticiones);
    filtroServicio.addEventListener("change", renderPeticiones);

    const perfilContainer = document.getElementById("perfilContainer");
    const menu = document.getElementById("menuDesplegable");
    perfilContainer.addEventListener("click", (e) => { e.stopPropagation(); menu.classList.toggle("oculto"); });
    document.addEventListener("click", () => menu.classList.add("oculto"));

    document.getElementById("cerrarSesion").addEventListener("click", () => {
        localStorage.removeItem('usuarioActivo');
        window.location.href = "/static/html/ServicioLogin.html";
    });

    document.getElementById("editarPerfil").addEventListener("click", () => {
        // Asegúrate de que este ID existe en el HTML de ServicioTecnico
        window.location.href = "/static/html/servicioEditT.html";
    });

    renderPeticiones();
});
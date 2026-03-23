// Controlador de Pestañas
window.openTab = function(evt, tabName) {
    const tabContents = document.querySelectorAll(".tab-content");
    tabContents.forEach(tab => tab.classList.remove("active"));
    
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => btn.classList.remove("active"));
    
    document.getElementById(tabName).classList.add("active");
    evt.currentTarget.classList.add("active");
};

document.addEventListener("DOMContentLoaded", async () => {
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (!currentUser || currentUser.role !== 'client') {
        window.location.href = "/static/html/ServicioLogin.html";
        return;
    }

    document.getElementById("userNameBar").textContent = currentUser.first_name || "Cliente";

    const servicesGrid = document.getElementById("servicesGrid");
    const listContainer = document.getElementById("requestList");

    // 1. CARGAR CATÁLOGO (Anti-CSS antiguo)
    async function loadCatalog() {
        try {
            const response = await fetch('/api/catalog');
            const catalog = await response.json();
            
            servicesGrid.style.display = "flex";
            servicesGrid.style.flexDirection = "column";
            servicesGrid.style.gap = "10px";
            servicesGrid.innerHTML = ""; 

            catalog.forEach(item => {
                const fila = document.createElement("div");
                // Contenedor principal: Fila horizontal estática y recta
                fila.style.cssText = "display: flex; flex-direction: row; border: 1px solid #ccc; border-radius: 4px; background: #fff; width: 100%; min-height: 55px; align-items: stretch;";
                
                fila.innerHTML = `
                    <div class="btn-desplegar" style="flex: 0 0 40%; display: flex; justify-content: space-between; align-items: center; padding: 0 15px; background: #f8f9fa; border-right: 1px solid #eee; cursor: pointer;">
                        <span class="nombre-servicio" style="font-weight: 600; color: #333; font-size: 14px; font-family: sans-serif;">${item.name}</span>
                        <span class="icono-mas" style="color: #888; font-weight: bold; font-size: 18px;">+</span>
                    </div>
                    <div class="formulario-horas" style="display: none; flex: 1; align-items: center; padding: 0 15px; gap: 15px; background: #fff;">
                        <label style="font-size: 13px; font-weight: bold; color: #555;">Horas:</label>
                        <input type="number" step="0.5" min="0" class="input-horas" style="width: 70px; padding: 6px; border: 1px solid #ccc; border-radius: 3px;">
                        
                        <label style="font-size: 13px; font-weight: bold; color: #555;">Comentario:</label>
                        <input type="text" class="input-comentario" placeholder="Opcional..." style="flex-grow: 1; padding: 6px; border: 1px solid #ccc; border-radius: 3px;">
                    </div>
                `;
                servicesGrid.appendChild(fila);
            });

            // Lógica de apertura hacia la derecha
            document.querySelectorAll(".btn-desplegar").forEach(btn => {
                btn.addEventListener("click", function() {
                    const form = this.nextElementSibling;
                    const icon = this.querySelector(".icono-mas");
                    
                    if (form.style.display === "none") {
                        form.style.display = "flex";
                        this.style.background = "#e9ecef";
                        icon.textContent = "-";
                    } else {
                        form.style.display = "none";
                        this.style.background = "#f8f9fa";
                        icon.textContent = "+";
                        form.querySelector(".input-horas").value = "";
                        form.querySelector(".input-comentario").value = "";
                    }
                });
            });
        } catch (error) {
            servicesGrid.innerHTML = "<p>Error crítico conectando con el servidor.</p>";
        }
    }

    // 2. CARGAR HISTORIAL DE OFERTAS
    async function loadMyRequests() {
        try {
            const response = await fetch(`/api/client/my-offers?email=${encodeURIComponent(currentUser.email)}`);
            const offers = await response.json();
            
            listContainer.style.display = "flex";
            listContainer.style.flexDirection = "column";
            listContainer.style.gap = "15px";
            listContainer.innerHTML = "";

            if (offers.length === 0) {
                listContainer.innerHTML = "<p>Aún no tienes ofertas generadas.</p>";
                return;
            }

            offers.sort((a, b) => b.id - a.id).forEach(offer => {
                const div = document.createElement("div");
                div.style.cssText = "border: 1px solid #ccc; padding: 20px; border-radius: 6px; background: #fff;";
                
                const date = new Date(offer.created_at).toLocaleDateString();
                let servicesText = offer.services.map(s => `<li style="margin-bottom: 5px;"><strong>${s.service_name}</strong>: ${s.hours}h ${s.comment ? `<br><small style="color:#666;">"${s.comment}"</small>` : ""}</li>`).join("");
                
                div.innerHTML = `
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px;">
                        <strong style="color: #004a8f; font-size: 1.1em;">OFERTA #${offer.id}</strong>
                        <span style="background-color: #17a2b8; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">${offer.status.toUpperCase()}</span>
                    </div>
                    <small style="color: #666;">Fecha: ${date}</small>
                    <ul style="margin-top: 10px; padding-left: 20px; color: #333;">${servicesText}</ul>
                `;
                listContainer.appendChild(div);
            });
        } catch (error) {
            console.error(error);
        }
    }

    // 3. ENVIAR OFERTA
    const btnSend = document.getElementById("btnSendRequest");
    if(btnSend) {
        btnSend.addEventListener("click", async () => {
            const filas = document.querySelectorAll(".formulario-horas");
            const requestedServices = [];

            filas.forEach(form => {
                if (form.style.display === "flex") {
                    const hours = parseFloat(form.querySelector(".input-horas").value);
                    const comment = form.querySelector(".input-comentario").value;
                    const serviceName = form.previousElementSibling.querySelector(".nombre-servicio").textContent.trim();

                    if (hours > 0) {
                        requestedServices.push({
                            service_name: serviceName,
                            hours: hours,
                            comment: comment
                        });
                    }
                }
            });

            if (requestedServices.length === 0) {
                alert("Debes desplegar al menos un servicio y ponerle horas para generar la oferta.");
                return;
            }

            const response = await fetch('/api/client/offers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    client_email: currentUser.email,
                    services: requestedServices
                })
            });

            if (response.ok) {
                alert("Oferta generada correctamente.");
                location.reload(); 
            } else {
                alert("Fallo de comunicación con el servidor.");
            }
        });
    }

    document.getElementById("logOut").addEventListener("click", () => {
        localStorage.removeItem('currentUser');
        window.location.href = "/static/html/ServicioLogin.html";
    });

    await loadCatalog();
    await loadMyRequests();
});
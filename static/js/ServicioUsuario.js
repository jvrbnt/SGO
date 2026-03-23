document.addEventListener("DOMContentLoaded", async () => {
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    const servicesGrid = document.getElementById("servicesGrid");
    const listContainer = document.getElementById("requestList");

    if (!currentUser || currentUser.role !== 'client') {
        window.location.href = "/static/html/ServicioLogin.html";
        return;
    }

    document.getElementById("userNameBar").textContent = currentUser.first_name || "User";

    // --- CARGA DE CATÁLOGO (SIN PRECIOS) ---
    async function loadCatalog() {
        try {
            const response = await fetch('/api/catalog');
            const catalog = await response.json();
            
            servicesGrid.innerHTML = ""; 
            servicesGrid.style.display = "flex";
            servicesGrid.style.flexDirection = "column";
            servicesGrid.style.gap = "8px";

            catalog.forEach(item => {
                const container = document.createElement("div");
                container.style.cssText = "display: flex; flex-direction: row; border: 1px solid #dee2e6; border-radius: 6px; overflow: hidden; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.05);";
                
                container.innerHTML = `
                    <button class="service-button" style="flex: 0 0 45%; text-align: left; padding: 15px; background: #f8f9fa; border: none; cursor: pointer; color: #333; text-shadow: none; display: flex; justify-content: space-between; align-items: center; border-right: 1px solid #dee2e6; transition: background 0.2s;">
                        <span style="font-weight: bold; text-shadow: none;">${item.name}</span>
                        <span style="color: #888; font-size: 18px;">+</span>
                    </button>
                    <div class="service-form" style="display: none; flex: 1; padding: 10px 15px; align-items: center; gap: 15px; background: #ffffff;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <label style="font-size: 14px; font-weight: bold; color: #555;">Horas:</label>
                            <input type="number" step="0.5" min="0" style="width: 70px; padding: 6px; border: 1px solid #ccc; border-radius: 4px; font-family: inherit;">
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px; flex-grow: 1;">
                            <label style="font-size: 14px; font-weight: bold; color: #555;">Comentario:</label>
                            <input type="text" placeholder="Instrucciones u observaciones..." style="width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px; font-family: inherit;">
                        </div>
                    </div>
                `;
                servicesGrid.appendChild(container);
            });

            document.querySelectorAll(".service-button").forEach(button => {
                button.addEventListener("click", function(e) {
                    e.preventDefault();
                    const form = this.nextElementSibling;
                    const icon = this.querySelector("span:last-child");
                    
                    if (form.style.display === "none") {
                        form.style.display = "flex";
                        this.style.background = "#e2e6ea"; 
                        icon.textContent = "-";
                    } else {
                        form.style.display = "none";
                        this.style.background = "#f8f9fa"; 
                        icon.textContent = "+";
                    }
                });
            });

        } catch (error) {
            servicesGrid.innerHTML = "<p>Error conectando con la base de datos de servicios.</p>";
        }
    }

    // --- CARGA DEL HISTORIAL ---
    async function loadMyRequests() {
        try {
            const response = await fetch(`/api/client/my-offers?email=${encodeURIComponent(currentUser.email)}`);
            const offers = await response.json();
            
            listContainer.innerHTML = "";
            if (offers.length === 0) {
                listContainer.innerHTML = "<p style='color: #666; font-style: italic;'>Aún no has generado ninguna solicitud.</p>";
                return;
            }

            offers.sort((a, b) => b.id - a.id).forEach(offer => {
                const div = document.createElement("div");
                div.className = "request-card";
                div.style.cssText = "border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; border-radius: 8px; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);";
                
                const date = new Date(offer.created_at).toLocaleDateString();
                let servicesText = offer.services.map(s => `<li style="margin-bottom: 5px;"><strong>${s.service_name}</strong>: ${s.hours}h ${s.comment ? `<br><small style="color:#666; font-style: italic;">"${s.comment}"</small>` : ""}</li>`).join("");
                
                let statusColor = offer.status === 'requested' ? '#17a2b8' : (offer.status === 'accepted' ? '#28a745' : '#6c757d');

                div.innerHTML = `
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px;">
                        <strong style="color: var(--color-csic); font-size: 1.1em;">SOLICITUD #${offer.id}</strong>
                        <span style="background-color: ${statusColor}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; text-transform: uppercase;">${offer.status}</span>
                    </div>
                    <small style="color: #888;">Fecha de creación: ${date}</small>
                    <ul style="margin-top: 10px; padding-left: 20px;">${servicesText}</ul>
                `;
                listContainer.appendChild(div);
            });
        } catch (error) {
            console.error("Error cargando historial:", error);
        }
    }

    // --- ENVÍO DE LA SOLICITUD ---
    const btnSend = document.getElementById("btnSendRequest");
    btnSend.addEventListener("click", async () => {
        const forms = document.querySelectorAll(".service-form");
        const requestedServices = [];

        forms.forEach(form => {
            if (form.style.display === "flex") {
                const hoursInput = form.querySelector("input[type='number']");
                const commentInput = form.querySelector("input[type='text']");
                const hours = parseFloat(hoursInput.value);
                // Extraemos el nombre limpiamente
                const serviceName = form.previousElementSibling.querySelector("span:first-child").textContent.trim();

                if (hours > 0) {
                    requestedServices.push({
                        service_name: serviceName,
                        hours: hours,
                        comment: commentInput.value
                    });
                }
            }
        });

        if (requestedServices.length === 0) {
            alert("Por favor, despliega un servicio e introduce las horas para enviar la solicitud.");
            return;
        }

        const payload = {
            client_email: currentUser.email,
            services: requestedServices
        };

        const response = await fetch('/api/client/offers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("¡Solicitud enviada correctamente!");
            location.reload(); 
        } else {
            alert("Error al enviar la solicitud.");
        }
    });

    // --- CERRAR SESIÓN ---
    document.getElementById("logOut").addEventListener("click", () => {
        localStorage.removeItem('currentUser');
        window.location.href = "/static/html/ServicioLogin.html";
    });

    await loadCatalog();
    await loadMyRequests();
});
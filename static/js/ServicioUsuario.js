document.addEventListener("DOMContentLoaded", async () => {
    const activeUser = JSON.parse(localStorage.getItem('activeUser'));
    const servicesGrid = document.getElementById("servicesGrid");
    const listContainer = document.getElementById("requestList");

    if (!activeUser) {
        window.location.href = "/static/html/ServicioLogin.html";
        return;
    }

    // Identificación de usuario en la barra superior
    document.getElementById("userNameBar").textContent = activeUser.firstName || "User";
    document.getElementById("userIcon").src = activeUser.profilePicture || "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";

    // 1. Cargar catálogo desde la base de datos
    async function loadCatalog() {
        try {
            const response = await fetch('/api/catalog');
            const catalog = await response.json();
            
            servicesGrid.innerHTML = ""; // Limpiar el "Loading..."

            catalog.forEach(item => {
                const container = document.createElement("div");
                container.className = "service-container";
                
                // Si es Micro-welding, aplicamos el ID para el centrado CSS que ya tienes
                if(item.name.toLowerCase().includes("welding")) {
                    container.id = "service-micro-welding";
                }

                container.innerHTML = `
                    <button class="service-button">${item.name}</button>
                    <div class="service-form">
                        <div class="input-group">
                            <label>Hours:</label>
                            <input type="number" step="0.5" min="0">
                        </div>
                        <div class="input-group">
                            <label>Comment:</label>
                            <input type="text" placeholder="Optional details...">
                        </div>
                    </div>
                `;
                servicesGrid.appendChild(container);
            });

            // Re-vincular eventos a los nuevos botones dinámicos
            document.querySelectorAll(".service-button").forEach(button => {
                button.addEventListener("click", function(e) {
                    e.stopPropagation();
                    this.nextElementSibling.classList.toggle("open");
                });
            });

        } catch (error) {
            console.error("Error loading catalog:", error);
            servicesGrid.innerHTML = "<p>Error loading catalog. Is the server running?</p>";
        }
    }

    // 2. Cargar historial de solicitudes del cliente desde PostgreSQL
    async function loadMyRequests() {
        try {
            const response = await fetch('/api/client/my-offers');
            const offers = await response.json();
            
            listContainer.innerHTML = "";
            offers.forEach(offer => {
                const div = document.createElement("div");
                div.className = "request-card";
                const date = new Date(offer.created_at).toLocaleDateString();
                
                let servicesText = offer.services.map(s => `${s.service_name} (${s.hours}h)`).join(", ");
                
                div.innerHTML = `
                    <strong style="color: var(--color-csic);">OFFER #${offer.id} - ${offer.status}</strong><br>
                    <small>${date}</small>
                    <p style="font-size:12px; margin-top:5px; color:#555;">${servicesText}</p>
                `;
                listContainer.appendChild(div);
            });
        } catch (error) {
            console.error("Error loading requests:", error);
        }
    }

    // 3. Enviar nueva solicitud a PostgreSQL
    const btnSend = document.getElementById("btnSendRequest");
    btnSend.addEventListener("click", async () => {
        const forms = document.querySelectorAll(".service-form");
        const requestedServices = [];

        forms.forEach(form => {
            const hoursInput = form.querySelector("input[type='number']");
            const commentInput = form.querySelector("input[type='text']");
            const hours = parseFloat(hoursInput.value);
            const serviceName = form.previousElementSibling.textContent;

            if (hours > 0) {
                requestedServices.push({
                    service_name: serviceName,
                    hours: hours,
                    comment: commentInput.value
                });
            }
        });

        if (requestedServices.length === 0) {
            alert("Please select at least one service.");
            return;
        }

        const response = await fetch('/api/client/offers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ services: requestedServices })
        });

        if (response.ok) {
            alert("Request sent and stored in Database!");
            location.reload();
        }
    });

    // Navegación y Logout
    document.getElementById("logOut").addEventListener("click", () => {
        localStorage.removeItem('activeUser');
        window.location.href = "/static/html/ServicioLogin.html";
    });

    document.getElementById("editProfile")?.addEventListener("click", () => {
        window.location.href = "/static/html/ServicioEdit.html";
    });

    // Ejecución inicial
    await loadCatalog();
    await loadMyRequests();
});
document.addEventListener("DOMContentLoaded", () => {
    const techData = JSON.parse(localStorage.getItem("currentUser"));
    
    // Seguridad: Si no está logueado o no es técnico, lo echamos al Login
    if (!techData || techData.role !== "technician") {
        window.location.href = "/static/html/ServicioLogin.html";
        return;
    }

    // Rellenamos su nombre en la barra superior
    const techNameEl = document.getElementById("techName");
    if (techNameEl) {
        techNameEl.textContent = `${techData.first_name} ${techData.last_name}`;
    }

    // EL BOTÓN DE EXIT STAFF (Ya funcional)
    const logOutBtn = document.getElementById("logOut");
    if (logOutBtn) {
        logOutBtn.addEventListener("click", () => {
            localStorage.removeItem("currentUser");
            window.location.href = "/static/html/ServicioLogin.html";
        });
    }

    // Cargar las ofertas desde la base de datos
    loadAllOffers();
});

const globalList = document.getElementById("globalRequestList");

async function loadAllOffers() {
    try {
        const response = await fetch("/api/technician/offers");
        if (!response.ok) throw new Error("Failed to fetch offers");

        const offers = await response.json();
        renderOffers(offers);
    } catch (error) {
        console.error("Error loading technical portal data:", error);
        if (globalList) {
            globalList.innerHTML = `<p style="color: red; text-align: center;">Error conectando con la base de datos.</p>`;
        }
    }
}

function renderOffers(offers) {
    if (!globalList) return;
    globalList.innerHTML = ""; 

    if (offers.length === 0) {
        globalList.innerHTML = "<p style='text-align:center;'>No hay solicitudes pendientes en el sistema.</p>";
        return;
    }

    offers.forEach((offer) => {
        const card = document.createElement("div");
        card.className = "request-card";
        card.style.cssText = "border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; border-radius: 8px; background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.1);";

        const servicesList = offer.services.map((s) => 
            `<li><strong>${s.service_name}</strong>: ${s.hours}h ${s.comment ? `(<em>${s.comment}</em>)` : ""}</li>`
        ).join("");

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="font-weight:bold; color:var(--color-csic); font-size: 1.1em;">OFERTA #${offer.id}</span>
                <span style="background:#eee; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold;">ESTADO: ${offer.status.toUpperCase()}</span>
            </div>
            <p style="margin: 5px 0;"><strong>ID Cliente:</strong> ${offer.client_id}</p>
            <p style="margin: 5px 0;"><strong>Fecha:</strong> ${new Date(offer.created_at).toLocaleDateString()}</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">
            <ul style="margin: 10px 0; padding-left: 20px; color: #555;">
                ${servicesList}
            </ul>
            <div style="margin-top: 15px;">
                <button onclick="updateOfferStatus(${offer.id}, 'accepted')" style="background-color: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; margin-right: 10px; font-weight: bold;">Aceptar Oferta</button>
                <button onclick="updateOfferStatus(${offer.id}, 'technical_offer')" style="background-color: #17a2b8; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-weight: bold;">Mover a Revisión</button>
            </div>
        `;
        globalList.appendChild(card);
    });
}

async function updateOfferStatus(offerId, newStatus) {
    try {
        const response = await fetch(`/api/technician/offers/${offerId}?new_status=${newStatus}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
        });

        if (response.ok) {
            loadAllOffers(); // Recarga la lista para ver el nuevo estado
        } else {
            const error = await response.json();
            alert("Error al actualizar: " + (error.detail || "Error desconocido"));
        }
    } catch (err) {
        console.error("Network error updating status:", err);
    }
}
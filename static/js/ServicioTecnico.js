// Referencias a elementos del DOM
const globalList = document.getElementById("globalRequestList");

/**
 * Carga todas las ofertas desde la base de datos y las renderiza en el panel.
 */
async function loadAllOffers() {
  try {
    const response = await fetch("/api/technician/offers");
    if (!response.ok) throw new Error("Failed to fetch offers");

    const offers = await response.json();
    renderOffers(offers);
  } catch (error) {
    console.error("Error loading technical portal data:", error);
    globalList.innerHTML = `<p style="color: red;">Error connecting to database.</p>`;
  }
}

/**
 * Genera el HTML para cada tarjeta de oferta.
 * @param {Array} offers - Lista de objetos de oferta procedentes del backend.
 */
function renderOffers(offers) {
  globalList.innerHTML = ""; // Limpiar contenedor

  if (offers.length === 0) {
    globalList.innerHTML = "<p>No pending requests in the system.</p>";
    return;
  }

  offers.forEach((offer) => {
    const card = document.createElement("div");
    card.className = "request-card";

    // Construcción de la lista de servicios desglosados
    const servicesList = offer.services
      .map(
        (s) => `
            <li>
                <strong>${s.service_name}</strong>: ${s.hours}h 
                <span class="service-status-tag">${s.status}</span>
                ${s.comment ? `<br><small><i>"${s.comment}"</i></small>` : ""}
            </li>
        `,
      )
      .join("");

    card.innerHTML = `
            <div class="request-header">
                <span class="status-badge status-${offer.status.toLowerCase()}">${offer.status.toUpperCase()}</span>
                <span class="request-date">${new Date(offer.created_at).toLocaleDateString()}</span>
            </div>
            <div class="request-body">
                <h3>Offer #${offer.id}</h3>
                <p><strong>Client ID:</strong> ${offer.client_id}</p>
                <ul class="services-summary">
                    ${servicesList}
                </ul>
            </div>
            <div class="request-actions">
                <button class="btn-action btn-accept" onclick="updateOfferStatus(${offer.id}, 'accepted')">Accept Offer</button>
                <button class="btn-action btn-manage" onclick="updateOfferStatus(${offer.id}, 'technical_offer')">Move to Review</button>
            </div>
        `;
    globalList.appendChild(card);
  });
}

/**
 * Actualiza el estado de una oferta en el servidor.
 * @param {number} offerId - ID único de la oferta.
 * @param {string} newStatus - Nuevo estado (accepted, technical_offer, finished, etc).
 */
async function updateOfferStatus(offerId, newStatus) {
  try {
    const response = await fetch(
      `/api/technician/offers/${offerId}?new_status=${newStatus}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
      },
    );

    if (response.ok) {
      loadAllOffers();
    } else {
      const error = await response.json();
      alert("Update failed: " + (error.detail || "Unknown error"));
    }
  } catch (err) {
    console.error("Network error updating status:", err);
  }
}

// Inicialización al cargar el documento
document.addEventListener("DOMContentLoaded", () => {
  const techData = JSON.parse(localStorage.getItem("currentUser"));
  if (techData && techData.role === "technician") {
    document.getElementById("techName").textContent =
      `${techData.first_name} ${techData.last_name}`;
    if (techData.profile_picture) {
      document.getElementById("techProfilePic").src = techData.profile_picture;
    }
  }

  loadAllOffers();
});
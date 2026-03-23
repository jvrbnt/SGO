// Función global para cambiar de pestaña
window.openTab = function (evt, tabName) {
  const tabContents = document.getElementsByClassName("tab-content");
  for (let i = 0; i < tabContents.length; i++) {
    tabContents[i].classList.remove("active");
  }
  const tabBtns = document.getElementsByClassName("tab-btn");
  for (let i = 0; i < tabBtns.length; i++) {
    tabBtns[i].classList.remove("active");
  }
  document.getElementById(tabName).classList.add("active");
  evt.currentTarget.classList.add("active");
};

document.addEventListener("DOMContentLoaded", () => {
  const techData = JSON.parse(localStorage.getItem("currentUser"));

  if (!techData || techData.role !== "technician") {
    window.location.href = "/static/html/ServicioLogin.html";
    return;
  }

  const techNameEl = document.getElementById("techName");
  if (techNameEl) {
    techNameEl.textContent = `${techData.first_name} ${techData.last_name}`;
  }

  const logOutBtn = document.getElementById("logOut");
  if (logOutBtn) {
    logOutBtn.addEventListener("click", () => {
      localStorage.removeItem("currentUser");
      window.location.href = "/static/html/ServicioLogin.html";
    });
  }

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

  // Forzamos a que sea una lista vertical de ancho completo (adiós Grid)
  globalList.style.display = "flex";
  globalList.style.flexDirection = "column";
  globalList.style.gap = "15px";
  globalList.style.width = "100%";
  globalList.innerHTML = "";

  if (offers.length === 0) {
    globalList.innerHTML =
      "<p style='text-align:center; padding: 20px; color: #666;'>No hay ofertas pendientes en el sistema.</p>";
    return;
  }

  // Ordenar de más nuevas a más antiguas
  offers
    .sort((a, b) => b.id - a.id)
    .forEach((offer) => {
      const card = document.createElement("div");
      card.style.cssText =
        "border: 1px solid #ccc; padding: 20px; border-radius: 8px; background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 100%; box-sizing: border-box;";

      const servicesList = offer.services
        .map(
          (s) =>
            `<li style="margin-bottom: 5px;"><strong>${s.service_name}</strong>: ${s.hours}h ${s.comment ? `<br><span style="color: #666; font-style: italic;">Obs: ${s.comment}</span>` : ""}</li>`,
        )
        .join("");

      let statusColor =
        offer.status === "requested"
          ? "#17a2b8"
          : offer.status === "accepted"
            ? "#28a745"
            : "#6c757d";

      card.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                <span style="font-weight:bold; color:var(--color-csic); font-size: 1.2em;">OFERTA #${offer.id}</span>
                <span style="background-color:${statusColor}; color: white; padding:5px 15px; border-radius:12px; font-size:12px; font-weight:bold; text-transform: uppercase;">${offer.status}</span>
            </div>
            <div style="display: flex; gap: 40px; margin-bottom: 15px;">
                <p style="margin: 0;"><strong>ID Cliente:</strong> ${offer.client_id}</p>
                <p style="margin: 0;"><strong>Fecha:</strong> ${new Date(offer.created_at).toLocaleDateString()}</p>
            </div>
            <ul style="margin: 10px 0 20px 0; padding-left: 20px; color: #333;">
                ${servicesList}
            </ul>
            <div style="display: flex; gap: 15px;">
                <button onclick="updateOfferStatus(${offer.id}, 'accepted')" style="background-color: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold;">Aceptar Oferta</button>
                <button onclick="updateOfferStatus(${offer.id}, 'technical_offer')" style="background-color: #17a2b8; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold;">Mover a Revisión</button>
            </div>
        `;
      globalList.appendChild(card);
    });
}

window.updateOfferStatus = async function (offerId, newStatus) {
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
      alert("Error al actualizar: " + (error.detail || "Error desconocido"));
    }
  } catch (err) {
    console.error("Network error updating status:", err);
  }
};

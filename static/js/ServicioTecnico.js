// --- 1. NAVEGACIÓN Y PESTAÑAS ---
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

// --- 2. INICIALIZACIÓN ---
document.addEventListener("DOMContentLoaded", () => {
  const techData = JSON.parse(localStorage.getItem("currentUser"));

  if (!techData || techData.role !== "technician") {
    window.location.href = "/static/html/ServicioLogin.html";
    return;
  }

  // Cargar Nombre y Foto si existen
  const userNameBar = document.getElementById("userNameBar");
  if (userNameBar) {
    userNameBar.textContent = techData.nickname || `${techData.first_name} ${techData.last_name}`;
  }

  if (techData.profilePicture) {
    const userIcon = document.getElementById("userIcon");
    if (userIcon) userIcon.src = techData.profilePicture;
  }

  // Lógica del Menú Desplegable
  const profileContainer = document.getElementById("profileContainer");
  const dropdownMenu = document.getElementById("dropdownMenu");

  if (profileContainer && dropdownMenu) {
    profileContainer.addEventListener("click", (e) => {
      e.stopPropagation();
      dropdownMenu.classList.toggle("hidden");
    });

    document.addEventListener("click", () => {
      dropdownMenu.classList.add("hidden");
    });
  }

  // Acción Editar Perfil
  const editProfileBtn = document.getElementById("editProfile");
  if (editProfileBtn) {
    editProfileBtn.addEventListener("click", () => {
      window.location.href = "/static/html/ServicioEditT.html";
    });
  }

  // Acción Cerrar Sesión
  const logOutBtn = document.getElementById("logOut");
  if (logOutBtn) {
    logOutBtn.addEventListener("click", () => {
      localStorage.removeItem("currentUser");
      window.location.href = "/static/html/ServicioLogin.html";
    });
  }

  window.loadAllOffers();
});

const globalList = document.getElementById("globalRequestList");

// --- 3. COMUNICACIÓN CON API ---

window.loadAllOffers = async function () {
  try {
    const response = await fetch("/api/technician/offers");
    if (!response.ok) throw new Error("Failed to fetch offers");

    const offers = await response.json();
    window.allOffers = offers;
    renderAll();
  } catch (error) {
    console.error("Error loading technician offers:", error);
    const globalList = document.getElementById("globalRequestList");
    if (globalList) {
      globalList.innerHTML = `<p style="color: red; text-align: center;">Error conectando con la base de datos.</p>`;
    }
  }
};

window.assignOffer = async function (offerId) {
  const techData = JSON.parse(localStorage.getItem("currentUser"));
  if (!techData || !techData.id) {
    alert("Error: Technician ID not found. Return to login.");
    return;
  }
  
  try {
    const response = await fetch(`/api/technician/offers/${offerId}/assign?tech_id=${techData.id}`, {
      method: "PATCH"
    });
    if (response.ok) {
      window.loadAllOffers();
      // Jump to "Mis Ofertas" tab automatically
      const myOffersBtn = document.querySelector(".tab-btn[onclick*='tabMisOfertas']");
      if(myOffersBtn) myOffersBtn.click();
    } else {
      const error = await response.json();
      alert("Error: " + (error.detail || "Error al asignar oferta"));
    }
  } catch (err) {
    console.error("Network error:", err);
  }
};

window.assignService = async function (serviceId) {
  const techData = JSON.parse(localStorage.getItem("currentUser"));
  if (!techData || !techData.id) {
    alert("Error: Technician ID not found. Return to login.");
    return;
  }
  
  try {
    const response = await fetch(`/api/technician/services/${serviceId}/assign?tech_id=${techData.id}`, {
      method: "PATCH"
    });
    if (response.ok) {
      window.loadAllOffers();
      const myOffersBtn = document.querySelector(".tab-btn[onclick*='tabMisOfertas']");
      if(myOffersBtn) myOffersBtn.click();
    } else {
      const error = await response.json();
      alert("Error: " + (error.detail || "Error al asignar servicio"));
    }
  } catch (err) {
    console.error("Network error:", err);
  }
};

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
      window.loadAllOffers();
    } else {
      const error = await response.json();
      alert("Error: " + (error.detail || "Error desconocido"));
    }
  } catch (err) {
    console.error("Network error:", err);
  }
};

// --- 4. MODO REVISIÓN (FLUJO VÍCTOR) ---

window.openReviewPanel = async function (offerId, isMineTab) {
  try {
    const response = await fetch(`/api/technician/offers/${offerId}`);
    if (!response.ok) throw new Error("No se pudo obtener la oferta");
    const offer = await response.json();

    const client = offer.client || {};
    
    const targetContainer = isMineTab ? document.getElementById("myOffersList") : document.getElementById("globalRequestList");

    targetContainer.innerHTML = `
        <div style="background: #fff; padding: 25px; border: 2px solid #3498db; border-radius: 8px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:20px; align-items:center;">
                <h2 style="margin:0; color:#3498db;">REVIEW MODE: OFFER #${offer.id}</h2>
                <button onclick="window.loadAllOffers()" style="background:#666; color:white; border:none; padding:8px 15px; cursor:pointer; border-radius:4px; font-weight:bold;">← BACK TO LIST</button>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; background:#f9f9f9; padding:15px; border-radius:6px; margin-bottom:20px; font-size:14px;">
                <div>
                    <h4 style="margin:0 0 10px 0; color:var(--color-csic);">CUSTOMER DETAILS</h4>
                    <p><strong>Name:</strong> ${client.first_name} ${client.last_name}</p>
                    <p><strong>Email:</strong> ${client.email}</p>
                    <p><strong>Entity:</strong> ${client.entity || "N/A"}</p>
                    <p><strong>Group:</strong> ${client.group_name || "N/A"}</p>
                </div>
                <div>
                    <h4 style="margin:0 0 10px 0; color:var(--color-csic);">INTERNAL DATA</h4>
                    <p><strong>IP Address:</strong> ${client.ip_address || "External"}</p>
                    <p><strong>CI (Project ID):</strong> ${client.project_id || "N/A"}</p>
                    <p><strong>CP (Account):</strong> ${client.internal_account || "N/A"}</p>
                    <hr style="border:0; border-top:1px solid #ddd; margin:10px 0;">
                    <p><strong>Offer Created:</strong> ${new Date(offer.created_at).toLocaleString()}</p>
                </div>
            </div>

            <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                <thead>
                    <tr style="text-align:left; border-bottom:2px solid #eee; color:#666; font-size:13px;">
                        <th style="padding:10px;">SERVICE</th>
                        <th style="padding:10px;">HOURS</th>
                        <th style="padding:10px;">INTERNAL NOTES</th>
                    </tr>
                </thead>
                <tbody>
                    ${offer.services
                      .map(
                        (s) => `
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px;"><strong>${s.service_name}</strong></td>
                            <td><input type="number" class="rev-hours" data-id="${s.id}" value="${s.hours}" style="width:60px; padding:5px; border:1px solid #ccc; border-radius:4px;"></td>
                            <td><input type="text" class="rev-notes" data-id="${s.id}" value="${s.comment || ""}" placeholder="Notes for this service..." style="width:95%; padding:5px; border:1px solid #ccc; border-radius:4px;"></td>
                        </tr>
                    `,
                      )
                      .join("")}
                </tbody>
            </table>

            <h4 style="color:#888; margin-bottom:10px;">MESSAGE FOR CLIENT (GLOBAL COMMENT)</h4>
            <textarea id="globalComment" style="width:100%; height:80px; padding:10px; border:1px solid #ccc; border-radius:4px; font-family:inherit;" placeholder="Explain the quotation to the researcher...">${offer.technician_comment || ""}</textarea>

            <button onclick="window.sendQuotedOffer(${offer.id})" style="width:100%; margin-top:20px; background:#27ae60; color:white; border:none; padding:15px; font-weight:bold; border-radius:4px; cursor:pointer; font-size:16px;">
                SEND QUOTED OFFER TO CLIENT
            </button>
        </div>
    `;
  } catch (err) {
    console.error("Error opening review panel:", err);
  }
};

window.sendQuotedOffer = async function (offerId) {
  const hours = document.querySelectorAll(".rev-hours");
  const notes = document.querySelectorAll(".rev-notes");
  const comment = document.getElementById("globalComment").value;

  const servicesData = Array.from(hours).map((h, idx) => ({
    id: h.dataset.id,
    hours: parseFloat(h.value),
    comment: notes[idx].value,
  }));

  try {
    const response = await fetch(`/api/technician/offers/${offerId}/review`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        services: servicesData,
        technician_comment: comment,
        status: "quoted", 
      }),
    });

    if (response.ok) {
      alert("Offer updated and sent to client. Status: QUOTED");
      window.loadAllOffers();
    } else {
      alert("Error sending offer.");
    }
  } catch (err) {
    console.error("Error saving review:", err);
  }
};

// --- 5. RENDERIZADO DE LA LISTA DE OFERTAS ---
function renderAll() {
  const techData = JSON.parse(localStorage.getItem("currentUser"));
  const techId = techData ? techData.id : null;
  
  const globalOffers = window.allOffers;
  const myOffers = window.allOffers.filter(o => 
    o.manager_id === techId || o.services.some(s => s.technician_id === techId)
  );
  
  renderOfferList(globalOffers, document.getElementById("globalRequestList"), true, techId);
  renderOfferList(myOffers, document.getElementById("myOffersList"), false, techId);
}

function renderOfferList(offers, container, isGlobal, techId) {
  if (!container) return;
  container.innerHTML = "";
  container.style.display = "flex";
  container.style.flexDirection = "column";
  container.style.gap = "15px";

  if (offers.length === 0) {
    container.innerHTML =
      "<p style='text-align:center; padding: 20px; color: #666;'>No hay solicitudes en esta sección.</p>";
    return;
  }

  offers
    .sort((a, b) => b.id - a.id)
    .forEach((offer) => {
      const card = document.createElement("div");
      card.style.cssText =
        "border: 1px solid #ccc; padding: 20px; border-radius: 8px; background: #fff; width: 100%; box-sizing: border-box;";

      const statusColor =
        {
          requested: "#17a2b8",
          quoted: "#f39c12", 
          accepted: "#27ae60",
          finished: "#2c3e50",
        }[offer.status] || "#6c757d";

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
            <span style="font-weight:bold; color:var(--color-csic); font-size: 1.2em;">OFFER #${offer.id}</span>
            <span style="background-color:${statusColor}; color: white; padding:5px 15px; border-radius:12px; font-size:12px; font-weight:bold;">
                ${offer.status}
            </span>
        </div>
        <div style="display: flex; gap: 40px; margin-bottom: 15px; font-size: 14px; color: #555;">
            <p style="margin: 0;"><strong>CLIENT ID:</strong> ${offer.client_id}</p>
            <p style="margin: 0;"><strong>DATE:</strong> ${new Date(offer.created_at).toLocaleDateString()}</p>
        </div>
        
        <details style="margin: 10px 0 20px 0; padding: 10px; background: #f9f9f9; border: 1px solid #ddd; border-radius: 6px;">
            <summary style="cursor: pointer; font-weight: bold; color: #2c3e50;">Ver Servicios (${offer.services.length})</summary>
            <div style="margin-top: 10px; display: flex; flex-direction: column; gap: 8px;">
            ${offer.services.map((s) => `
                <div style="display: flex; justify-content: space-between; align-items: center; background: white; padding: 8px 12px; border: 1px solid #eee; border-radius: 4px;">
                    <div style="font-size:14px; color:#333;">
                        <strong>${s.service_name}</strong> (${s.hours}h)
                    </div>
                    <div>
                        ${
                          !s.technician_id
                            ? `<button onclick="window.assignService(${s.id})" style="background:#8e44ad; color:white; border:none; padding:4px 10px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold;">Asignarme</button>`
                            : s.technician_id !== techId
                            ? `<span style="background:#e74c3c; color:white; padding:4px 10px; border-radius:4px; font-weight:bold; font-size:11px;">Técnico #${s.technician_id}</span>`
                            : `<span style="background:#27ae60; color:white; padding:4px 10px; border-radius:4px; font-weight:bold; font-size:11px;">Mío</span>`
                        }
                    </div>
                </div>
            `).join("")}
            </div>
        </details>
        
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 15px;">
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            ${
              isGlobal && !offer.manager_id
                ? `<button onclick="window.assignOffer(${offer.id})" style="background:#8e44ad; color:white; border:none; padding:8px 15px; border-radius:4px; cursor:pointer; font-weight:bold;">Manager de Oferta</button>`
                : ""
            }
            ${
              (!isGlobal || (isGlobal && offer.manager_id === techId)) && (offer.status === "requested" || offer.status === "quoted")
                ? `<button onclick="window.openReviewPanel(${offer.id}, ${!isGlobal})" style="background:#3498db; color:white; border:none; padding:8px 15px; border-radius:4px; cursor:pointer; font-weight:bold;">Review</button>`
                : ""
            }
            ${
              (!isGlobal || (isGlobal && offer.manager_id === techId)) && offer.status === "accepted"
                ? `<button onclick="window.updateOfferStatus(${offer.id}, 'finished')" style="background:#2c3e50; color:white; border:none; padding:8px 15px; border-radius:4px; cursor:pointer; font-weight:bold;">Finish Work</button>`
                : ""
            }
          </div>
          <div style="text-align: right;">
            ${
              isGlobal && offer.manager_id && offer.manager_id !== techId
                ? `<span style="color:#e74c3c; font-weight:bold; font-size:12px;">Manager: Técnico #${offer.manager_id}</span>`
                : isGlobal && offer.manager_id === techId
                ? `<span style="color:#27ae60; font-weight:bold; font-size:12px;">Manager: Yo</span>`
                : ""
            }
          </div>
        </div>
    `;
      container.appendChild(card);
    });
}
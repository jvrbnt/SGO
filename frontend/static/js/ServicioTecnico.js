// --- 1. NAVIGATION AND TABS ---
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

// --- 2. INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  const techData = JSON.parse(localStorage.getItem("currentUser"));

  if (!techData || techData.role !== "technician") {
    window.location.href = "/login";
    return;
  }

  // Load Name and Photo if they exist
  const userNameBar = document.getElementById("userNameBar");
  if (userNameBar) {
    userNameBar.textContent = techData.nickname || `${techData.first_name} ${techData.last_name}`;
  }

  if (techData.profilePicture) {
    const userIcon = document.getElementById("userIcon");
    if (userIcon) userIcon.src = techData.profilePicture;
  }

  // Dropdown Menu Logic
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

  // Edit Profile Action
  const editProfileBtn = document.getElementById("editProfile");
  if (editProfileBtn) {
    editProfileBtn.addEventListener("click", () => {
      window.location.href = "/editar-tecnico";
    });
  }

  // Logout Action
  const logOutBtn = document.getElementById("logOut");
  if (logOutBtn) {
    logOutBtn.addEventListener("click", () => {
      localStorage.removeItem("currentUser");
      window.location.href = "/login";
    });
  }

  window.loadAllOffers();
});

const globalList = document.getElementById("globalRequestList");

// --- 3. API COMMUNICATION ---

window.loadAllOffers = async function () {
  // Save which offer details are currently open before re-render
  const openOfferIds = new Set(
    [...document.querySelectorAll('details[data-offer-id][open]')]
      .map(el => el.dataset.offerId)
  );

  try {
    const response = await fetch("/api/technician/offers");
    if (!response.ok) throw new Error("Failed to fetch offers");

    const offers = await response.json();
    window.allOffers = offers;
    renderAll();

    // Reopen any details that were open before
    if (openOfferIds.size > 0) {
      document.querySelectorAll('details[data-offer-id]').forEach(el => {
        if (openOfferIds.has(el.dataset.offerId)) el.open = true;
      });
    }
  } catch (error) {
    console.error("Error loading technician offers:", error);
    const globalList = document.getElementById("globalRequestList");
    if (globalList) {
      globalList.innerHTML = `<p style="color: red; text-align: center;">Error connecting to the database.</p>`;
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
    } else {
      const error = await response.json();
      alert("Error: " + (error.detail || "Error assigning offer"));
    }
  } catch (err) {
    console.error("Network error:", err);
  }
};

window.unassignOffer = async function (offerId) {
  const techData = JSON.parse(localStorage.getItem("currentUser"));
  if (!techData || !techData.id) {
    alert("Error: Technician ID not found. Return to login.");
    return;
  }

  try {
    const response = await fetch(`/api/technician/offers/${offerId}/unassign?tech_id=${techData.id}`, {
      method: "PATCH"
    });
    if (response.ok) {
      window.loadAllOffers();
    } else {
      const error = await response.json();
      alert("Error: " + (error.detail || "Error unassigning offer"));
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
    } else {
      const error = await response.json();
      alert("Error: " + (error.detail || "Error assigning service"));
    }
  } catch (err) {
    console.error("Network error:", err);
  }
};

window.unassignService = async function (serviceId) {
  const techData = JSON.parse(localStorage.getItem("currentUser"));
  if (!techData || !techData.id) {
    alert("Error: Technician ID not found. Return to login.");
    return;
  }

  try {
    const response = await fetch(`/api/technician/services/${serviceId}/unassign?tech_id=${techData.id}`, {
      method: "PATCH"
    });
    if (response.ok) {
      window.loadAllOffers();
    } else {
      const error = await response.json();
      alert("Error: " + (error.detail || "Error unassigning service"));
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
      alert("Error: " + (error.detail || "Unknown error"));
    }
  } catch (err) {
    console.error("Network error:", err);
  }
};

// --- 4. REVIEW MODE (TECHNICIAN WORKFLOW) ---

// Map entity → price field
function getPriceField(entity) {
  if (!entity) return 'price1';
  const e = entity.toLowerCase();
  if (e === 'internal') return 'price1';
  if (e === 'csic' || e === 'uam') return 'price2';
  if (e === 'opis' || e === 'university') return 'price3';
  if (e === 'company') return 'price4';
  return 'price1'; // fallback
}

window.openReviewPanel = async function (offerId, isMineTab, readOnly = false) {
  try {
    const response = await fetch(`/api/technician/offers/${offerId}`);
    if (!response.ok) throw new Error("Could not retrieve offer details");
    const offer = await response.json();

    // Filter catalog for "Add Service" dropdown: exclude services already in offer
    const currentServiceNames = offer.services.map(s => s.service_name);
    const catalogRes = await fetch("/api/catalog");
    let catalogItems = catalogRes.ok ? await catalogRes.json() : [];
    catalogItems = catalogItems.filter(item => !currentServiceNames.includes(item.name));

    const client = offer.client || {};
    const isInternal = (client.entity || '').toLowerCase() === 'internal';
    const priceField = getPriceField(client.entity);
    const inputAttr = readOnly ? 'disabled style="background:#f3f4f6; color:#888; cursor:not-allowed;"' : '';
    const textareaAttr = readOnly ? 'disabled style="background:#f3f4f6; color:#888; cursor:not-allowed; resize:none;"' : '';

    const targetContainer = isMineTab ? document.getElementById("myOffersList") : document.getElementById("globalRequestList");

    // Build service rows (only active ones)
    const activeServices = offer.services.filter(s => !s.is_deleted);
    const serviceRows = activeServices.map((s) => {
      const catalogPrices = s.catalog_item || {};
      const pricePerHour = catalogPrices[priceField] ?? 0;
      const totalPrice = (pricePerHour * (s.hours || 0)).toFixed(2);
      return `
        <tr style="border-bottom:1px solid #eee;" id="rev-row-${s.id}">
          <td style="padding:10px;"><strong>${s.service_name}</strong></td>
          <td style="padding:10px; white-space:nowrap; color:#555;">
            <span class="rev-price-ph" style="display:inline-block; background:#f0f4ff; border:1px solid #c8d8ff; border-radius:4px; padding:5px 10px; font-weight:600; color:#2563eb; font-size:13px; min-width:70px; text-align:center;">${pricePerHour.toFixed(2)} €/h</span>
          </td>
          <td style="padding:10px;">
            <input type="number" class="rev-hours" data-id="${s.id}" data-pph="${pricePerHour}" value="${s.hours}" step="0.5" min="0"
              style="width:65px; padding:5px; border:1px solid #ccc; border-radius:4px;"
              ${readOnly ? 'disabled style="width:65px;padding:5px;border:1px solid #ccc;border-radius:4px;background:#f3f4f6;color:#888;cursor:not-allowed;"' : `oninput="window.updateRowPrice('${s.id}', this.value, ${pricePerHour})"`}>
          </td>
          <td style="padding:10px;">
            <input type="number" class="rev-total-price" data-id="${s.id}" value="${s.quoted_price ?? totalPrice}" step="0.01" min="0"
              ${readOnly ? 'disabled style="width:90px;padding:5px;border:1px solid #c8d8ff;border-radius:4px;background:#f3f4f6;font-weight:600;color:#888;cursor:not-allowed;"' : 'style="width:90px; padding:5px; border:1px solid #c8d8ff; border-radius:4px; background:#f0f4ff; font-weight:600; color:#2563eb;"'}>
          </td>
          <td style="padding:10px; display:flex; align-items:center; gap:5px;">
            ${s.added_by_technician ? '' : `
              <input type="text" class="rev-notes" data-id="${s.id}" value="${s.comment || ''}" placeholder="Internal notes..."
                ${readOnly ? 'disabled style="width:95%;padding:5px;border:1px solid #ccc;border-radius:4px;background:#f3f4f6;color:#888;cursor:not-allowed;"' : 'style="width:95%; padding:5px; border:1px solid #ccc; border-radius:4px;"'}>
              <button class="btn-view-comment" title="View full note" onclick="window.showFullNote(this.previousElementSibling.value)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
              </button>
            `}
          </td>
          <td style="padding:10px; text-align:right;">
             ${!readOnly ? `
                <button onclick="window.deleteServiceFromOffer(${s.id}, ${offer.id}, ${isMineTab}, '${s.service_name.replace(/'/g, "\\'")}')" 
                        style="background:none; border:none; cursor:pointer; padding:5px; color:#ef4444;" title="Delete service">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trash-2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                </button>
             ` : ''}
          </td>
        </tr>
      `;
    }).join('');

    targetContainer.innerHTML = `
      <div style="background:#fff; padding:25px; border:2px solid #3498db; border-radius:8px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:20px; align-items:center;">
          <h2 style="margin:0; color:#3498db;">REVIEW MODE: OFFER #${offer.id}</h2>
          <button onclick="window.loadAllOffers()" class="btn-card btn-back">← BACK TO LIST</button>
        </div>

        <div style="display:grid; grid-template-columns:${isInternal ? '1fr 1fr' : '1fr'}; gap:20px; background:#f9f9f9; padding:15px; border-radius:6px; margin-bottom:20px; font-size:14px;">
          <div>
            <h4 style="margin:0 0 10px 0; color:var(--color-csic);">CUSTOMER DETAILS</h4>
            <p><strong>Name:</strong> ${client.first_name} ${client.last_name}</p>
            <p><strong>Email:</strong> ${client.email}</p>
            <p><strong>Entity:</strong> ${client.entity || 'N/A'}</p>
            ${isInternal ? `<p><strong>Group:</strong> ${client.group_name || 'N/A'}</p>` : ''}
          </div>
          ${isInternal ? `
          <div>
            <h4 style="margin:0 0 10px 0; color:var(--color-csic);">INTERNAL DATA</h4>
            <p><strong>IP Address:</strong> ${client.ip_address || 'N/A'}</p>
            <p><strong>CI (Project ID):</strong> ${client.project_id || 'N/A'}</p>
            <p><strong>CP (Account):</strong> ${client.internal_account || 'N/A'}</p>
            <hr style="border:0; border-top:1px solid #ddd; margin:10px 0;">
            <p><strong>Offer created:</strong> ${new Date(offer.created_at).toLocaleString()}</p>
          </div>
          ` : `
          <style></style>
          `}
        </div>
        ${!isInternal ? `<p style="font-size:13px; color:#888; margin-bottom:15px;"><strong>Offer created:</strong> ${new Date(offer.created_at).toLocaleString()}</p>` : ''}

        <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
          <thead>
            <tr style="text-align:left; border-bottom:2px solid #eee; color:#666; font-size:13px;">
              <th style="padding:10px;">SERVICE</th>
              <th style="padding:10px;">PRICE/H</th>
              <th style="padding:10px;">HOURS</th>
              <th style="padding:10px;">TOTAL PRICE (€)</th>
              <th style="padding:10px;">INTERNAL NOTES</th>
              <th style="padding:10px; text-align:right;">ACTIONS</th>
            </tr>
          </thead>
          <tbody>${serviceRows}</tbody>
        </table>

        <!-- ADD SERVICE SECTION -->
        ${!readOnly ? `
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:15px; margin-bottom:20px;">
          <h4 style="margin:0 0 12px 0; font-size:13px; color:#475569; letter-spacing:0.025em;">+ ADD ADDITIONAL SERVICE</h4>
          <div style="display:flex; gap:10px; align-items:center;">
            <select id="newServiceSelect" style="flex:1; padding:8px; border:1px solid #cbd5e1; border-radius:4px; font-size:14px; background:white;">
                <option value="">Select a service from catalog...</option>
                ${catalogItems.map(item => `<option value="${item.name}">${item.name}</option>`).join('')}
            </select>
            <input type="number" id="newServiceHours" placeholder="Hours" value="" step="0.5" min="0" style="width:80px; padding:8px; border:1px solid #cbd5e1; border-radius:4px; font-size:14px;">
            <button onclick="window.addServiceToOffer(${offer.id}, ${isMineTab})" 
                    style="background:#1e293b; color:white; border:none; padding:8px 20px; border-radius:4px; font-weight:600; cursor:pointer; font-size:14px; transition: background 0.2s;"
                    onmouseover="this.style.background='#334155'" onmouseout="this.style.background='#1e293b'">
              ADD
            </button>
          </div>
        </div>
        ` : ''}

        <!-- GRAND TOTAL BAR -->
        <div id="rev-grand-total-bar" style="display:flex; justify-content:flex-start; padding:12px 4px 18px 4px; border-top:2px solid #e2e8f0; margin-top:4px; margin-bottom:20px;">
          <div style="text-align:left;">
            <div style="font-size:12px; font-weight:600; color:#64748b; letter-spacing:0.08em; text-transform:uppercase; text-decoration:underline; margin-bottom:4px;">Total Price</div>
            <div id="rev-grand-total" style="font-size:28px; font-weight:700; color:#1e293b; letter-spacing:-0.5px;"></div>
          </div>
        </div>

        <h4 style="color:#888; margin-bottom:10px;">MESSAGE FOR THE CLIENT (GLOBAL COMMENT)</h4>
        <textarea id="globalComment" ${readOnly ? 'disabled style="width:100%;height:80px;padding:10px;border:1px solid #ccc;border-radius:4px;font-family:inherit;background:#f3f4f6;color:#888;cursor:not-allowed;resize:none;"' : 'style="width:100%; height:80px; padding:10px; border:1px solid #ccc; border-radius:4px; font-family:inherit;"'} placeholder="Explain the quote to the researcher...">${offer.technician_comment || ''}</textarea>

        ${readOnly ? `
          <div style="background:#fff3cd; border:1px solid #ffc107; border-radius:6px; padding:12px; margin-top:15px; font-size:13px; color:#856404; display:flex; align-items:center; gap:8px;">
            This offer has already been sent to the client and cannot be modified from here.
          </div>
        ` : `
          <button onclick="window.sendQuotedOffer(${offer.id})" class="btn-card btn-send">
            SEND QUOTED OFFER TO CLIENT
          </button>
        `}
      </div>
    `;

    // Initialize grand total and wire manual price edits
    window.recalcGrandTotal();
    if (!readOnly) {
      document.querySelectorAll('.rev-total-price').forEach(inp => {
        inp.addEventListener('input', window.recalcGrandTotal);
      });
    }
  } catch (err) {
    console.error("Error opening review panel:", err);
  }
};

// Live update total price when hours change
window.updateRowPrice = function (serviceId, hoursVal, pricePerHour) {
  const hours = parseFloat(hoursVal) || 0;
  const total = (hours * pricePerHour).toFixed(2);
  const totalInput = document.querySelector(`.rev-total-price[data-id="${serviceId}"]`);
  if (totalInput) totalInput.value = total;
  window.recalcGrandTotal();
};

// Recalculate grand total from all rev-total-price inputs
window.recalcGrandTotal = function () {
  const inputs = document.querySelectorAll('.rev-total-price');
  let sum = 0;
  inputs.forEach(inp => { sum += parseFloat(inp.value) || 0; });
  const el = document.getElementById('rev-grand-total');
  if (el) el.textContent = sum.toFixed(2) + ' €';
};

window.sendQuotedOffer = async function (offerId) {
  const hours = document.querySelectorAll(".rev-hours");
  const notes = document.querySelectorAll(".rev-notes");
  const totals = document.querySelectorAll(".rev-total-price");
  const comment = document.getElementById("globalComment").value;

  const servicesData = Array.from(hours).map((h) => {
    const row = h.closest("tr");
    const noteEl = row.querySelector(".rev-notes");
    const totalEl = row.querySelector(".rev-total-price");
    
    return {
      id: parseInt(h.dataset.id),
      hours: parseFloat(h.value),
      quoted_price: parseFloat(totalEl?.value) || null,
      comment: noteEl ? noteEl.value : "",
    };
  });

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
      alert("Review finalized. Offer sent to the client.");
      window.loadAllOffers();
    } else {
      alert("Error sending the offer.");
    }
  } catch (err) {
    console.error("Error saving review:", err);
  }
};

window.deleteServiceFromOffer = async function (serviceId, offerId, isMineTab, serviceName) {
  if (!confirm(`Are you sure you want to delete "${serviceName}"?`)) return;

  try {
    const response = await fetch(`/api/technician/services/${serviceId}`, {
      method: "DELETE"
    });
    if (response.ok) {
      window.openReviewPanel(offerId, isMineTab);
    } else {
      const err = await response.json();
      alert(`Error: ${err.detail || "Could not delete service"}`);
    }
  } catch (err) {
    console.error("Error deleting service:", err);
  }
};

window.addServiceToOffer = async function (offerId, isMineTab) {
  const select = document.getElementById("newServiceSelect");
  const hoursInput = document.getElementById("newServiceHours");

  if (!select.value || !hoursInput.value) {
    alert("Please select a service from the catalog and indicate the number of hours.");
    return;
  }

  try {
    const response = await fetch(`/api/technician/offers/${offerId}/services`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        service_name: select.value,
        hours: parseFloat(hoursInput.value) || 0
      })
    });
    if (response.ok) {
      window.openReviewPanel(offerId, isMineTab);
    } else {
      const err = await response.json();
      alert(`Error: ${err.detail || "Could not add service"}`);
    }
  } catch (err) {
    console.error("Error adding service:", err);
  }
};


// --- 5. OFFER LIST RENDERING ---
window.currentGlobalFilter = 'all';
window.currentMyFilter = 'all';

window.setFilter = function (type, status, btnElement) {
  if (type === 'global') {
    window.currentGlobalFilter = status;
    document.querySelectorAll('.global-btn').forEach(btn => btn.classList.remove('active'));
  } else {
    window.currentMyFilter = status;
    document.querySelectorAll('.my-btn').forEach(btn => btn.classList.remove('active'));
  }
  btnElement.classList.add('active');
  renderAll();
};

function renderAll() {
  const techData = JSON.parse(localStorage.getItem("currentUser"));
  const techId = techData ? techData.id : null;

  let globalOffers = window.allOffers || [];
  let myOffers = globalOffers.filter(o =>
    o.manager_id === techId || (o.services && o.services.some(s => s.technician_id === techId))
  );

  if (window.currentGlobalFilter !== 'all') {
    globalOffers = globalOffers.filter(o => o.status === window.currentGlobalFilter);
  }

  if (window.currentMyFilter !== 'all') {
    myOffers = myOffers.filter(o => o.status === window.currentMyFilter);
  }

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
      "<p style='text-align:center; padding: 20px; color: #666;'>No requests in this section.</p>";
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
            <span style="font-weight:bold; color:var(--color-csic); font-size: 1.2em;">PO_${offer.id}</span>
            <span style="background-color:${statusColor}; color: white; padding:5px 15px; border-radius:12px; font-size:12px; font-weight:bold;">
                ${offer.status}
            </span>
        </div>
        <div style="display: flex; gap: 40px; margin-bottom: 15px; font-size: 14px; color: #555;">
            <p style="margin: 0;"><strong>CLIENT:</strong> ${offer.client ? offer.client.first_name + ' ' + offer.client.last_name : 'ID ' + offer.client_id}</p>
            <p style="margin: 0;"><strong>DATE:</strong> ${new Date(offer.created_at).toLocaleDateString()}</p>
        </div>
        
        <details data-offer-id="${offer.id}" style="margin: 10px 0 20px 0; padding: 10px; background: #f9f9f9; border: 1px solid #ddd; border-radius: 6px;">
            <summary style="cursor: pointer; font-weight: bold; color: #2c3e50;">View Services (${offer.services.length})</summary>
            <div style="margin-top: 10px; display: flex; flex-direction: column; gap: 8px;">
            ${offer.services.map((s) => `
                <div style="display: flex; justify-content: space-between; align-items: stretch; background: white; padding: 0; border: 1px solid #eee; border-radius: 4px; gap: 0; overflow: hidden;">
                    <div style="font-size:14px; color:#333; flex: 1; padding: 8px 12px;">
                        <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
                            <span><strong>${s.service_name}</strong> (${s.hours}h)</span>
                            ${s.technician_id ? `<span style="font-size:12px; color:#555;"><strong>Assigned Technician:</strong> ${s.technician ? s.technician.first_name + ' ' + s.technician.last_name : 'Technician #' + s.technician_id}</span>` : ''}
                        </div>
                        ${s.comment ? `<div style="margin-top:4px; font-size:12px; color:#777; display:flex; align-items:center; gap:5px;"><svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='12' height='12' fill='#aaa'><path d='M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z'/></svg><em>${s.comment}</em></div>` : ''}
                    </div>
                    <div style="display:flex; align-items:stretch;">
                        ${!s.technician_id
          ? `<button onclick="window.assignService(${s.id})" class="btn-assign-service">Assign to me</button>`
          : s.technician_id === techId
            ? `<button onclick="window.unassignService(${s.id})" class="btn-unassign-service">Unassign</button>`
            : ''
        }
                    </div>
                </div>
            `).join("")}
            </div>
        </details>
        
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 15px;">
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            ${offer.manager_id === techId ? `<button onclick="window.unassignOffer(${offer.id})" class="btn-card btn-unassign">Release Offer</button>` : `<button onclick="window.assignOffer(${offer.id})" class="btn-card btn-manager">Manage Offer</button>`}
            ${
        // Review button always visible; readOnly when not 'requested'
        `<button onclick="window.openReviewPanel(${offer.id}, ${!isGlobal}, ${offer.status !== 'requested'})" class="btn-card btn-review">Review</button>`
        }
            ${offer.status === 'accepted' ? `<button onclick="window.updateOfferStatus(${offer.id}, 'finished')" class="btn-card btn-finish">Finish Work</button>` : ''}
          </div>
          <div style="text-align: right;">
            ${offer.manager_id
          ? `<span style="background-color:${offer.manager_id === techId ? '#7dbe9e' : '#e08080'}; color:white; font-weight:bold; font-size:12px; padding: 4px 10px; border-radius: 6px;">Manager: ${offer.manager ? offer.manager.first_name + ' ' + offer.manager.last_name : 'Technician #' + offer.manager_id}</span>`
          : ""
        }
          </div>
        </div>
    `;
      container.appendChild(card);
    });
}

// --- 5. MODAL SYSTEM FOR FULL COMMENTS ---
window.showFullNote = function (text) {
  // Clear any existing modal
  const existing = document.getElementById("commentModal");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.id = "commentModal";
  modal.className = "modal-backdrop";
  modal.onclick = (e) => {
    if (e.target === modal) window.closeCommentModal();
  };

  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h3>FULL NOTE</h3>
        <button onclick="window.closeCommentModal()" style="background:none; border:none; color:white; font-size:20px; cursor:pointer;">&times;</button>
      </div>
      <div class="modal-body">${text || "<em>No comments available.</em>"}</div>
      <div class="modal-footer">
        <button onclick="window.closeCommentModal()" class="btn-modal-close">CLOSE</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
};

window.closeCommentModal = function () {
  const modal = document.getElementById("commentModal");
  if (modal) {
    modal.style.opacity = "0";
    setTimeout(() => modal.remove(), 200);
  }
};
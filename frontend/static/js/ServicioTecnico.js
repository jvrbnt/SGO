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

// --- AUTHENTICATION INTERCEPTOR ---
const originalFetch = window.fetch;
window.fetch = async function() {
    let [resource, config] = arguments;
    if(typeof resource === 'string' && resource.startsWith('/api') && resource !== '/api/login') {
        const token = localStorage.getItem('authToken');
        if(token) {
            config = config || {};
            config.headers = config.headers || {};
            config.headers['Authorization'] = `Bearer ${token}`;
        }
    }
    const response = await originalFetch(resource, config);
    if (response.status === 401) {
        alert("Session expired. Please log in again.");
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        window.location.href = '/login';
    }
    return response;
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
  window.loadCatalogPrices();
  window.loadBillingClients();

  // Adjust UI based on privilege level
  if (techData.privilege_level === "Admin" || techData.privilege_level === "Mod") {
    const tabPreciosBtn = document.getElementById("tabPreciosBtn");
    if (tabPreciosBtn) tabPreciosBtn.textContent = "Dashboard";

    if (techData.privilege_level === "Admin") {
      const adminPanel = document.getElementById("adminPanel");
      if (adminPanel) adminPanel.style.display = "flex";
      window.loadAdminTechnicians();
    }
  }
});

const globalList = document.getElementById("globalRequestList");

// --- 3. API COMMUNICATION ---

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

window.markServiceStatus = async function (serviceId, newStatus) {
  try {
    const response = await fetch(`/api/technician/services/${serviceId}/status?new_status=${newStatus}`, {
      method: "PATCH"
    });
    if (response.ok) {
      const data = await response.json();
      if (data.offer_finished) {
        alert("All services completed — offer has been marked as FINISHED!");
      }
      window.loadAllOffers();
    } else {
      const error = await response.json();
      alert("Error: " + (error.detail || "Could not update service status"));
    }
  } catch (err) {
    console.error("Network error:", err);
  }
};

// --- 4. REVIEW MODE (TECHNICIAN WORKFLOW) ---

// Map entity → price field
function getPriceField(entity) {
  if (!entity) return 'price_internal';
  const e = entity.toLowerCase();
  if (e === 'internal') return 'price_internal';
  if (e === 'csic' || e === 'uam') return 'price_csic';
  if (e === 'opis' || e === 'university') return 'price_public';
  if (e === 'company') return 'price_private';
  return 'price_internal'; // fallback
}

window.openReviewPanel = async function (offerId, isMineTab, readOnly = false, previousEdits = null) {
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
    const hasManager = offer.manager_id != null;
    const allServicesAssigned = activeServices.length > 0 && activeServices.every(s => s.technician_id != null);
    const canSend = hasManager && allServicesAssigned;
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
          <td style="padding:10px; display:flex; align-items:center; gap:5px;">
            <input type="number" class="rev-hours" data-id="${s.id}" data-pph="${pricePerHour}" data-original="${s.original_hours !== null ? s.original_hours : s.hours}" value="${s.hours}" step="0.5" min="0"
              style="width:65px; padding:5px; border:1px solid #ccc; border-radius:4px;"
              ${readOnly ? 'disabled style="width:65px;padding:5px;border:1px solid #ccc;border-radius:4px;background:#f3f4f6;color:#888;cursor:not-allowed;"' : `oninput="window.updateRowPrice('${s.id}', this.value, ${pricePerHour})"`}>
            ${(!s.added_by_technician && !readOnly) ? `
              <button class="btn-reset-hours" data-id="${s.id}" style="display:${parseFloat(s.hours) !== parseFloat(s.original_hours !== null ? s.original_hours : s.hours) ? 'inline-block' : 'none'}; background:none; border:none; cursor:pointer; color:var(--color-csic); padding:2px;" title="Reset to original hours" onclick="window.resetHours('${s.id}')">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-rotate-ccw"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>
              </button>
            ` : ''}
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
          <button onclick="window.backToListFromReview(${offer.id})" class="btn-card btn-back">← BACK TO LIST</button>
        </div>

        <div style="display:grid; grid-template-columns:${isInternal ? '1fr 1fr' : '1fr'}; gap:20px; background:#f9f9f9; padding:15px; border-radius:6px; margin-bottom:20px; font-size:14px;">
          <div>
            <h4 style="margin:0 0 10px 0; color:var(--color-csic);">CUSTOMER DETAILS</h4>
            <p><strong>Name:</strong> ${client.first_name} ${client.last_name}</p>
            <p><strong>Email:</strong> ${client.email}</p>
            <p><strong>Entity:</strong> ${client.entity || 'N/A'}</p>
            ${isInternal ? `<p><strong>Group:</strong> ${client.grupo || 'N/A'}</p>` : ''}
          </div>
          ${isInternal ? `
          <div>
            <h4 style="margin:0 0 10px 0; color:var(--color-csic);">INTERNAL DATA</h4>
            <p><strong>IP:</strong> ${client.investigador_principal || 'N/A'}</p>
            <p><strong>CI:</strong> ${client.cuenta_interna || 'N/A'}</p>
            <p><strong>CP:</strong> ${client.codigo_proyecto || 'N/A'}</p>
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
          <button onclick="window.sendQuotedOffer(${offer.id})" class="btn-card btn-send" ${!canSend ? 'disabled style="opacity:0.5; cursor:not-allowed;"' : ''}>
            SEND QUOTED OFFER TO CLIENT
          </button>
          ${!canSend ? `
            <div style="background:#fce4e4; border:1px solid #f8aaaa; border-radius:6px; padding:10px; margin-top:10px; font-size:12px; color:#cc0000;">
              <strong>Note:</strong> You can only send the quotation when the offer has a Manager assigned AND all services have technicians assigned.
            </div>
          ` : ''}
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

    if (previousEdits) {
      window.restoreEdits(previousEdits);
    } else if (window.offerDrafts && window.offerDrafts[offer.id]) {
      window.restoreEdits(window.offerDrafts[offer.id]);
    }
  } catch (err) {
    console.error("Error opening review panel:", err);
  }
};

window.offerDrafts = window.offerDrafts || {};

window.backToListFromReview = function (offerId) {
  if (window.captureEdits) {
    window.offerDrafts[offerId] = window.captureEdits();
  }
  window.loadAllOffers();
};

// Live update total price when hours change
window.updateRowPrice = function (serviceId, hoursVal, pricePerHour) {
  const hours = parseFloat(hoursVal) || 0;
  const total = (hours * pricePerHour).toFixed(2);
  const totalInput = document.querySelector(`.rev-total-price[data-id="${serviceId}"]`);
  if (totalInput) totalInput.value = total;
  window.recalcGrandTotal();

  const input = document.querySelector(`.rev-hours[data-id="${serviceId}"]`);
  const resetBtn = document.querySelector(`.btn-reset-hours[data-id="${serviceId}"]`);
  if (input && resetBtn) {
    const original = parseFloat(input.dataset.original);
    if (parseFloat(hoursVal) !== original) {
      resetBtn.style.display = 'inline-block';
    } else {
      resetBtn.style.display = 'none';
    }
  }
};

window.resetHours = function (serviceId) {
  const input = document.querySelector(`.rev-hours[data-id="${serviceId}"]`);
  if (input) {
    input.value = input.dataset.original;
    window.updateRowPrice(serviceId, input.value, parseFloat(input.dataset.pph));
  }
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
      if (window.offerDrafts && window.offerDrafts[offerId]) {
        delete window.offerDrafts[offerId];
      }
      window.loadAllOffers();
    } else {
      alert("Error sending the offer.");
    }
  } catch (err) {
    console.error("Error saving review:", err);
  }
};

window.captureEdits = function () {
  const edits = {};
  document.querySelectorAll(".rev-hours").forEach(inp => {
    const id = inp.dataset.id;
    edits[id] = {
      hours: inp.value,
      note: document.querySelector(`.rev-notes[data-id="${id}"]`)?.value || "",
      quotedPrice: document.querySelector(`.rev-total-price[data-id="${id}"]`)?.value || ""
    };
  });
  edits.globalComment = document.getElementById("globalComment")?.value || "";
  return edits;
};

window.restoreEdits = function (edits) {
  if (!edits) return;
  document.querySelectorAll(".rev-hours").forEach(inp => {
    const id = inp.dataset.id;
    const edit = edits[id];
    if (edit) {
      inp.value = edit.hours;
      const noteInp = document.querySelector(`.rev-notes[data-id="${id}"]`);
      if (noteInp) noteInp.value = edit.note;
      const priceInp = document.querySelector(`.rev-total-price[data-id="${id}"]`);
      if (priceInp) priceInp.value = edit.quotedPrice;
      window.updateRowPrice(id, edit.hours, parseFloat(inp.dataset.pph));
    }
  });
  const gc = document.getElementById("globalComment");
  if (gc && edits.globalComment !== undefined) gc.value = edits.globalComment;
};

window.deleteServiceFromOffer = async function (serviceId, offerId, isMineTab, serviceName) {
  const previousEdits = window.captureEdits ? window.captureEdits() : null;
  if (!confirm(`Are you sure you want to delete "${serviceName}"?`)) return;

  try {
    const response = await fetch(`/api/technician/services/${serviceId}`, {
      method: "DELETE"
    });
    if (response.ok) {
      window.openReviewPanel(offerId, isMineTab, false, previousEdits);
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

  const previousEdits = window.captureEdits ? window.captureEdits() : null;

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
      window.openReviewPanel(offerId, isMineTab, false, previousEdits);
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
          invoiced: "#9b59b6",
          finished: "#2c3e50",
        }[offer.status] || "#6c757d";

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
            <span style="font-weight:bold; color:var(--color-csic); font-size: 1.2em;">OFFER ${offer.reference || offer.id}</span>
            <span style="background-color:${statusColor}; color: white; padding:5px 15px; border-radius:12px; font-size:12px; font-weight:bold;">
                ${offer.status}
            </span>
        </div>
        <div style="display: flex; gap: 40px; margin-bottom: 15px; font-size: 14px; color: #555;">
            <p style="margin: 0;"><strong>CLIENT:</strong> ${offer.client ? offer.client.first_name + ' ' + offer.client.last_name : 'ID ' + offer.client_id}</p>
            <p style="margin: 0;"><strong>DATE:</strong> ${new Date(offer.created_at).toLocaleDateString()}</p>
        </div>
        
        <div style="margin: 10px 0 20px 0; padding: 10px; background: #f9f9f9; border: 1px solid #ddd; border-radius: 6px;">
            <div style="font-weight: bold; color: #2c3e50; margin-bottom: 8px;">Services (${offer.services.filter(s => !s.is_deleted).length})</div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
            ${offer.services
          .filter(s => !s.is_deleted)
          .sort((a, b) => a.service_name.localeCompare(b.service_name))
          .map((s) => `
                <div style="display: flex; justify-content: space-between; align-items: stretch; background: white; padding: 0; border: 1px solid #eee; border-radius: 4px; gap: 0; overflow: hidden;">
                    <div style="font-size:14px; color:#333; flex: 1; padding: 8px 12px;">
                        <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
                            <span><strong>${s.service_name}</strong> (${s.hours}h)</span>
                            ${s.technician_id ? `<span style="font-size:12px; color:#555;"><strong>Assigned Technician:</strong> ${s.technician ? s.technician.first_name + ' ' + s.technician.last_name : 'Technician #' + s.technician_id}</span>` : ''}
                            ${(offer.status === 'accepted' || offer.status === 'finished') ? `
                              <span style="font-size:11px; font-weight:bold; padding:4px 8px; border-radius:12px; display:inline-flex; align-items:center; gap:4px; ${s.status === 'done' ? 'background:#d1fae5; color:#065f46;' : 'background:#fef3c7; color:#92400e;'}">
                                ${s.status === 'done' 
                                  ? `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg> DONE` 
                                  : `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> PENDING`}
                              </span>
                            ` : ''}
                        </div>
                        ${s.comment ? `<div style="margin-top:4px; font-size:12px; color:#777; display:flex; align-items:center; gap:5px;"><svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='12' height='12' fill='#aaa'><path d='M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z'/></svg><em>${s.comment}</em></div>` : ''}
                    </div>
                    <div style="display:flex; align-items:stretch;">
                        ${(offer.status === 'accepted' || offer.status === 'finished')
                          ? (s.technician_id === techId || (techData && techData.privilege_level === 'Admin')
                              ? (s.status !== 'done'
                                ? `<button onclick="window.markServiceStatus(${s.id}, 'done')" style="background:#059669; color:white; border:none; padding:8px 14px; cursor:pointer; font-size:12px; font-weight:bold; white-space:nowrap;">✓ Service Done</button>`
                                : `<button onclick="window.markServiceStatus(${s.id}, 'pending')" style="background:#d97706; color:white; border:none; padding:8px 14px; cursor:pointer; font-size:12px; font-weight:bold; white-space:nowrap;">↩ Back to Pending</button>`)
                              : '')
                          : (!s.technician_id
              ? `<button onclick="window.assignService(${s.id})" class="btn-assign-service">Assign to me</button>`
              : s.technician_id === techId && offer.status === 'requested'
                ? `<button onclick="window.unassignService(${s.id})" class="btn-unassign-service">Unassign</button>`
                : '')
            }
                    </div>
                </div>
            `).join("")}
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 15px;">
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            ${offer.manager_id === techId 
              ? (offer.status === 'requested' ? `<button onclick="window.unassignOffer(${offer.id})" class="btn-card btn-unassign">Release Offer</button>` : '') 
              : (!offer.manager_id 
                  ? `<button onclick="window.assignOffer(${offer.id})" class="btn-card btn-manager">Manage Offer</button>` 
                  : '')
            }
            <button onclick="window.openReviewPanel(${offer.id}, ${!isGlobal}, ${offer.status !== 'requested'})" class="btn-card btn-review">Review</button>
            ${offer.status !== 'requested' ? `<button onclick="window.downloadOfferDocument(${offer.id})" class="btn-card" style="background:#2c3e50; color:white;" title="Download offer as Word document">📄 Document</button>` : ''}
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

// --- 6. PRICE MANAGEMENT ---
window.loadCatalogPrices = async function () {
  try {
    const response = await fetch("/api/catalog");
    if (!response.ok) throw new Error("Failed to fetch catalog");
    const catalog = await response.json();
    window.catalogPrices = catalog;
    window.renderPricesTable();
  } catch (error) {
    console.error("Error loading catalog prices:", error);
    const container = document.getElementById("pricesTableContainer");
    if (container) {
      container.innerHTML = `<p style="color: red; text-align: center;">Error loading catalog prices.</p>`;
    }
  }
};

window.pendingPriceChanges = window.pendingPriceChanges || {};

window.renderPricesTable = function () {
  const container = document.getElementById("pricesTableContainer");
  if (!container || !window.catalogPrices) return;

  const techData = JSON.parse(localStorage.getItem("currentUser"));
  const canEdit = techData && (techData.privilege_level === "Admin" || techData.privilege_level === "Mod");
  const pending = window.pendingPriceChanges || {};
  const pendingCount = Object.keys(pending).reduce((acc, id) => acc + Object.keys(pending[id]).length, 0);

  function renderCell(item, field, label, dbPrice) {
    const pendingEntry = pending[item.id] && pending[item.id][field];
    if (pendingEntry) {
      return `
        <td style="padding:8px 10px; background:#fff8e1; border:1px solid #f59e0b; border-radius:4px;">
          <button class="price-edit-btn" onclick="window.openPriceEditor(${item.id}, '${item.name.replace(/'/g, "\\'") }', '${label}', '${field}', ${pendingEntry.newPrice})"
            style="background:transparent; border:none; width:100%; text-align:left; cursor:pointer; padding:0;">
            <span style="text-decoration:line-through; color:#94a3b8; font-size:11px; display:block;">${pendingEntry.oldPrice.toFixed(2)} €/h</span>
            <span style="color:#f59e0b; font-weight:700; font-size:14px;">${pendingEntry.newPrice.toFixed(2)} €/h</span>
          </button>
        </td>`;
    } else {
      return `
        <td style="padding:12px 10px;">
          ${canEdit ? `<button class="price-edit-btn" onclick="window.openPriceEditor(${item.id}, '${item.name.replace(/'/g, "\\'") }', '${label}', '${field}', ${dbPrice})">${dbPrice.toFixed(2)} €/h</button>` : `<span style="font-weight:bold; color:var(--color-csic);">${dbPrice.toFixed(2)} €/h</span>`}
        </td>`;
    }
  }

  const rows = [...window.catalogPrices].sort((a, b) => a.name.localeCompare(b.name)).map(item => `
    <tr style="border-bottom:1px solid #eee; transition: background 0.2s;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
      <td style="padding:12px 10px; font-weight:600; color:#1e293b;">${item.name}</td>
      ${renderCell(item, 'price_internal', 'Internal', item.price_internal)}
      ${renderCell(item, 'price_csic', 'CSIC/UAM', item.price_csic || 0)}
      ${renderCell(item, 'price_public', 'University/OPIS', item.price_public || 0)}
      ${renderCell(item, 'price_private', 'Company', item.price_private || 0)}
    </tr>
  `).join('');

  const pendingBar = canEdit && pendingCount > 0 ? `
    <div style="margin-top:20px; padding:15px 20px; background:#fff8e1; border:2px solid #f59e0b; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
      <span style="color:#92400e; font-weight:600; font-size:14px;">⚠️ ${pendingCount} unsaved change${pendingCount > 1 ? 's' : ''}. Click <strong>Save All</strong> to commit to the database.</span>
      <div style="display:flex; gap:10px;">
        <button onclick="window.cancelAllPrices()" style="background:#ef4444; color:white; border:none; padding:9px 20px; border-radius:6px; font-weight:bold; cursor:pointer; font-size:13px;">CANCEL</button>
        <button onclick="window.saveAllPrices()" style="background:#10b981; color:white; border:none; padding:9px 20px; border-radius:6px; font-weight:bold; cursor:pointer; font-size:13px;">SAVE ALL CHANGES</button>
      </div>
    </div>
  ` : '';

  container.innerHTML = `
    <table style="width:100%; border-collapse:collapse; font-size:14px;">
      <thead>
        <tr style="text-align:left; border-bottom:2px solid #eee; color:#666;">
          <th style="padding:12px 10px;">SERVICE NAME</th>
          <th style="padding:12px 10px;">INTERNAL (€/h)</th>
          <th style="padding:12px 10px;">CSIC/UAM (€/h)</th>
          <th style="padding:12px 10px;">UNIV/OPIS (€/h)</th>
          <th style="padding:12px 10px;">COMPANY (€/h)</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
    ${pendingBar}
  `;

  // Add some styles if not already in CSS
  if (!document.getElementById('price-table-styles')) {
    const style = document.createElement('style');
    style.id = 'price-table-styles';
    style.innerHTML = `
      .price-edit-btn {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 5px 10px;
        cursor: pointer;
        font-weight: 500;
        color: #334155;
        transition: all 0.2s;
        width: 100%;
        text-align: center;
      }
      .price-edit-btn:hover {
        background: #e2e8f0;
        border-color: #94a3b8;
        color: #0f172a;
      }
    `;
    document.head.appendChild(style);
  }
};

let currentEditingItem = null;

window.openPriceEditor = function (itemId, serviceName, entityLabel, field, currentPrice) {
  currentEditingItem = { itemId, field, currentPrice };
  const modal = document.getElementById("priceEditModal");
  const context = document.getElementById("priceEditContext");
  const input = document.getElementById("newPriceInput");

  if (modal && context && input) {
    context.innerHTML = `New price for <span style="color:var(--color-csic); border-bottom: 2px solid #e2e8f0; padding-bottom: 2px;">${serviceName}</span><br>specifically for <span style="color:#2563eb; font-weight: 700;">${entityLabel}</span>:`;
    input.value = currentPrice;
    modal.style.display = "flex";
    modal.style.opacity = "1";
    input.focus();
  }
};

window.closePriceModal = function () {
  const modal = document.getElementById("priceEditModal");
  if (modal) {
    modal.style.opacity = "0";
    setTimeout(() => {
      modal.style.display = "none";
      currentEditingItem = null;
    }, 200);
  }
};

// Stage the price change locally — does NOT call the API yet
window.savePriceUpdate = function () {
  if (!currentEditingItem) return;

  const newVal = parseFloat(document.getElementById("newPriceInput").value);
  if (isNaN(newVal) || newVal < 0) {
    alert("Please enter a valid price.");
    return;
  }

  const { itemId, field, currentPrice } = currentEditingItem;

  // Store pending change (keep original DB price for the strikethrough)
  if (!window.pendingPriceChanges[itemId]) {
    window.pendingPriceChanges[itemId] = {};
  }
  // If reverting to the DB value, remove the pending entry
  const dbItem = window.catalogPrices.find(i => i.id === itemId);
  const dbPrice = dbItem ? (dbItem[field] || 0) : currentPrice;
  if (newVal === dbPrice && window.pendingPriceChanges[itemId][field]) {
    delete window.pendingPriceChanges[itemId][field];
    if (Object.keys(window.pendingPriceChanges[itemId]).length === 0) {
      delete window.pendingPriceChanges[itemId];
    }
  } else {
    window.pendingPriceChanges[itemId][field] = { oldPrice: dbPrice, newPrice: newVal };
  }

  window.closePriceModal();
  // Re-render table to show the pending state
  window.renderPricesTable();
};

// Commit all pending changes to the server
window.saveAllPrices = async function () {
  const pending = window.pendingPriceChanges;
  const entries = [];
  Object.keys(pending).forEach(itemId => {
    const changes = pending[itemId];
    entries.push({ itemId: parseInt(itemId), changes });
  });

  if (entries.length === 0) return;

  const totalChanges = entries.reduce((acc, entry) => acc + Object.keys(entry.changes).length, 0);
  if (!confirm(`Are you sure you want to save ${totalChanges} price change(s) to the database?\n\nThis action cannot be undone.`)) {
    return;
  }

  try {
    // Send each item update sequentially
    for (const { itemId, changes } of entries) {
      const body = {};
      Object.keys(changes).forEach(field => { body[field] = changes[field].newPrice; });
      const res = await fetch(`/api/catalog/${itemId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `Error updating item ${itemId}`);
      }
    }
    // All saved successfully
    window.pendingPriceChanges = {};
    window.loadCatalogPrices();
  } catch (error) {
    alert("Error saving prices: " + error.message);
  }
};

// Discard all pending changes
window.cancelAllPrices = function () {
  window.pendingPriceChanges = {};
  window.renderPricesTable();
};

// --- 7. ADMIN DASHBOARD MANAGEMENT ---
window.loadAdminTechnicians = async function () {
  const list = document.getElementById("adminTechList");
  if (!list) return;

  try {
    const res = await fetch("/api/admin/technicians");
    if (!res.ok) throw new Error("Could not fetch technicians");
    const technicians = await res.json();

    // Admin user details
    const currentUser = JSON.parse(localStorage.getItem("currentUser"));

    list.innerHTML = technicians.map(t => {
      const isSelf = t.id === currentUser.id;
      // Cannot toggle own role or Admins overall except self-protection
      const canToggle = !isSelf && t.privilege_level !== "Admin";

      let actionBtn = "";
      if (canToggle) {
        const nextRole = t.privilege_level === "Mod" ? "Technician" : "Mod";
        const btnColor = nextRole === "Mod" ? "#3b82f6" : "#f59e0b";
        actionBtn = `<button onclick="window.adminToggleRole(${t.id}, '${nextRole}')" style="background:${btnColor}; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:bold; font-size:12px; cursor:pointer;">Make ${nextRole}</button>`;
      } else if (isSelf) {
        actionBtn = `<span style="font-size:12px; color:#9ca3af; font-style:italic;">You</span>`;
      } else if (t.privilege_level === "Admin") {
        actionBtn = `<span style="font-size:12px; color:#9ca3af; font-style:italic;">Admin</span>`;
      }

      return `
        <tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:12px 8px;"><b>${t.first_name} ${t.last_name}</b></td>
          <td style="padding:12px 8px; color:#64748b;">${t.email}</td>
          <td style="padding:12px 8px;"><span style="background:#e2e8f0; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold; color:#334155;">${t.privilege_level}</span></td>
          <td style="padding:12px 8px;">${actionBtn}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    list.innerHTML = `<tr><td colspan="4" style="color:red; padding:10px;">Error loading users</td></tr>`;
  }
};

window.adminCreateTechnician = async function () {
  const first = document.getElementById("newTechFirst").value.trim();
  const last = document.getElementById("newTechLast").value.trim();
  const email = document.getElementById("newTechEmail").value.trim();
  const password = document.getElementById("newTechPassword").value;

  if (!first || !last || !email || !password) {
    alert("Please fill in all fields to create a technician.");
    return;
  }

  try {
    const res = await fetch("/api/admin/technicians", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        first_name: first,
        last_name: last,
        email: email,
        password: password,
        privilege_level: "Technician"
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error creating technician");

    alert("Technician created successfully!");
    document.getElementById("newTechFirst").value = "";
    document.getElementById("newTechLast").value = "";
    document.getElementById("newTechEmail").value = "";
    document.getElementById("newTechPassword").value = "";
    window.loadAdminTechnicians();
  } catch (err) {
    alert(err.message);
  }
};

window.adminToggleRole = async function (id, newRole) {
  if (!confirm(`Are you sure you want to change this user's role to ${newRole}?`)) return;

  try {
    const res = await fetch(`/api/admin/technicians/${id}/role?privilege_level=${newRole}`, {
      method: "PATCH"
    });

    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Could not change role");
    }

    window.loadAdminTechnicians();
  } catch (err) {
    alert(err.message);
  }
};

// --- 8. INVOICING / BILLING MODULE ---

window.loadBillingClients = async function () {
  const techData = JSON.parse(localStorage.getItem("currentUser"));
  if (!techData) return;
  const select = document.getElementById("billingClientSelect");
  if (!select) return;

  try {
    const res = await fetch(`/api/technician/billing-clients?tech_id=${techData.id}`);
    const clients = await res.json();

    let html = '<option value="">-- Select a client --</option>';
    if (clients.length === 0) {
      html = '<option value="">-- No clients with pending offers --</option>';
    } else {
      clients.forEach(c => {
        html += `<option value="${c.id}">${c.first_name} ${c.last_name} (${c.email})</option>`;
      });
    }
    select.innerHTML = html;
  } catch (err) {
    console.error("Error loading billing clients:", err);
  }
};

window.loadBillingClientOffers = async function () {
  const select = document.getElementById("billingClientSelect");
  const container = document.getElementById("billingOffersContainer");
  const list = document.getElementById("billingOffersList");

  if (!select.value) {
    container.style.display = "none";
    return;
  }

  const techData = JSON.parse(localStorage.getItem("currentUser"));
  container.style.display = "flex";
  list.innerHTML = "<p>Loading offers...</p>";

  try {
    const res = await fetch(`/api/technician/billing-offers?tech_id=${techData.id}&client_id=${select.value}`);
    const offers = await res.json();
    window.currentBillingOffers = offers;

    if (offers.length === 0) {
      list.innerHTML = "<p>No active offers found.</p>";
      window.calculateInvoiceTotal();
      return;
    }

    list.innerHTML = offers.map(o => {
      const isBillable = o.status === "accepted" || o.status === "ready_to_invoice";
      const badgeColor = o.status === "accepted" ? "#27ae60" : (o.status === "quoted" ? "#f39c12" : (o.status === "ready_to_invoice" ? "#17a2b8" : "#94a3b8"));

      let sum = 0;
      const validServices = o.services.filter(s => !s.is_deleted);
      validServices.forEach(s => {
        sum += (s.quoted_price || 0);
      });

      const servicesListHtml = validServices.map(s =>
        `<div style="font-size:12px; color:#555; padding-left:25px; margin-top:4px;">
           • ${s.service_name} — ${s.hours}h <strong style="color:#2563eb;">(${s.quoted_price ? s.quoted_price.toFixed(2) + ' €' : '0.00 €'})</strong>
         </div>`
      ).join("");

      return `
        <div style="border:1px solid ${isBillable ? '#cbd5e1' : '#e2e8f0'}; border-radius:8px; padding:15px; display:flex; gap:15px; background:${isBillable ? '#fff' : '#f8fafc'}; opacity:${isBillable ? '1' : '0.6'}; transition:0.2s;">
          <div style="padding-top:4px;">
            <input type="checkbox" class="invoice-offer-checkbox" value="${o.id}" data-price="${sum}" ${isBillable ? 'checked onchange="window.calculateInvoiceTotal()"' : 'disabled'} style="transform:scale(1.5);">
          </div>
          <div style="flex:1;">
            <div style="display:flex; justify-content:space-between; margin-bottom: 8px;">
              <span style="font-weight:bold; color:var(--color-csic); font-size:16px;">PO_${o.id}</span>
              <span style="background:${badgeColor}; color:white; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:bold;">${o.status.toUpperCase()}</span>
            </div>
            ${servicesListHtml}
            <div style="margin-top:10px; padding-top:10px; border-top:1px solid #e2e8f0; text-align:right;">
               Total Sub-offer: <strong style="color:#0f172a; font-size:14px;">${sum.toFixed(2)} €</strong>
            </div>
          </div>
        </div>
      `;
    }).join("");

    window.calculateInvoiceTotal();
  } catch (err) {
    list.innerHTML = `<p style="color:red;">Error fetching offers</p>`;
  }
};

window.calculateInvoiceTotal = function () {
  const checkboxes = document.querySelectorAll(".invoice-offer-checkbox:checked");
  let sum = 0;
  checkboxes.forEach(cb => {
    sum += parseFloat(cb.getAttribute("data-price") || "0");
  });

  const sumEl = document.getElementById("billingTotalSum");
  if (sumEl) sumEl.textContent = sum.toFixed(2);

  // Also hide the whole submission frame if nothing is valid to be invoiced
  const submitFrame = document.getElementById("billingSubmitFrame");
  if (submitFrame) {
    if (checkboxes.length > 0) {
      submitFrame.style.display = "block";
    } else {
      submitFrame.style.display = "none";
    }
  }
};

window.submitInvoice = async function () {
  const techData = JSON.parse(localStorage.getItem("currentUser"));
  const clientId = document.getElementById("billingClientSelect").value;
  const comment = document.getElementById("billingComment").value;

  const checkboxes = document.querySelectorAll(".invoice-offer-checkbox:checked");
  const offerIds = Array.from(checkboxes).map(cb => parseInt(cb.value));

  if (!clientId || offerIds.length === 0) {
    alert("You must select at least one accepted offer to generate an invoice.");
    return;
  }

  let totalSum = 0;
  checkboxes.forEach(cb => totalSum += parseFloat(cb.getAttribute("data-price")));

  if (!confirm(`Are you sure you want to invoice ${offerIds.length} offers for a total of ${totalSum.toFixed(2)} €?\n\nThis will mark these offers as 'invoiced' and send them to the client.`)) {
    return;
  }

  try {
    const res = await fetch("/api/technician/invoices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_id: parseInt(clientId),
        technician_id: techData.id,
        offer_ids: offerIds,
        total_price: totalSum,
        comment: comment
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Could not generate invoice");
    }

    alert("Invoice generated successfully!");
    document.getElementById("billingComment").value = "";
    document.getElementById("billingClientSelect").value = "";
    document.getElementById("billingOffersContainer").style.display = "none";

    window.loadBillingClients();
    window.loadAllOffers(); // refresh arrays
    window.loadTechInvoices();
  } catch (err) {
    alert(err.message);
  }
};

// Store invoices data for the review modal
window._invoicesCache = [];


window.loadTechInvoices = async function () {
  const container = document.getElementById("techInvoicesContainer");
  if (!container) return;
  const techData = JSON.parse(localStorage.getItem("currentUser"));

  try {
    const res = await fetch("/api/technician/invoices/all");
    const invoices = await res.json();
    window._invoicesCache = invoices;

    if (invoices.length === 0) {
      container.innerHTML = "<p>No invoices have been generated yet.</p>";
      return;
    }

    container.innerHTML = invoices.map(inv => {
      const isFinished = inv.status === 'finished';
      const isOwner = inv.technician_id === techData.id;
      const clientName = inv.client_first_name ? `${inv.client_first_name} ${inv.client_last_name}` : `Client #${inv.client_id}`;
      return `
         <div style="background: ${isFinished ? '#f1f5f9' : 'white'}; border: 1px solid ${isFinished ? '#cbd5e1' : '#ccc'}; border-radius: 8px; padding: 15px; display: flex; justify-content: space-between; align-items: start;">
           <div>
             <h4 style="margin:0 0 5px 0; color:var(--color-csic);">Invoice #${inv.id}</h4>
             <p style="margin:0; font-size:13px; color:#64748b;">
               Client: <strong>${clientName}</strong> &nbsp;|&nbsp; Date: ${new Date(inv.created_at).toLocaleDateString()} | Total: <strong>${inv.total_price.toFixed(2)} €</strong>
             </p>
             <p style="margin:5px 0 0 0; font-size:13px; color:#475569;">
               Generated by: <strong>${inv.technician_first_name ? inv.technician_first_name + ' ' + inv.technician_last_name : 'Technician #' + inv.technician_id}</strong>
             </p>
           </div>
           
           <div style="display:flex; flex-direction:column; align-items:flex-end; gap:8px;">
             <span style="display:inline-block; padding:4px 10px; background:${isFinished ? '#2c3e50' : '#9b59b6'}; color:white; font-size:11px; font-weight:bold; border-radius:12px;">
               ${inv.status.toUpperCase()}
             </span>
             <div style="display:flex; gap:6px;">
               <button onclick="window.openInvoiceReview(${inv.id})" style="background:#3498db; color:white; border:none; padding:6px 12px; border-radius:4px; font-size:12px; cursor:pointer; font-weight:600;" title="View invoice details">
                 Review
               </button>
               ${!isFinished && isOwner ? `
                 <button onclick="window.finishInvoice(${inv.id})" style="background:#2c3e50; color:white; border:none; padding:6px 12px; border-radius:4px; font-size:12px; cursor:pointer;" title="Mark this invoice and its offers as FINISHED">
                   Finish Work
                 </button>
               ` : ''}
             </div>
           </div>
         </div>
       `;
    }).join('');

  } catch (err) {
    container.innerHTML = `<p style="color:red;">Error loading invoices history.</p>`;
  }
};

window.openInvoiceReview = function (invoiceId) {
  const inv = (window._invoicesCache || []).find(i => i.id === invoiceId);
  if (!inv) return;

  const existing = document.getElementById("invoiceReviewModal");
  if (existing) existing.remove();

  const isFinished = inv.status === 'finished';
  const clientName = inv.client_first_name ? `${inv.client_first_name} ${inv.client_last_name}` : `Client #${inv.client_id}`;
  const techName = inv.technician_first_name ? `${inv.technician_first_name} ${inv.technician_last_name}` : `Technician #${inv.technician_id}`;
  const statusColor = isFinished ? '#2c3e50' : '#9b59b6';

  const offersHtml = (inv.offers || []).map(offer => {
    const offerTotal = (offer.services || []).reduce((sum, s) => sum + (s.quoted_price || 0), 0);
    const servicesHtml = (offer.services || []).map(s => `
      <tr style="border-bottom:1px solid #f1f5f9;">
        <td style="padding:8px 10px; font-size:13px;"><strong>${s.service_name}</strong></td>
        <td style="padding:8px 10px; font-size:13px; color:#555;">${s.hours}h</td>
        <td style="padding:8px 10px; font-size:13px; color:#3b82f6; font-weight:600;">${s.quoted_price != null ? s.quoted_price.toFixed(2) + ' €' : '—'}</td>
        <td style="padding:8px 10px; font-size:12px; color:#64748b;">${s.technician ? s.technician.first_name + ' ' + s.technician.last_name : '<em style="color:#aaa;">Unassigned</em>'}</td>
        <td style="padding:8px 10px; font-size:12px; color:#94a3b8; font-style:italic;">${s.comment || ''}</td>
      </tr>
    `).join('');

    return `
      <div style="border:1px solid #e2e8f0; border-radius:6px; margin-bottom:14px; overflow:hidden;">
        <div style="background:#f8fafc; padding:10px 15px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0;">
          <span style="font-weight:700; color:var(--color-csic); font-size:14px;">PO_${offer.id}</span>
          <span style="font-size:12px; color:#64748b;">${offer.created_at ? new Date(offer.created_at).toLocaleDateString() : ''}</span>
        </div>
        <table style="width:100%; border-collapse:collapse;">
          <thead>
            <tr style="text-align:left; color:#94a3b8; font-size:11px; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid #e2e8f0;">
              <th style="padding:8px 10px;">Service</th>
              <th style="padding:8px 10px;">Hours</th>
              <th style="padding:8px 10px;">Price</th>
              <th style="padding:8px 10px;">Technician</th>
              <th style="padding:8px 10px;">Notes</th>
            </tr>
          </thead>
          <tbody>${servicesHtml}</tbody>
        </table>
        ${offer.technician_comment ? `
          <div style="padding:8px 15px; background:#fffbeb; border-top:1px solid #fde68a; font-size:12px; color:#92400e;">
            <strong>Message to client:</strong> ${offer.technician_comment}
          </div>
        ` : ''}
        <div style="padding:8px 15px; background:#f8fafc; border-top:1px solid #e2e8f0; text-align:right; font-size:13px; color:#1e293b; font-weight:600;">
          Offer subtotal: ${offerTotal.toFixed(2)} €
        </div>
      </div>
    `;
  }).join('');

  const modal = document.createElement("div");
  modal.id = "invoiceReviewModal";
  modal.style.cssText = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.55); z-index:9999; display:flex; align-items:center; justify-content:center; padding:20px; box-sizing:border-box;";
  modal.onclick = (e) => { if (e.target === modal) modal.remove(); };

  modal.innerHTML = `
    <div style="background:white; border-radius:10px; width:100%; max-width:780px; max-height:88vh; overflow-y:auto; box-shadow:0 20px 60px rgba(0,0,0,0.25);">
      <!-- Header -->
      <div style="background:linear-gradient(135deg, var(--color-csic, #1a5276) 0%, #2980b9 100%); padding:20px 25px; border-radius:10px 10px 0 0; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <h2 style="margin:0; color:white; font-size:18px;">Invoice #${inv.id}</h2>
          <span style="display:inline-block; margin-top:5px; padding:3px 10px; background:${statusColor}; color:white; font-size:11px; font-weight:bold; border-radius:10px;">${inv.status.toUpperCase()}</span>
        </div>
        <button onclick="document.getElementById('invoiceReviewModal').remove()" style="background:rgba(255,255,255,0.2); border:none; color:white; width:32px; height:32px; border-radius:50%; font-size:18px; cursor:pointer; line-height:1; display:flex; align-items:center; justify-content:center;">&times;</button>
      </div>

      <!-- Summary bar -->
      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0; border-bottom:1px solid #e2e8f0;">
        <div style="padding:15px 20px; border-right:1px solid #e2e8f0;">
          <div style="font-size:11px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:3px;">Client</div>
          <div style="font-weight:700; color:#1e293b;">${clientName}</div>
          <div style="font-size:12px; color:#64748b;">${inv.client_email || ''}</div>
          ${inv.client_entity ? `<div style="font-size:11px; color:#94a3b8; margin-top:2px;">${inv.client_entity}</div>` : ''}
        </div>
        <div style="padding:15px 20px; border-right:1px solid #e2e8f0;">
          <div style="font-size:11px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:3px;">Generated by</div>
          <div style="font-weight:700; color:#1e293b;">${techName}</div>
          <div style="font-size:12px; color:#64748b;">${new Date(inv.created_at).toLocaleString()}</div>
        </div>
        <div style="padding:15px 20px; text-align:right;">
          <div style="font-size:11px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:3px;">Total</div>
          <div style="font-size:26px; font-weight:800; color:#1e293b;">${inv.total_price.toFixed(2)} €</div>
          <div style="font-size:12px; color:#64748b;">${(inv.offers || []).length} offer(s)</div>
        </div>
      </div>

      <!-- Offers & services -->
      <div style="padding:20px 25px;">
        <h4 style="margin:0 0 14px 0; font-size:13px; color:#64748b; text-transform:uppercase; letter-spacing:0.05em;">Included Offers & Services</h4>
        ${offersHtml || '<p style="color:#94a3b8; font-size:13px;">No offers linked to this invoice.</p>'}
      </div>

      ${inv.comment ? `
        <div style="margin:0 25px 20px 25px; padding:12px 15px; background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; font-size:13px; color:#0369a1;">
          <strong>Invoice comment:</strong> ${inv.comment}
        </div>
      ` : ''}

      <!-- Footer -->
      <div style="padding:15px 25px; border-top:1px solid #e2e8f0; text-align:right;">
        <button onclick="document.getElementById('invoiceReviewModal').remove()" style="background:#64748b; color:white; border:none; padding:8px 20px; border-radius:6px; font-size:13px; font-weight:600; cursor:pointer;">Close</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
};

window.finishInvoice = async function (invoiceId) {
  if (!confirm("Are you sure you want to finish this invoice? This will mark all its offers as 'finished' and they will be locked.")) {
    return;
  }

  try {
    const res = await fetch(`/api/technician/invoices/${invoiceId}/finish`, {
      method: "POST"
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Error finishing invoice");
    }

    alert("Invoice and underlying offers successfully marked as FINISHED!");
    window.loadTechInvoices();
    window.loadAllOffers(); // Refresh the main dashboard cards completely
  } catch (err) {
    alert(err.message);
  }
};

// Live auto-refresh: poll data every 15 seconds silently
// Detects if the Review Panel is open to avoid interrupting active editing
function isReviewPanelOpen() {
  return !!document.querySelector(".btn-back");
}

// --- DOWNLOAD OFFER DOCUMENT ---
window.downloadOfferDocument = async function (offerId) {
  try {
    const response = await fetch(`/api/technician/offers/${offerId}/document`);
    if (!response.ok) {
      const err = await response.json();
      alert("Error: " + (err.detail || "Could not generate document"));
      return;
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    // Extract filename from Content-Disposition header or use default
    const disposition = response.headers.get("Content-Disposition");
    const match = disposition && disposition.match(/filename="?(.+?)"?$/);
    a.download = match ? match[1] : `Oferta_${offerId}.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Download error:", err);
    alert("Network error downloading document.");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    if (window.loadTechInvoices) window.loadTechInvoices();
  }, 1000);

  setInterval(async () => {
    try {
      // Skip offer reload if technician is currently editing a review panel
      if (!isReviewPanelOpen()) {
        if (window.loadAllOffers) await window.loadAllOffers();
      }
      if (window.loadTechInvoices) await window.loadTechInvoices();
      if (window.loadBillingClients) await window.loadBillingClients();
    } catch (e) { /* silent fail */ }
  }, 15000);
});

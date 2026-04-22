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

document.addEventListener("DOMContentLoaded", async () => {
  const currentUser = JSON.parse(localStorage.getItem("currentUser"));

  // 1. SECURITY: Clients only
  if (!currentUser || currentUser.role !== "client") {
    window.location.href = "/login";
    return;
  }

  // 2. UI: USER BAR
  const displayName =
    currentUser.nickname ||
    `${currentUser.first_name || ""} ${currentUser.last_name || ""}`.trim() ||
    "Researcher";
  document.getElementById("userNameBar").textContent = displayName;

  if (currentUser.profilePicture) {
    document.getElementById("userIcon").src = currentUser.profilePicture;
  }

  // 3. DROPDOWN MENU
  const profileContainer = document.getElementById("profileContainer");
  const dropdownMenu = document.getElementById("dropdownMenu");

  if (profileContainer && dropdownMenu) {
    profileContainer.addEventListener("click", (e) => {
      e.stopPropagation();
      dropdownMenu.classList.toggle("hidden");
    });
    document.addEventListener("click", () =>
      dropdownMenu.classList.add("hidden"),
    );
  }

  // 4. NAVIGATION BUTTONS
  document.getElementById("logOut")?.addEventListener("click", () => {
    localStorage.removeItem("currentUser");
    window.location.href = "/login";
  });

  document.getElementById("editProfile")?.addEventListener("click", () => {
    window.location.href = "/editar-cliente";
  });

  // 5. LOAD SERVICE CATALOG
  async function loadCatalog() {
    const grid = document.getElementById("servicesGrid");
    try {
      const response = await fetch("/api/catalog");
      const catalog = await response.json();

      grid.style.display = "flex";
      grid.style.flexDirection = "column";
      grid.style.gap = "10px";
      grid.innerHTML = "";

      catalog.forEach((item) => {
        const fila = document.createElement("div");
        fila.style.cssText =
          "display:flex; border:1px solid #ccc; border-radius:4px; background:#fff; align-items:stretch; min-height:55px;";

        fila.innerHTML = `
                    <div class="btn-desplegar" style="flex:0 0 40%; display:flex; justify-content:space-between; align-items:center; padding:0 15px; background:#f8f9fa; border-right:1px solid #eee; cursor:pointer;">
                        <span class="nombre-servicio" style="font-weight:600; font-size:14px;">${item.name}</span>
                        <span class="icono-mas">+</span>
                    </div>
                    <div class="formulario-horas" style="display:none; flex:1; align-items:center; padding:0 15px; gap:15px; background:#fff;">
                        <label style="font-size:12px; font-weight:bold;">HOURS:</label>
                        <input type="number" step="0.5" min="0" class="input-horas" style="width:60px; padding:5px;">
                        <label style="font-size:12px; font-weight:bold;">NOTE:</label>
                        <input type="text" class="input-comentario" placeholder="Optional..." style="flex-grow:1; padding:5px;">
                    </div>
                `;
        grid.appendChild(fila);
      });

      document.querySelectorAll(".btn-desplegar").forEach((btn) => {
        btn.addEventListener("click", function () {
          const form = this.nextElementSibling;
          const icon = this.querySelector(".icono-mas");
          const isOpen = form.style.display === "flex";
          form.style.display = isOpen ? "none" : "flex";
          icon.textContent = isOpen ? "+" : "-";
          this.style.background = isOpen ? "#f8f9fa" : "#e9ecef";
        });
      });
    } catch (e) {
      grid.innerHTML = "<p>Error loading catalog.</p>";
    }
  }

  // 6. LOAD MY OFFERS (ADVANCED ASSIGNMENT LOGIC)
  window.loadMyRequests = async function () {
    const list = document.getElementById("requestList");
    try {
      const response = await fetch(
        `/api/client/my-offers?email=${encodeURIComponent(currentUser.email)}`,
      );
      const offers = await response.json();

      list.innerHTML = "";
      list.style.display = "grid";
      list.style.gridTemplateColumns = "repeat(auto-fill, minmax(400px, 1fr))"; // 3 por línea en pantallas grandes
      list.style.gap = "25px";
      list.style.alignItems = "start";
      list.style.marginBottom = "30px";
      if (offers.length === 0) {
        list.innerHTML =
          "<p style='text-align:center; padding:20px;'>You have no offers yet.</p>";
        return;
      }

      offers
        .sort((a, b) => b.id - a.id)
        .forEach((offer) => {
          const div = document.createElement("div");
          div.style.cssText =
            "border:1px solid #e2e8f0; padding:24px; border-radius:12px; background:#fff; position:relative; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); transition: transform 0.2s, box-shadow 0.2s;";
          div.onmouseover = () => { div.style.transform = 'translateY(-4px)'; div.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)'; };
          div.onmouseout = () => { div.style.transform = 'translateY(0)'; div.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)'; };

          const statusColors = {
            requested: "#17a2b8",
            quoted: "#f39c12",
            accepted: "#28a745",
            invoiced: "#9b59b6",
            finished: "#2c3e50",
          };
          const color = statusColors[offer.status] || "#666";

          div.innerHTML = `
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid #eee; padding-bottom:10px; margin-bottom:10px;">
              <strong style="color:#004a8f;">OFFER #${offer.id}</strong>
              <span style="background:${color}; color:white; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:bold;">${offer.status.toUpperCase()}</span>
            </div>
            <div style="font-size:13px; color:#555; margin-bottom:10px;">Date: ${new Date(offer.created_at).toLocaleDateString()}</div>

            ${offer.status === 'quoted' ? `
              <!-- QUOTED: tabla de precios destacada -->
              <div style="background:#f0f7ff; border:2px solid #3498db; border-radius:8px; padding:15px; margin-bottom:15px;">
                <h4 style="margin:0 0 12px 0; color:#2563eb; font-size:14px; display:flex; align-items:center; gap:8px;">
                  QUOTATION
                </h4>
                <table style="width:100%; border-collapse:collapse; font-size:13px;">
                  <thead>
                    <tr style="border-bottom:2px solid #c8d8ff; color:#2563eb;">
                      <th style="padding:6px 8px; text-align:left; font-weight:600;">Service</th>
                      <th style="padding:6px 8px; text-align:right; font-weight:600;">Hours</th>
                      <th style="padding:6px 8px; text-align:right; font-weight:600;">Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${offer.services.map(s => {
                      if (s.is_deleted && s.added_by_technician) return '';
                      const isDel = s.is_deleted;
                      const isAdded = s.added_by_technician;
                      const isEdited = !isDel && !isAdded && s.original_hours !== null && parseFloat(s.hours) !== parseFloat(s.original_hours);

                      const colorStyle = isDel ? 'color: #94a3b8;' : 'color:#333;';
                      let label = '';
                      if (isDel) {
                         label = ' <span style="color:#ef4444; font-size:11px; font-weight:bold; text-decoration:none;">(Deleted by technician)</span>';
                      } else if (isAdded) {
                         label = ' <span style="color:#10b981; font-size:11px; font-weight:bold;">(Added by technician)</span>';
                      } else if (isEdited) {
                         label = ' <span style="color:#f59e0b; font-size:11px; font-weight:bold;">(Edited by technician)</span>';
                      }
                      
                      const nameDisplay = isDel ? `<span style="text-decoration:line-through;">${s.service_name}</span>` : s.service_name;
                      let hoursDisplay = isDel ? `<span style="text-decoration:line-through;">${s.hours}h</span>` : `${s.hours}h`;
                      
                      if (isEdited) {
                          hoursDisplay = `<span style="text-decoration:line-through; color:#94a3b8; font-size:11px; margin-right:4px;">${s.original_hours}h</span><span style="color:#f59e0b; font-weight:bold;">${s.hours}h</span>`;
                      }

                      return `
                        <tr style="border-bottom:1px solid #dce8ff;">
                          <td style="padding:6px 8px; ${colorStyle}">${nameDisplay}${label}</td>
                          <td style="padding:6px 8px; text-align:right; color:#555;">${hoursDisplay}</td>
                          <td style="padding:6px 8px; text-align:right; font-weight:600; color:#2563eb;">
                            ${isDel ? '0.00 €' : (s.quoted_price != null ? s.quoted_price.toFixed(2) + ' €' : '—')}
                          </td>
                        </tr>
                      `;
                    }).join('')}
                  </tbody>
                  <tfoot>
                    <tr style="border-top:2px solid #3498db; background:#e8f2ff;">
                      <td colspan="2" style="padding:8px; font-weight:bold; color:#1e40af; font-size:14px;">TOTAL</td>
                      <td style="padding:8px; text-align:right; font-weight:bold; color:#1e40af; font-size:16px;">
                        ${offer.services.filter(s => !s.is_deleted).reduce((acc, s) => acc + (s.quoted_price ?? 0), 0).toFixed(2)} €
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            ` : (offer.status === 'accepted' || offer.status === 'finished' || offer.status === 'invoiced') && offer.services.some(s => s.quoted_price != null) ? `
              <!-- ACCEPTED / INVOICED / FINISHED: resumen compacto de precios -->
              <div style="background:${offer.status === 'invoiced' || offer.status === 'finished' ? '#fcf0fb' : '#f6fff8'}; border:1px solid ${offer.status === 'invoiced' || offer.status === 'finished' ? '#9b59b6' : '#28a745'}; border-radius:6px; padding:12px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                  <span style="font-size:13px; color:${offer.status === 'invoiced' || offer.status === 'finished' ? '#9b59b6' : '#1a6b33'}; font-weight:600;">${offer.status === 'invoiced' ? 'Invoiced quotation' : offer.status === 'finished' ? 'Completed work' : 'Accepted quotation'}</span>
                  <span style="font-size:16px; font-weight:bold; color:${offer.status === 'invoiced' || offer.status === 'finished' ? '#9b59b6' : '#1a6b33'};">
                    ${offer.services.filter(s => !s.is_deleted).reduce((acc, s) => acc + (s.quoted_price ?? 0), 0).toFixed(2)} € total
                  </span>
                </div>
                <ul style="margin:0; padding-left:16px; font-size:13px; color:#555;">
                  ${offer.services.map(s => {
                    if (s.is_deleted) return ''; // Don't show deleted in compact summary
                    const isAdded = s.added_by_technician;
                    const isEdited = !isAdded && s.original_hours !== null && parseFloat(s.hours) !== parseFloat(s.original_hours);
                    let hoursDisplay = `${s.hours}h`;
                    if (isEdited) {
                       hoursDisplay = `<span style="text-decoration:line-through; color:#94a3b8; font-size:11px; margin-right:4px;">${s.original_hours}h</span><span style="color:#f59e0b; font-weight:bold;">${s.hours}h</span>`;
                    }
                    const priceColor = offer.status === 'invoiced' || offer.status === 'finished' ? '#9b59b6' : '#1a6b33';
                    return `
                      <li style="margin-bottom:3px;">
                        ${s.service_name} — ${hoursDisplay}
                        ${isAdded ? '<small style="color:#10b981; font-weight:bold; margin-left:4px;">(Added by technician)</small>' : ''}
                        ${isEdited ? '<small style="color:#f59e0b; font-weight:bold; margin-left:4px;">(Edited by technician)</small>' : ''}
                        ${s.quoted_price != null ? `<span style="color:${priceColor}; font-weight:600; margin-left:4px;">(${s.quoted_price.toFixed(2)} €)</span>` : ''}
                      </li>
                    `;
                  }).join('')}
                </ul>
              </div>
            ` : `
              <!-- REQUESTED: lista simple sin precios -->
              <ul style="padding-left:15px; font-size:14px; margin-bottom:10px;">
                ${offer.services.map(s => `<li><strong>${s.service_name}</strong>: ${s.hours}h ${s.comment ? `<br><i style="color:#888;">"${s.comment}"</i>` : ''}</li>`).join('')}
              </ul>
            `}

            ${offer.technician_comment ? `
              <div style="background:#fff8e1; border-left:4px solid #f39c12; padding:10px; margin-top:5px; font-size:13px; word-break: break-word; overflow-wrap: anywhere;">
                <strong>Technician's note:</strong> ${offer.technician_comment}
              </div>
            ` : ''}

            ${offer.status === 'quoted' ? `
              <button onclick="window.acceptQuotedOffer(${offer.id})" style="width:100%; margin-top:15px; background:#28a745; color:white; border:none; padding:12px; border-radius:4px; font-weight:bold; cursor:pointer; font-size:14px;">
                ACCEPT QUOTATION AND CONFIRM WORK
              </button>
            ` : ''}
          `;
          list.appendChild(div);
        });
    } catch (e) {
      console.error("Error loading history", e);
    }
  };

  // 7. SUBMIT NEW REQUEST
  document
    .getElementById("btnSendRequest")
    ?.addEventListener("click", async () => {
      const requestedServices = [];
      document.querySelectorAll(".formulario-horas").forEach((form) => {
        if (form.style.display === "flex") {
          const hours = parseFloat(form.querySelector(".input-horas").value);
          if (hours > 0) {
            requestedServices.push({
              service_name:
                form.previousElementSibling.querySelector(".nombre-servicio")
                  .textContent,
              hours: hours,
              comment: form.querySelector(".input-comentario").value,
            });
          }
        }
      });

      if (requestedServices.length === 0)
        return alert("Select at least one service with hours.");

      const res = await fetch("/api/client/offers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_email: currentUser.email,
          services: requestedServices,
        }),
      });

      if (res.ok) {
        alert("Request sent successfully.");
        location.reload();
      }
    });

  // 8. ACCEPTANCE LOGIC
  window.acceptQuotedOffer = async function (offerId) {
    if (
      !confirm("Do you confirm that you accept the quotation and the indicated hours?")
    )
      return;

    const res = await fetch(
      `/api/technician/offers/${offerId}?new_status=accepted`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
      },
    );

    if (res.ok) {
      alert("Offer accepted. The technician has been notified.");
      window.loadMyRequests();
    }
  };

  // 9. INVOICES / BILLING
  window.loadClientInvoices = async function () {
    const list = document.getElementById("invoiceList");
    if (!list) return;
    
    try {
      const response = await fetch(`/api/client/invoices?email=${encodeURIComponent(currentUser.email)}`);
      const invoices = await response.json();
      
      if (invoices.length === 0) {
        list.innerHTML = "<p style='text-align:center; color:#666;'>No invoices generated yet.</p>";
        return;
      }
      
      list.innerHTML = invoices.map(inv => {
        let detailsHtml = '';
        if (inv.offers && inv.offers.length > 0) {
           detailsHtml = '<div style="margin-top:15px; display:flex; flex-direction:column; gap:10px;">';
           inv.offers.forEach(o => {
               let offerSum = 0;
               let srvsHtml = '';
               o.services.filter(s => !s.is_deleted).forEach(s => {
                   offerSum += (s.quoted_price || 0);
                   let unitPriceInfo = '';
                   if (s.hours > 0 && s.quoted_price) {
                       const unit = s.quoted_price / s.hours;
                       unitPriceInfo = `<span style="color:#94a3b8; margin-left:5px;">(${unit.toFixed(2)} € / h)</span>`;
                   }
                   srvsHtml += `<div style="display:flex; justify-content:space-between; font-size:12px; color:#64748b; margin-top:3px; padding-left:10px;">
                                  <span>• ${s.service_name} — ${s.hours}h ${unitPriceInfo}</span>
                                  <span>${s.quoted_price ? s.quoted_price.toFixed(2) + ' €' : '0.00 €'}</span>
                                </div>`;
               });
               
               detailsHtml += `
                 <div style="border:1px dashed #cbd5e1; border-radius:6px; padding:10px; background:#f8fafc;">
                    <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:13px; color:#334155; margin-bottom:5px;">
                       <span>PO_${o.id}</span>
                       <span style="color:#0f172a;">${offerSum.toFixed(2)} €</span>
                    </div>
                    ${srvsHtml}
                 </div>
               `;
           });
           detailsHtml += '</div>';
        }
        
        return `
          <div style="border:1px solid ${inv.status === 'finished' ? '#cbd5e1' : '#ccc'}; border-radius:8px; padding:20px; background:${inv.status === 'finished' ? '#f8fafc' : '#fff'}; display:flex; flex-direction:column; gap:10px;">
            <div style="display:flex; justify-content:space-between; border-bottom:2px solid #eee; padding-bottom:10px;">
              <h3 style="margin:0; color:var(--color-csic);">Invoice #${inv.id}</h3>
              <span style="background:${inv.status === 'finished' ? '#2c3e50' : '#9b59b6'}; color:white; padding:4px 12px; border-radius:12px; font-weight:bold; font-size:12px;">${inv.status.toUpperCase()}</span>
            </div>
            
            <div style="display:flex; justify-content:space-between; font-size:14px; color:#555;">
              <span><strong>Date:</strong> ${new Date(inv.created_at).toLocaleDateString()}</span>
            </div>
            
            ${detailsHtml}
            
            ${inv.comment ? `
              <div style="background:#f8fafc; padding:10px; border-left:4px solid #3b82f6; font-size:14px; margin-top:5px; border-radius:4px;">
                <strong>Technician's Note:</strong><br>${inv.comment}
              </div>
            ` : ''}
            
            <div style="text-align:right; border-top:1px solid #eee; padding-top:10px; margin-top:5px;">
              <span style="font-size:18px; color:#0f172a;"><strong>Total: ${inv.total_price.toFixed(2)} €</strong></span>
            </div>
          </div>
        `;
      }).join('');
      
    } catch (e) {
      list.innerHTML = "<p style='color:red;'>Error fetching invoices</p>";
    }
  };


  await loadCatalog();
  await window.loadMyRequests();
  await window.loadClientInvoices();
  
  // Live auto-refresh: silently re-fetch data every 15 seconds
  setInterval(async () => {
    try {
      await window.loadMyRequests();
      await window.loadClientInvoices();
    } catch(e) { /* silent fail */ }
  }, 15000);
});

// Global function for tabs
window.openTab = function (evt, tabName) {
  const contents = document.getElementsByClassName("tab-content");
  for (let i = 0; i < contents.length; i++) {
    contents[i].style.display = "none";
    contents[i].classList.remove("active");
  }
  const btns = document.getElementsByClassName("tab-btn");
  for (let i = 0; i < btns.length; i++) {
    btns[i].classList.remove("active");
  }
  document.getElementById(tabName).style.display = "block";
  document.getElementById(tabName).classList.add("active");
  evt.currentTarget.classList.add("active");
};

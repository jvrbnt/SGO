document.addEventListener("DOMContentLoaded", async () => {
  const currentUser = JSON.parse(localStorage.getItem("currentUser"));

  // 1. SEGURIDAD: Solo clientes
  if (!currentUser || currentUser.role !== "client") {
    window.location.href = "/login";
    return;
  }

  // 2. UI: BARRA DE USUARIO
  const displayName =
    currentUser.nickname ||
    `${currentUser.first_name || ""} ${currentUser.last_name || ""}`.trim() ||
    "Investigador";
  document.getElementById("userNameBar").textContent = displayName;

  if (currentUser.profilePicture) {
    document.getElementById("userIcon").src = currentUser.profilePicture;
  }

  // 3. MENÚ DESPLEGABLE
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

  // 4. BOTONES DE NAVEGACIÓN
  document.getElementById("logOut")?.addEventListener("click", () => {
    localStorage.removeItem("currentUser");
    window.location.href = "/login";
  });

  document.getElementById("editProfile")?.addEventListener("click", () => {
    window.location.href = "/editar-cliente";
  });

  // 5. CARGAR CATÁLOGO DE SERVICIOS
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
                        <label style="font-size:12px; font-weight:bold;">HORAS:</label>
                        <input type="number" step="0.5" min="0" class="input-horas" style="width:60px; padding:5px;">
                        <label style="font-size:12px; font-weight:bold;">NOTA:</label>
                        <input type="text" class="input-comentario" placeholder="Opcional..." style="flex-grow:1; padding:5px;">
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
      grid.innerHTML = "<p>Error cargando catálogo.</p>";
    }
  }

  // 6. CARGAR MIS OFERTAS (CON LÓGICA DE VÍCTOR)
  window.loadMyRequests = async function () {
    const list = document.getElementById("requestList");
    try {
      const response = await fetch(
        `/api/client/my-offers?email=${encodeURIComponent(currentUser.email)}`,
      );
      const offers = await response.json();

      list.innerHTML = "";
      if (offers.length === 0) {
        list.innerHTML =
          "<p style='text-align:center; padding:20px;'>No tienes ofertas aún.</p>";
        return;
      }

      offers
        .sort((a, b) => b.id - a.id)
        .forEach((offer) => {
          const div = document.createElement("div");
          div.style.cssText =
            "border:1px solid #ccc; padding:20px; border-radius:8px; background:#fff; margin-bottom:15px; position:relative;";

          const statusColors = {
            requested: "#17a2b8",
            quoted: "#f39c12",
            accepted: "#28a745",
            finished: "#2c3e50",
          };
          const color = statusColors[offer.status] || "#666";

          div.innerHTML = `
                    <div style="display:flex; justify-content:space-between; border-bottom:1px solid #eee; padding-bottom:10px; margin-bottom:10px;">
                        <strong style="color:#004a8f;">OFERTA #${offer.id}</strong>
                        <span style="background:${color}; color:white; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:bold;">${offer.status.toUpperCase()}</span>
                    </div>
                    <div style="font-size:13px; color:#555; margin-bottom:10px;">Fecha: ${new Date(offer.created_at).toLocaleDateString()}</div>
                    
                    <ul style="padding-left:15px; font-size:14px;">
                        ${offer.services.map((s) => `<li><strong>${s.service_name}</strong>: ${s.hours}h ${s.comment ? `<br><i style="color:#888;">"${s.comment}"</i>` : ""}</li>`).join("")}
                    </ul>

                    ${
                      offer.technician_comment
                        ? `
                        <div style="background:#fff8e1; border-left:4px solid #f39c12; padding:10px; margin-top:15px; font-size:13px;">
                            <strong>Nota del técnico:</strong> ${offer.technician_comment}
                        </div>
                    `
                        : ""
                    }

                    ${
                      offer.status === "quoted"
                        ? `
                        <button onclick="window.acceptQuotedOffer(${offer.id})" style="width:100%; margin-top:15px; background:#28a745; color:white; border:none; padding:12px; border-radius:4px; font-weight:bold; cursor:pointer;">
                            ACEPTAR PRESUPUESTO Y CONFIRMAR TRABAJO
                        </button>
                    `
                        : ""
                    }
                `;
          list.appendChild(div);
        });
    } catch (e) {
      console.error("Error cargando historial", e);
    }
  };

  // 7. ENVIAR NUEVA SOLICITUD
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
        return alert("Selecciona al menos un servicio con horas.");

      const res = await fetch("/api/client/offers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_email: currentUser.email,
          services: requestedServices,
        }),
      });

      if (res.ok) {
        alert("Solicitud enviada con éxito.");
        location.reload();
      }
    });

  // 8. LÓGICA DE ACEPTACIÓN (VÍCTOR)
  window.acceptQuotedOffer = async function (offerId) {
    if (
      !confirm("¿Confirmas que aceptas el presupuesto y las horas indicadas?")
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
      alert("Oferta aceptada. El técnico ha sido notificado.");
      window.loadMyRequests();
    }
  };

  await loadCatalog();
  await window.loadMyRequests();
});

// Función global para pestañas
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

document.addEventListener("DOMContentLoaded", () => {
    const activeUser = JSON.parse(localStorage.getItem('activeUser'));
    const globalList = document.getElementById("globalRequestList");

    // Filter selectors
    const filterStatus = document.getElementById("filterStatus");
    const filterTechnician = document.getElementById("filterTechnician");
    const filterService = document.getElementById("filterService");

    if (!activeUser) {
        window.location.href = "/static/html/ServicioLogin.html";
        return;
    }

    document.getElementById("userNameBar").textContent = activeUser.nickname || activeUser.name || "Technician";
    document.getElementById("userIcon").src = activeUser.profilePicture || "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";

    function renderRequests() {
        globalList.innerHTML = "";
        const users = JSON.parse(localStorage.getItem('users')) || [];

        // Current filter values
        const statusFilter = filterStatus.value;
        const technicianFilter = filterTechnician.value;
        const serviceFilter = filterService.value;

        users.forEach(u => {
            if (u.requests) {
                u.requests.forEach((r, index) => {
                    const status = r.status || "Requested";
                    const technician = r.technician || null;
                    const service = r.service;

                    // Apply filters
                    let matchesStatus = (statusFilter === "todos" || status === statusFilter);
                    let matchesService = (serviceFilter === "todos" || service === serviceFilter);
                    let matchesTechnician = true;

                    if (technicianFilter === "sin_asignar") {
                        matchesTechnician = (technician === null);
                    } else if (technicianFilter === "mis_peticiones") {
                        matchesTechnician = (technician === activeUser.name);
                    }

                    // If all 3 filters match, render it
                    if (matchesStatus && matchesService && matchesTechnician) {
                        const card = document.createElement("div");
                        card.className = `request-card ${technician ? 'reserved' : ''}`;

                        card.innerHTML = `
                            <div>
                                <span class="status-badge">${status}</span>
                                <strong style="color: var(--color-csic); font-size: 16px;">${service}</strong><br>
                                <p style="margin: 5px 0; font-size: 13px; color: #666;">
                                    👤 <b>User:</b> ${u.name} ${u.lastName}<br>
                                    📅 <b>Date:</b> ${r.date}<br>
                                    ⏱️ <b>Hours:</b> ${r.hours}h
                                </p>
                                <p style="font-size: 12px; color: #444; background: #f9f9f9; padding: 5px; border-radius: 4px;">
                                    💬 ${r.comment || 'No comments'}
                                </p>
                            </div>
                            ${technician
                                ? `<div class="assigned-technician">✅ Reserved by: ${technician}</div>`
                                : `<button class="btn-reserve" data-email="${u.email}" data-idx="${index}">Reserve</button>`
                            }
                        `;
                        globalList.appendChild(card);
                    }
                });
            }
        });

        // Reserve button events
        document.querySelectorAll(".btn-reserve").forEach(btn => {
            btn.addEventListener("click", function() {
                assignRequest(this.dataset.email, this.dataset.idx);
            });
        });
    }

    function assignRequest(email, idx) {
        let users = JSON.parse(localStorage.getItem('users')) || [];
        const uIdx = users.findIndex(u => u.email === email);

        if (uIdx !== -1) {
            users[uIdx].requests[idx].status = "Accepted";
            users[uIdx].requests[idx].technician = activeUser.name;
            localStorage.setItem('users', JSON.stringify(users));
            renderRequests();
        }
    }

    // Filter change listeners
    filterStatus.addEventListener("change", renderRequests);
    filterTechnician.addEventListener("change", renderRequests);
    filterService.addEventListener("change", renderRequests);

    // Dropdown menu and navigation
    const profileContainer = document.getElementById("profileContainer");
    const dropdownMenu = document.getElementById("dropdownMenu");
    profileContainer.addEventListener("click", (e) => { e.stopPropagation(); dropdownMenu.classList.toggle("hidden"); });
    document.addEventListener("click", () => dropdownMenu.classList.add("hidden"));

    document.getElementById("logOut").addEventListener("click", () => {
        localStorage.removeItem('activeUser');
        window.location.href = "/static/html/ServicioLogin.html";
    });

    document.getElementById("editProfile").addEventListener("click", () => {
        window.location.href = "/static/html/servicioEditT.html";
    });

    renderRequests();
});
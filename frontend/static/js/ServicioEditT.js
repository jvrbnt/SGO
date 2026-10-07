document.addEventListener("DOMContentLoaded", () => {
    // Use currentUser to be consistent with Technician flow
    const techData = JSON.parse(localStorage.getItem('currentUser'));
    const authFetch = (resource, config = {}) => {
        const token = localStorage.getItem("authToken");
        return fetch(resource, {
            ...config,
            headers: {
                ...(config.headers || {}),
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
        });
    };

    // Validate technician and session
    if (!techData || techData.role !== "technician") {
        window.location.href = "/login";
        return;
    }

    // --- UPDATE TOP BAR ---
    const updateBar = () => {
        const name = techData.nickname || techData.display_name || `${techData.first_name} ${techData.last_name}`;
        document.getElementById("userNameBar").textContent = name;
        document.getElementById("userIcon").src = window.avatarFor(techData);
    };
    updateBar();

    // --- LOAD FORM DATA ---
    document.getElementById("photoPreview").src = window.avatarFor(techData);
    document.getElementById("editNickname").value = techData.nickname || techData.display_name || "";

    // --- SAVE CHANGES ---
    document.getElementById("btnSaveChanges").addEventListener("click", async () => {
        try {
            const res = await authFetch("/api/me", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    display_name: document.getElementById("editNickname").value.trim() || null,
                }),
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(Array.isArray(data.detail) ? "Invalid profile data." : (data.detail || "Could not update profile"));
            }

            data.nickname = data.display_name;
            localStorage.setItem('currentUser', JSON.stringify(data));
            showToast("Technician profile updated successfully!", "success");
            window.location.reload();
        } catch (err) {
            showToast(err.message || "Could not update profile.", "error");
        }
    });

    // --- NAVIGATION AND MENU ---
    const profileContainer = document.getElementById("profileContainer");
    const dropdownMenu = document.getElementById("dropdownMenu");

    profileContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle("hidden");
    });

    document.addEventListener("click", () => dropdownMenu.classList.add("hidden"));

    document.getElementById("goToServices").addEventListener("click", () => {
        window.location.href = "/tecnico";
    });

    document.getElementById("logOut").addEventListener("click", () => {
        localStorage.removeItem('currentUser');
        localStorage.removeItem('authToken');
        window.location.href = "/login";
    });
});

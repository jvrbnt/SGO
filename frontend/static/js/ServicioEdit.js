document.addEventListener("DOMContentLoaded", () => {
    const currentUser = JSON.parse(localStorage.getItem("currentUser"));
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

    // Security: Redirect if no user is found
    if (!currentUser) {
        window.location.href = "/login";
        return;
    }

    // --- UI ELEMENTS ---
    const userIconBar = document.getElementById("userIcon");
    const userNameBar = document.getElementById("userNameBar");
    const photoPreview = document.getElementById("photoPreview");
    const editNickname = document.getElementById("editNickname");
    const editEntity = document.getElementById("editEntity");
    const internalFields = document.getElementById("internalFields");

    // Function to update visual profile elements
    const updateUI = (user) => {
        const displayName = user.nickname || user.display_name || `${user.first_name || ""} ${user.last_name || ""}`.trim() || "User";
        userNameBar.textContent = displayName;
        const photo = window.avatarFor(user);
        userIconBar.src = photo;
        photoPreview.src = photo;
    };

    // --- INITIAL DATA LOAD ---
    updateUI(currentUser);
    editNickname.value = currentUser.nickname || currentUser.display_name || "";
    editEntity.value = currentUser.entity || "CSIC";

    const toggleInternal = (val) => {
        if (val === "Internal") {
            internalFields.classList.remove("hidden-form");
        } else {
            internalFields.classList.add("hidden-form");
        }
    };
    toggleInternal(currentUser.entity);

    if (currentUser.entity === "Internal") {
        document.getElementById("editGroup").value = currentUser.grupo || currentUser.group || "";
    }

    editEntity.addEventListener("change", (e) => toggleInternal(e.target.value));

    // --- DROPDOWN MENU LOGIC ---
    const profileContainer = document.getElementById("profileContainer");
    const dropdownMenu = document.getElementById("dropdownMenu");

    profileContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle("hidden");
    });

    // Close the menu if clicked outside
    document.addEventListener("click", () => {
        dropdownMenu.classList.add("hidden");
    });

    // --- MENU BUTTONS ---
    document.getElementById("goToServices").addEventListener("click", () => {
        window.location.href = "/cliente";
    });

    document.getElementById("logOut").addEventListener("click", () => {
        localStorage.removeItem("currentUser");
        localStorage.removeItem("authToken");
        window.location.href = "/login";
    });

    // --- SAVE CHANGES ---
    document.getElementById("btnSaveChanges").addEventListener("click", async () => {
        const entity = editEntity.value;
        const nickname = editNickname.value.trim();
        const payload = {
            display_name: nickname || null,
            entity,
            grupo: null,
        };

        if (entity === "Internal") {
            payload.grupo = document.getElementById("editGroup").value;
        }

        try {
            const response = await authFetch("/api/me", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(Array.isArray(data.detail) ? "Invalid profile data." : (data.detail || "Could not update profile"));
            }

            data.nickname = data.display_name;
            localStorage.setItem("currentUser", JSON.stringify(data));
            showToast("Profile updated successfully!", "success");
            updateUI(data);
        } catch (err) {
            showToast(err.message || "Could not update profile.", "error");
        }
    });
});

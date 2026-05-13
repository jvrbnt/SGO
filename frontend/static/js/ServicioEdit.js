document.addEventListener("DOMContentLoaded", () => {
    const DEFAULT_PHOTO = "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";
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
        const photo = user.profilePicture || user.profile_picture || DEFAULT_PHOTO;
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
        document.getElementById("editIP").value = currentUser.investigador_principal || currentUser.ip || "";
        document.getElementById("editInternalAccount").value = currentUser.cuenta_interna || currentUser.account || "";
        document.getElementById("editProject").value = currentUser.codigo_proyecto || currentUser.project || "";
    }

    // --- PHOTO MANAGEMENT ---
    const inputPhotoFile = document.getElementById("inputPhotoFile");
    let currentPhotoBase64 = currentUser.profilePicture || currentUser.profile_picture || DEFAULT_PHOTO;

    document.getElementById("btnChangePhoto").addEventListener("click", () => inputPhotoFile.click());
    
    document.getElementById("btnRemovePhoto").addEventListener("click", () => {
        currentPhotoBase64 = DEFAULT_PHOTO;
        photoPreview.src = DEFAULT_PHOTO;
    });

    inputPhotoFile.addEventListener("change", function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                photoPreview.src = e.target.result;
                currentPhotoBase64 = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

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
            profile_picture: currentPhotoBase64,
            entity,
            investigador_principal: null,
            cuenta_interna: null,
            codigo_proyecto: null,
            grupo: null,
        };

        if (entity === "Internal") {
            payload.grupo = document.getElementById("editGroup").value;
            payload.investigador_principal = document.getElementById("editIP").value;
            payload.cuenta_interna = document.getElementById("editInternalAccount").value;
            payload.codigo_proyecto = document.getElementById("editProject").value;
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

            data.profilePicture = data.profile_picture;
            data.nickname = data.display_name;
            localStorage.setItem("currentUser", JSON.stringify(data));
            showToast("Profile updated successfully!", "success");
            updateUI(data);
        } catch (err) {
            showToast(err.message || "Could not update profile.", "error");
        }
    });
});

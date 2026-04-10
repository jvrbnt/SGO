document.addEventListener("DOMContentLoaded", () => {
    const DEFAULT_PHOTO = "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";
    const currentUser = JSON.parse(localStorage.getItem("currentUser"));

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
        const displayName = user.nickname || `${user.first_name || ""} ${user.last_name || ""}`.trim() || "User";
        userNameBar.textContent = displayName;
        const photo = user.profilePicture || DEFAULT_PHOTO;
        userIconBar.src = photo;
        photoPreview.src = photo;
    };

    // --- INITIAL DATA LOAD ---
    updateUI(currentUser);
    editNickname.value = currentUser.nickname || "";
    editEntity.value = currentUser.entity || "CSIC";

    const toggleInternal = (val) => {
        if (val === "interno(MiNa)") {
            internalFields.classList.remove("hidden-form");
        } else {
            internalFields.classList.add("hidden-form");
        }
    };
    toggleInternal(currentUser.entity);

    if (currentUser.entity === "interno(MiNa)") {
        document.getElementById("editGroup").value = currentUser.group || "";
        document.getElementById("editIP").value = currentUser.ip || "";
        document.getElementById("editInternalAccount").value = currentUser.account || "";
        document.getElementById("editProject").value = currentUser.project || "";
    }

    // --- PHOTO MANAGEMENT ---
    const inputPhotoFile = document.getElementById("inputPhotoFile");
    let currentPhotoBase64 = currentUser.profilePicture || DEFAULT_PHOTO;

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
        window.location.href = "/login";
    });

    // --- SAVE CHANGES ---
    document.getElementById("btnSaveChanges").addEventListener("click", () => {
        const entity = editEntity.value;
        const nickname = editNickname.value.trim();

        // Update currentUser object
        currentUser.nickname = nickname;
        currentUser.entity = entity;
        currentUser.profilePicture = currentPhotoBase64;

        if (entity === "interno(MiNa)") {
            currentUser.group = document.getElementById("editGroup").value;
            currentUser.ip = document.getElementById("editIP").value;
            currentUser.account = document.getElementById("editInternalAccount").value;
            currentUser.project = document.getElementById("editProject").value;
        } else {
            // Clear internal data if entity changes
            delete currentUser.group;
            delete currentUser.ip;
            delete currentUser.account;
            delete currentUser.project;
        }

        // Save to localStorage
        localStorage.setItem("currentUser", JSON.stringify(currentUser));
        
        // Sync with global user list
        let users = JSON.parse(localStorage.getItem("users")) || [];
        const idx = users.findIndex(u => u.email === currentUser.email);
        if (idx !== -1) {
            users[idx] = currentUser;
            localStorage.setItem("users", JSON.stringify(users));
        }

        alert("Profile updated successfully!");
        updateUI(currentUser); // Reflect changes immediately on the top bar
    });
});
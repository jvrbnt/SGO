document.addEventListener("DOMContentLoaded", () => {
    const activeUser = JSON.parse(localStorage.getItem('activeUser'));
    const DEFAULT_PHOTO = "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";

    if (!activeUser) {
        window.location.href = "/SGO/static/html/ServicioLogin.html";
        return;
    }

    // --- NAME IN TOP BAR ---
    const updateNameBar = () => {
        let displayName = "";
        if (activeUser.nickname && activeUser.nickname.trim() !== "") {
            displayName = activeUser.nickname;
        } else {
            const fullName = `${activeUser.name || ""} ${activeUser.lastName || ""}`.trim();
            displayName = fullName !== "" ? fullName : "User";
        }
        document.getElementById("userNameBar").textContent = displayName;
    };
    updateNameBar();

    // --- INITIAL LOAD ---
    document.getElementById("userIcon").src = activeUser.profilePicture || DEFAULT_PHOTO;
    document.getElementById("photoPreview").src = activeUser.profilePicture || DEFAULT_PHOTO;
    document.getElementById("editNickname").value = activeUser.nickname || "";
    document.getElementById("editEntity").value = activeUser.entity || "CSIC";

    const internalDiv = document.getElementById("internalFields");

    const manageInternalView = (value) => {
        if (value === "interno(MiNa)") {
            internalDiv.classList.remove("hidden-form");
        } else {
            internalDiv.classList.add("hidden-form");
        }
    };

    manageInternalView(activeUser.entity);

    // Load internal fields only if user is internal
    if (activeUser.entity === "interno(MiNa)") {
        if (activeUser.group) {
            document.getElementById("editGroup").value = activeUser.group;
        }
        document.getElementById("editIP").value = activeUser.ip || "";
        document.getElementById("editInternalAccount").value = activeUser.account || "";
        document.getElementById("editProject").value = activeUser.project || "";
    }

    // --- PHOTO MANAGEMENT ---
    const btnChangePhoto = document.getElementById("btnChangePhoto");
    const btnRemovePhoto = document.getElementById("btnRemovePhoto");
    const inputPhotoFile = document.getElementById("inputPhotoFile");
    const photoPreview = document.getElementById("photoPreview");
    let newPhotoBase64 = activeUser.profilePicture;

    btnChangePhoto.addEventListener("click", () => inputPhotoFile.click());
    btnRemovePhoto.addEventListener("click", () => {
        newPhotoBase64 = DEFAULT_PHOTO;
        photoPreview.src = DEFAULT_PHOTO;
    });

    inputPhotoFile.addEventListener("change", function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                photoPreview.src = e.target.result;
                newPhotoBase64 = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // --- ENTITY CHANGE ---
    document.getElementById("editEntity").addEventListener("change", function() {
        manageInternalView(this.value);
    });

    // --- DROPDOWN MENU ---
    const profileContainer = document.getElementById("profileContainer");
    const dropdownMenu = document.getElementById("dropdownMenu");
    profileContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle("hidden");
    });
    document.addEventListener("click", () => dropdownMenu.classList.add("hidden"));

    // --- SAVE CHANGES ---
    document.getElementById("btnSaveChanges").addEventListener("click", () => {
        const selectedEntity = document.getElementById("editEntity").value;
        const selectedGroup = document.getElementById("editGroup").value;

        // Simple validation: if internal, require a group
        if (selectedEntity === "interno(MiNa)" && selectedGroup === "") {
            alert("Please select a Research Group.");
            return;
        }

        activeUser.profilePicture = newPhotoBase64;
        activeUser.nickname = document.getElementById("editNickname").value;
        activeUser.entity = selectedEntity;

        if (activeUser.entity === "interno(MiNa)") {
            activeUser.group = selectedGroup;
            activeUser.ip = document.getElementById("editIP").value;
            activeUser.account = document.getElementById("editInternalAccount").value;
            activeUser.project = document.getElementById("editProject").value;
        }

        localStorage.setItem('activeUser', JSON.stringify(activeUser));
        let users = JSON.parse(localStorage.getItem('users')) || [];
        const index = users.findIndex(u => u.email === activeUser.email);
        if (index !== -1) {
            users[index] = activeUser;
            localStorage.setItem('users', JSON.stringify(users));
        }

        alert("Profile updated successfully");
        window.location.reload();
    });

    document.getElementById("goToServices").addEventListener("click", () => {
        window.location.href = "/SGO/static/html/ServicioUsuario.html";
    });
    document.getElementById("logOut").addEventListener("click", () => {
        localStorage.removeItem('activeUser');
        window.location.href = "/SGO/static/html/ServicioLogin.html";
    });
});
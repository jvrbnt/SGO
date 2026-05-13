document.addEventListener("DOMContentLoaded", () => {
    // Use currentUser to be consistent with Technician flow
    const techData = JSON.parse(localStorage.getItem('currentUser'));
    const DEFAULT_PHOTO = "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";
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
        document.getElementById("userIcon").src = techData.profilePicture || techData.profile_picture || DEFAULT_PHOTO;
    };
    updateBar();

    // --- LOAD FORM DATA ---
    document.getElementById("photoPreview").src = techData.profilePicture || techData.profile_picture || DEFAULT_PHOTO;
    document.getElementById("editNickname").value = techData.nickname || techData.display_name || "";

    // --- PHOTO MANAGEMENT ---
    const btnChangePhoto = document.getElementById("btnChangePhoto");
    const btnRemovePhoto = document.getElementById("btnRemovePhoto");
    const inputPhotoFile = document.getElementById("inputPhotoFile");
    const photoPreview = document.getElementById("photoPreview");
    let newPhotoBase64 = techData.profilePicture || techData.profile_picture || DEFAULT_PHOTO;

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

    // --- SAVE CHANGES ---
    document.getElementById("btnSaveChanges").addEventListener("click", async () => {
        try {
            const res = await authFetch("/api/me", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    display_name: document.getElementById("editNickname").value.trim() || null,
                    profile_picture: newPhotoBase64,
                }),
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(Array.isArray(data.detail) ? "Invalid profile data." : (data.detail || "Could not update profile"));
            }

            data.profilePicture = data.profile_picture;
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

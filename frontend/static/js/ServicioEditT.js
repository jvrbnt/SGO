document.addEventListener("DOMContentLoaded", () => {
    // Use currentUser to be consistent with Technician flow
    const techData = JSON.parse(localStorage.getItem('currentUser'));
    const DEFAULT_PHOTO = "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";

    // Validate technician and session
    if (!techData || techData.role !== "technician") {
        window.location.href = "/login";
        return;
    }

    // --- UPDATE TOP BAR ---
    const updateBar = () => {
        const name = techData.nickname || `${techData.first_name} ${techData.last_name}`;
        document.getElementById("userNameBar").textContent = name;
        document.getElementById("userIcon").src = techData.profilePicture || DEFAULT_PHOTO;
    };
    updateBar();

    // --- LOAD FORM DATA ---
    document.getElementById("photoPreview").src = techData.profilePicture || DEFAULT_PHOTO;
    document.getElementById("editNickname").value = techData.nickname || "";

    // --- PHOTO MANAGEMENT ---
    const btnChangePhoto = document.getElementById("btnChangePhoto");
    const btnRemovePhoto = document.getElementById("btnRemovePhoto");
    const inputPhotoFile = document.getElementById("inputPhotoFile");
    const photoPreview = document.getElementById("photoPreview");
    let newPhotoBase64 = techData.profilePicture || DEFAULT_PHOTO;

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
    document.getElementById("btnSaveChanges").addEventListener("click", () => {
        techData.profilePicture = newPhotoBase64;
        techData.nickname = document.getElementById("editNickname").value;

        // Update current session
        localStorage.setItem('currentUser', JSON.stringify(techData));

        // Update in global user list
        let users = JSON.parse(localStorage.getItem('users')) || [];
        const index = users.findIndex(u => u.email === techData.email);
        if (index !== -1) {
            users[index] = techData;
            localStorage.setItem('users', JSON.stringify(users));
        }

        alert("Technician profile updated successfully!");
        window.location.reload();
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
        window.location.href = "/login";
    });
});
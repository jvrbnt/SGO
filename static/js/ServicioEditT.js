document.addEventListener("DOMContentLoaded", () => {
    const activeUser = JSON.parse(localStorage.getItem('activeUser'));
    const DEFAULT_PHOTO = "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";

    if (!activeUser) {
        window.location.href = "/SGO/static/html/ServicioLogin.html";
        return;
    }

    // --- NAME IN TOP BAR ---
    const updateBar = () => {
        const name = activeUser.nickname || activeUser.name || "Technician";
        document.getElementById("userNameBar").textContent = name;
        document.getElementById("userIcon").src = activeUser.profilePicture || DEFAULT_PHOTO;
    };
    updateBar();

    // --- LOAD FORM DATA ---
    document.getElementById("photoPreview").src = activeUser.profilePicture || DEFAULT_PHOTO;
    document.getElementById("editNickname").value = activeUser.nickname || "";

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

    // --- SAVE CHANGES ---
    document.getElementById("btnSaveChanges").addEventListener("click", () => {
        activeUser.profilePicture = newPhotoBase64;
        activeUser.nickname = document.getElementById("editNickname").value;

        // Update current session
        localStorage.setItem('activeUser', JSON.stringify(activeUser));

        // Update local user database
        let users = JSON.parse(localStorage.getItem('users')) || [];
        const index = users.findIndex(u => u.email === activeUser.email);
        if (index !== -1) {
            users[index] = activeUser;
            localStorage.setItem('users', JSON.stringify(users));
        }

        alert("Technician profile updated successfully");
        window.location.reload();
    });

    // --- NAVIGATION ---
    const profileContainer = document.getElementById("profileContainer");
    const dropdownMenu = document.getElementById("dropdownMenu");
    profileContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle("hidden");
    });
    document.addEventListener("click", () => dropdownMenu.classList.add("hidden"));

    document.getElementById("editProfile").addEventListener("click", () => {
        window.location.href = "/SGO/static/html/servicioEditT.html";
    });

    document.getElementById("logOut").addEventListener("click", () => {
        localStorage.removeItem('activeUser');
        window.location.href = "/SGO/static/html/ServicioLogin.html";
    });
});
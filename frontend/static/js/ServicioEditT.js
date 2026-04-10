document.addEventListener("DOMContentLoaded", () => {
    // Usamos 'currentUser' para ser consistentes con ServicioTecnico.js
    const techData = JSON.parse(localStorage.getItem('currentUser'));
    const DEFAULT_PHOTO = "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";

    // Validar si es técnico y si hay sesión
    if (!techData || techData.role !== "technician") {
        window.location.href = "/login";
        return;
    }

    // --- ACTUALIZAR BARRA SUPERIOR ---
    const updateBar = () => {
        const name = techData.nickname || `${techData.first_name} ${techData.last_name}`;
        document.getElementById("userNameBar").textContent = name;
        document.getElementById("userIcon").src = techData.profilePicture || DEFAULT_PHOTO;
    };
    updateBar();

    // --- CARGAR DATOS EN EL FORMULARIO ---
    document.getElementById("photoPreview").src = techData.profilePicture || DEFAULT_PHOTO;
    document.getElementById("editNickname").value = techData.nickname || "";

    // --- GESTIÓN DE FOTO ---
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

    // --- GUARDAR CAMBIOS ---
    document.getElementById("btnSaveChanges").addEventListener("click", () => {
        techData.profilePicture = newPhotoBase64;
        techData.nickname = document.getElementById("editNickname").value;

        // Actualizar sesión actual
        localStorage.setItem('currentUser', JSON.stringify(techData));

        // Actualizar en la lista global de usuarios (si la usas para el login)
        let users = JSON.parse(localStorage.getItem('users')) || [];
        const index = users.findIndex(u => u.email === techData.email);
        if (index !== -1) {
            users[index] = techData;
            localStorage.setItem('users', JSON.stringify(users));
        }

        alert("Perfil de técnico actualizado correctamente");
        window.location.reload();
    });

    // --- NAVEGACIÓN Y MENÚ ---
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
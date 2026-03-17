document.addEventListener("DOMContentLoaded", () => {
    const usuarioActivo = JSON.parse(localStorage.getItem('usuarioActivo'));
    const FOTO_DEFECTO = "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";
    
    if (!usuarioActivo) {
        window.location.href = "/static/html/ServicioLogin.html";
        return;
    }

    // --- NOMBRE EN LA BARRA ---
    const actualizarBarra = () => {
        const nombre = usuarioActivo.apodo || usuarioActivo.nombre || "Técnico";
        document.getElementById("nombreUsuarioBarra").textContent = nombre;
        document.getElementById("iconoUsuario").src = usuarioActivo.fotoPerfil || FOTO_DEFECTO;
    };
    actualizarBarra();

    // --- CARGAR DATOS EN FORMULARIO ---
    document.getElementById("previewFoto").src = usuarioActivo.fotoPerfil || FOTO_DEFECTO;
    document.getElementById("editApodo").value = usuarioActivo.apodo || "";

    // --- GESTIÓN DE FOTO ---
    const btnCambiarFoto = document.getElementById("btnCambiarFoto");
    const btnQuitarFoto = document.getElementById("btnQuitarFoto");
    const inputFileFoto = document.getElementById("inputFileFoto");
    const previewFoto = document.getElementById("previewFoto");
    let nuevaFotoBase64 = usuarioActivo.fotoPerfil;

    btnCambiarFoto.addEventListener("click", () => inputFileFoto.click());
    
    btnQuitarFoto.addEventListener("click", () => {
        nuevaFotoBase64 = FOTO_DEFECTO;
        previewFoto.src = FOTO_DEFECTO;
    });

    inputFileFoto.addEventListener("change", function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewFoto.src = e.target.result;
                nuevaFotoBase64 = e.target.result;
            }
            reader.readAsDataURL(file);
        }
    });

    // --- GUARDAR CAMBIOS ---
    document.getElementById("btnGuardarCambios").addEventListener("click", () => {
        usuarioActivo.fotoPerfil = nuevaFotoBase64;
        usuarioActivo.apodo = document.getElementById("editApodo").value;

        // Actualizar sesión actual
        localStorage.setItem('usuarioActivo', JSON.stringify(usuarioActivo));

        // Actualizar base de datos local (usuarios)
        let usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];
        const index = usuarios.findIndex(u => u.email === usuarioActivo.email);
        if (index !== -1) {
            usuarios[index] = usuarioActivo;
            localStorage.setItem('usuarios', JSON.stringify(usuarios));
        }

        alert("Perfil técnico actualizado correctamente");
        window.location.reload();
    });

    // --- NAVEGACIÓN ---
    const perfilContainer = document.getElementById("perfilContainer");
    const menu = document.getElementById("menuDesplegable");
    perfilContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        menu.classList.toggle("oculto");
    });
    document.addEventListener("click", () => menu.classList.add("oculto"));

document.getElementById("editarPerfil").addEventListener("click", () => {
    window.location.href = "/static/html/ServicioEditT.html";
});

    document.getElementById("cerrarSesion").addEventListener("click", () => {
        localStorage.removeItem('usuarioActivo');
        window.location.href = "/static/html/ServicioLogin.html";
    });
});
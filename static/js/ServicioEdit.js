document.addEventListener("DOMContentLoaded", () => {
    const usuarioActivo = JSON.parse(localStorage.getItem('usuarioActivo'));
    const FOTO_DEFECTO = "https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png";
    
    if (!usuarioActivo) {
        window.location.href = "/SGO/static/html/ServicioLogin.html";
        return;
    }

    // --- LOGICA DE NOMBRE EN BARRA ---
    const actualizarNombreBarra = () => {
        let nombreAMostrar = "";
        if (usuarioActivo.apodo && usuarioActivo.apodo.trim() !== "") {
            nombreAMostrar = usuarioActivo.apodo;
        } else {
            const nombreCompleto = `${usuarioActivo.nombre || ""} ${usuarioActivo.apellidos || ""}`.trim();
            nombreAMostrar = nombreCompleto !== "" ? nombreCompleto : "Usuario";
        }
        document.getElementById("nombreUsuarioBarra").textContent = nombreAMostrar;
    };
    actualizarNombreBarra();

    // --- CARGA INICIAL DE INPUTS ---
    document.getElementById("iconoUsuario").src = usuarioActivo.fotoPerfil || FOTO_DEFECTO;
    document.getElementById("previewFoto").src = usuarioActivo.fotoPerfil || FOTO_DEFECTO;
    document.getElementById("editApodo").value = usuarioActivo.apodo || "";
    document.getElementById("editEntidad").value = usuarioActivo.entidad || "CSIC";

    const divInternos = document.getElementById("camposInternos");
    
    const gestionarVistaInterna = (valor) => {
        if (valor === "interno(MiNa)") {
            divInternos.classList.remove("oculto-form");
        } else {
            divInternos.classList.add("oculto-form");
        }
    };

    gestionarVistaInterna(usuarioActivo.entidad);

    // Solo cargamos los datos si es interno
    if (usuarioActivo.entidad === "interno(MiNa)") {
        if (usuarioActivo.grupo) {
            document.getElementById("editGrupo").value = usuarioActivo.grupo;
        }
        document.getElementById("editIP").value = usuarioActivo.ip || "";
        document.getElementById("editCuentaInterna").value = usuarioActivo.cuentaInterna || "";
        document.getElementById("editProyecto").value = usuarioActivo.proyecto || "";
    }

    // --- GESTIÓN DE LA FOTO ---
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

    // --- CAMBIO DE ENTIDAD ---
    document.getElementById("editEntidad").addEventListener("change", function() {
        gestionarVistaInterna(this.value);
    });

    // --- MENU DESPLEGABLE ---
    const perfilContainer = document.getElementById("perfilContainer");
    const menuDesplegable = document.getElementById("menuDesplegable");
    perfilContainer.addEventListener("click", (e) => {
        e.stopPropagation();
        menuDesplegable.classList.toggle("oculto");
    });
    document.addEventListener("click", () => menuDesplegable.classList.add("oculto"));

    // --- GUARDAR ---
    document.getElementById("btnGuardarCambios").addEventListener("click", () => {
        const entidadSeleccionada = document.getElementById("editEntidad").value;
        const grupoSeleccionado = document.getElementById("editGrupo").value;

        // Validación simple: si es interno, obligar a elegir grupo
        if (entidadSeleccionada === "interno(MiNa)" && grupoSeleccionado === "") {
            alert("Por favor, selecciona un Grupo de Investigación.");
            return;
        }

        usuarioActivo.fotoPerfil = nuevaFotoBase64;
        usuarioActivo.apodo = document.getElementById("editApodo").value;
        usuarioActivo.entidad = entidadSeleccionada;

        if (usuarioActivo.entidad === "interno(MiNa)") {
            usuarioActivo.grupo = grupoSeleccionado;
            usuarioActivo.ip = document.getElementById("editIP").value;
            usuarioActivo.cuentaInterna = document.getElementById("editCuentaInterna").value;
            usuarioActivo.proyecto = document.getElementById("editProyecto").value;
        }

        localStorage.setItem('usuarioActivo', JSON.stringify(usuarioActivo));
        let usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];
        const index = usuarios.findIndex(u => u.email === usuarioActivo.email);
        if (index !== -1) {
            usuarios[index] = usuarioActivo;
            localStorage.setItem('usuarios', JSON.stringify(usuarios));
        }

        alert("Perfil actualizado correctamente");
        window.location.reload();
    });

    document.getElementById("irServicios").addEventListener("click", () => { window.location.href = "/SGO/static/html/ServicioUsuario.html"; });
    document.getElementById("cerrarSesion").addEventListener("click", () => {
        localStorage.removeItem('usuarioActivo');
        window.location.href = "/SGO/static/html/ServicioLogin.html";
    });
});
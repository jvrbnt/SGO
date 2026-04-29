from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["pages"])

@router.get("/")
async def read_index():
    return FileResponse("frontend/templates/ServicioLogin.html")

@router.get("/login")
async def read_login():
    return FileResponse("frontend/templates/ServicioLogin.html")

@router.get("/cliente")
async def read_cliente():
    return FileResponse("frontend/templates/ServicioCliente.html")

@router.get("/tecnico")
async def read_tecnico():
    return FileResponse("frontend/templates/ServicioTecnico.html")

@router.get("/registro")
async def read_registro():
    return FileResponse("frontend/templates/ServicioSign.html")

@router.get("/editar-cliente")
async def read_edit_cliente():
    return FileResponse("frontend/templates/ServicioEdit.html")

@router.get("/editar-tecnico")
async def read_edit_tecnico():
    return FileResponse("frontend/templates/servicioEditT.html")

@router.get("/cookies")
async def read_cookies():
    return FileResponse("frontend/templates/Cookies.html")

@router.get("/proteccion-datos")
async def read_proteccion():
    return FileResponse("frontend/templates/Proteccion.html")

@router.get("/aviso-legal")
async def read_avisolegal():
    return FileResponse("frontend/templates/AvisoLegal.html")

@router.get("/contacto")
async def read_contacto():
    return FileResponse("frontend/templates/Contacto.html")

@router.get("/developers")
async def read_developers():
    return FileResponse("frontend/templates/Developers.html")

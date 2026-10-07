"""
Example usage of Nextcloud integration

Este archivo muestra cómo usar el cliente de Nextcloud tanto de forma
sincróna como dentro de los endpoints FastAPI.
"""

import os
from backend.nextcloud import NextcloudClient, get_nextcloud_client

# ============================================================
# EJEMPLO 1: Uso directo del cliente de Nextcloud
# ============================================================

def example_direct_usage():
    """Direct usage of Nextcloud client"""
    client = NextcloudClient(
        base_url="https://saco.csic.es",
        username="tu_usuario",
        password="tu_contraseña"
    )

    # Subir un archivo
    success = client.upload_file(
        local_file_path="./documento_local.pdf",
        remote_file_path="/SGO/documentos/documento_local.pdf"
    )
    print(f"Upload successful: {success}")

    # Descargar un archivo
    success = client.download_file(
        remote_file_path="/SGO/documentos/documento_local.pdf",
        local_file_path="./downloaded_file.pdf"
    )
    print(f"Download successful: {success}")

    # Crear una carpeta
    success = client.create_folder("/SGO/reportes/")
    print(f"Folder created: {success}")

    # Listar archivos
    files = client.list_files("/SGO/")
    print(f"Files in /SGO/: {files}")

    # Eliminar un archivo
    success = client.delete_file("/SGO/documentos/documento_local.pdf")
    print(f"Delete successful: {success}")


# ============================================================
# EJEMPLO 2: Uso con variables de entorno (.env)
# ============================================================

def example_from_env():
    """Using client initialized from environment variables"""
    client = get_nextcloud_client()

    # Ahora simplemente usa el cliente
    success = client.upload_file(
        local_file_path="./test.pdf",
        remote_file_path="/test.pdf"
    )
    return success


# ============================================================
# EJEMPLO 3: Integración en FastAPI (ya está en routers/nextcloud.py)
# ============================================================

"""
Los siguientes endpoints ya están disponibles en tu API:

1. POST /api/files/upload
   - Sube un archivo a Nextcloud
   - Parámetros: file (UploadFile), remote_path (str)
   
2. GET /api/files/download
   - Descarga un archivo desde Nextcloud
   - Parámetros: remote_path (str)
   
3. POST /api/files/folder
   - Crea una carpeta en Nextcloud
   - Parámetros: folder_path (str)
   
4. DELETE /api/files/file
   - Elimina un archivo de Nextcloud
   - Parámetros: remote_path (str)

Ejemplos con curl:

# Upload
curl -X POST "http://localhost:8000/api/files/upload" \
  -F "file=@documento.pdf" \
  -F "remote_path=/SGO/documentos/documento.pdf"

# Download
curl -X GET "http://localhost:8000/api/files/download?remote_path=/SGO/documentos/documento.pdf" \
  -o documento_descargado.pdf

# Create folder
curl -X POST "http://localhost:8000/api/files/folder" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/SGO/reportes/"}'

# Delete file
curl -X DELETE "http://localhost:8000/api/files/file?remote_path=/SGO/documentos/documento.pdf"
"""


# ============================================================
# EJEMPLO 4: Uso en un modelo o servicio
# ============================================================

class DocumentService:
    """Example service that uses Nextcloud"""

    def __init__(self):
        self.nc_client = get_nextcloud_client()

    def save_document(self, local_path: str, document_name: str) -> bool:
        """Save a document to Nextcloud"""
        remote_path = f"/SGO/documentos/{document_name}"
        return self.nc_client.upload_file(local_path, remote_path)

    def get_document(self, document_name: str, local_path: str) -> bool:
        """Retrieve a document from Nextcloud"""
        remote_path = f"/SGO/documentos/{document_name}"
        return self.nc_client.download_file(remote_path, local_path)

    def delete_document(self, document_name: str) -> bool:
        """Delete a document from Nextcloud"""
        remote_path = f"/SGO/documentos/{document_name}"
        return self.nc_client.delete_file(remote_path)


if __name__ == "__main__":
    print("Este archivo contiene ejemplos de uso de Nextcloud")
    print("Consulta la documentación para más detalles")

#!/usr/bin/env python
"""Test Nextcloud connection"""
import os
import logging
from backend.nextcloud import NextcloudClient
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Cargar variables de entorno
load_dotenv()

url = os.getenv("NEXTCLOUD_URL")
username = os.getenv("NEXTCLOUD_USERNAME")
password = os.getenv("NEXTCLOUD_PASSWORD")
remote_path = os.getenv("NEXTCLOUD_REMOTE_PATH")

print(f"=== Configuración ===")
print(f"URL: {url}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password) if password else 'NO SET'}")
print(f"Remote Path: {remote_path}")
print()

if not url or not username or not password:
    print("❌ ERROR: Faltan credenciales en .env")
    exit(1)

print("=== Probando conexión ===")
client = NextcloudClient(url, username, password, remote_path)

# Test 1: Listar archivos
print("\n[Test 1] Listando archivos en /...")
try:
    result = client.list_files("/")
    if result:
        print("✅ Conexión exitosa")
        print(f"Response (primeros 500 chars): {str(result)[:500]}")
    else:
        print("❌ Falló al listar archivos")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Crear archivo de prueba
print("\n[Test 2] Creando archivo de prueba...")
test_file = "test_nextcloud.txt"
try:
    with open(test_file, "w") as f:
        f.write("Test file from SGO")
    
    success = client.upload_file(test_file, "/sgo_test.txt")
    if success:
        print("✅ Archivo subido exitosamente")
    else:
        print("❌ Falló al subir archivo")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Descargar archivo
print("\n[Test 3] Descargando archivo...")
try:
    download_path = "test_nextcloud_download.txt"
    success = client.download_file("/sgo_test.txt", download_path)
    if success and os.path.exists(download_path):
        with open(download_path, "r") as f:
            content = f.read()
        print(f"✅ Archivo descargado: {content}")
    else:
        print("❌ Falló al descargar archivo")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Limpiar
""" print("\n[Test 4] Eliminando archivo de prueba...")
try:
    success = client.delete_file("/sgo_test.txt")
    if success:
        print("✅ Archivo eliminado")
    else:
        print("❌ Falló al eliminar archivo")
except Exception as e:
    print(f"❌ Error: {e}") """

# Limpiar archivos locales
for f in [test_file, download_path]:
    if os.path.exists(f):
        os.remove(f)

print("\n=== Prueba completada ===")

# Guía Interna de Desarrollo (Para el Equipo)

¡Hola equipo! En las últimas actualizaciones hemos profesionalizado la arquitectura del proyecto SGO para garantizar que sea seguro y fácil de desplegar en el servidor del CSIC. Aquí tenéis explicados los nuevos conceptos y archivos que vais a ver en el repositorio.

## 1. El Sistema de Paquetes (`uv` y `pyproject.toml`)
**¿Qué ha pasado con `requirements.txt` y `pip`?**
Los hemos eliminado. En producción (el servidor), usar `pip install` es peligroso porque las versiones de las librerías pueden cambiar de un día para otro y romper el servidor. 

Hemos migrado a **`uv`**, que es el gestor moderno oficial. 
*   **`pyproject.toml`**: Es el nuevo archivo maestro que dice qué librerías necesita nuestro proyecto (sustituye a `requirements.txt`).
*   **`uv.lock`**: Es un archivo generado automáticamente que "congela" las versiones exactas de las librerías. Gracias a este archivo, si desplegamos en el servidor dentro de 2 años, se instalará *exactamente* el mismo entorno que tenemos hoy, evitando cuelgues.
*   **`.venv`**: La carpeta de vuestro entorno virtual.

**¿Cómo trabajo ahora?**
Simplemente instala uv (`pip install uv` a nivel global) y en la carpeta del proyecto ejecuta `uv sync`. Eso instalará todo mágicamente.

## 2. La Base de Datos (`Alembic` y `alembic.ini`)
Antes modificábamos las columnas de la Base de Datos a mano desde DBeaver. Esto es una mala práctica porque si borras una columna por error en producción, pierdes todos los datos.

*   **¿Qué es Alembic?** Es como un "Git" pero para la base de datos.
*   **`alembic.ini`**: Archivo de configuración de la herramienta.
*   **Carpeta `alembic/versions/`**: Aquí se guardan los "commits" de la base de datos (archivos `.py` con las instrucciones de qué columnas se han añadido o borrado).

**¿Cómo trabajo ahora?**
Si cambias algo en `models.py` (ej: añades un campo `telefono`), no toques DBeaver. Ve a la terminal y pon:
1. `uv run alembic revision --autogenerate -m "añadir_telefono"`
2. `uv run alembic upgrade head` (Esto aplicará el cambio a PostgreSQL de forma segura).

## 3. Seguridad (`JWT` y `.env`)
Hemos dejado de guardar las sesiones inseguras en el navegador. Ahora el servidor Python firma una llave digital (JSON Web Token o JWT) y se la da al usuario cuando inicia sesión. 

**Atención con el `.env`:**
Vuestro archivo `.env` local DEBE tener ahora esta variable para que el servidor pueda firmar las llaves:
`JWT_SECRET_KEY=2437b3509e0cc3640b7edfc73948b5752521914fdaf8278371c96efd4aa130a8`

*(Nota: Recordad que el archivo `.env` NUNCA se sube a GitHub).*

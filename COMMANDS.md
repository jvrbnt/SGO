# SGO Project - Cheat Sheet de Comandos

Esta guía contiene todos los comandos actualizados tras la refactorización de seguridad, la adopción del gestor moderno `uv`, migraciones con `Alembic`, y JWT.

## 1. Configuración del Entorno (Nuevo Flujo con `uv`)
Ya **no** usamos `pip` ni `requirements.txt`. Hemos migrado a `uv` (mucho más rápido y seguro).

*   **Instalar dependencias del proyecto (sustituye a pip install -r):**
    `uv sync`
*   **Añadir una nueva librería al proyecto (sustituye a pip install X):**
    `uv add <nombre_paquete>`
*   **Ejecutar un script usando el entorno de uv:**
    `uv run python script.py`

## 2. Base de Datos y Migraciones (Alembic)
Hemos integrado Alembic, que funciona muy parecido a Git, pero para la base de datos. **NUNCA** debes modificar una columna en `models.py` sin crear una migración, o romperás los datos de producción. El flujo seria:

*   **Generar una migración (tras cambiar models.py):**
    `uv run alembic revision --autogenerate -m "nombre_descriptivo"`
*   **Revisar el archivo generado:**
    Abre la carpeta `alembic/versions/` y asegúrate de que el script hace lo que quieres (ej. usa `alter_column` en lugar de `drop_column` si estás renombrando).
*   **Aplicar la migración a la Base de Datos:**
    `uv run alembic upgrade head`

## 3. Ejecución del Servidor Local (FastAPI)
*   **Ejecución de desarrollo (con autorecarga):**
    `uv run uvicorn backend.main:app --reload`
*   **Aviso de Seguridad:** Tu archivo `.env` debe contener `JWT_SECRET_KEY` y `SECRET_PEPPER`.
## 4. Servidor de Producción (Docker)
Preparación de comandos para cuando automaticemos el despliegue en `/srv/www/sgo/`:

*   **Levantar toda la infraestructura (BD + FastAPI):**
    `docker compose up -d --build`
*   **Ver logs en tiempo real:**
    `docker compose logs -f web`
*   **Bajar la infraestructura:**
    `docker compose down`

## 5. Flujo de Git y Ramas
*   **Crear nueva rama:** `git checkout -b feature/nombre-de-tarea`
*   **Cambiar de rama:** `git checkout nombre-de-la-rama`
*   **Actualizar rama actual con servidor:** `git pull origin main`
*   **Subir rama:** `git push -u origin nombre-de-la-rama`

## 6. Emergencias y Rollbacks
*   **Hard Reset (calcar el servidor borrando lo tuyo):**
    `git reset --hard origin/main`
*   **Deshacer el último commit (manteniendo cambios en local):**
    `git reset --soft HEAD~1`

# Sistema de Gestión de Ofertas (SGO) - CSIC MiNaWeb

Plataforma unificada para la gestión integral de servicios técnicos, facturación, y seguimiento de ofertas de la Sala Blanca (MiNa). 

## 🏗️ Arquitectura
*   **Backend:** Python 3.13 con FastAPI.
*   **Base de Datos:** PostgreSQL (con SQLAlchemy ORM + Alembic).
*   **Gestor de Paquetes:** `uv`.
*   **Frontend:** Vanilla JS, HTML y CSS (Servido estáticamente).
*   **Seguridad:** Autenticación JWT (JSON Web Tokens) + Roles de usuario (Admin, Técnico, Cliente).

## 🚀 Requisitos y Configuración Inicial

### 1. Variables de Entorno (`.env`)
En la raíz del proyecto, debes crear un archivo `.env` con las credenciales de acceso.
```env
DATABASE_URL=postgresql://sgo_user:PASSWORD@IP_SERVIDOR:5432/mina_sgo
SECRET_PEPPER=tu_pimienta_para_passwords
JWT_SECRET_KEY=tu_clave_secreta_jwt_de_64_caracteres
```
*Nota: Es obligatorio estar conectado a la VPN del CSIC para que el backend pueda alcanzar la Base de Datos.*

### 2. Instalación de Dependencias (`uv`)
Hemos abandonado `pip` y `requirements.txt` a favor del estándar moderno `uv` para evitar dependencias rotas en el servidor.
1. Instala `uv` si no lo tienes: `pip install uv`
2. Sincroniza el proyecto (instala el entorno `.venv` automáticamente):
   ```bash
   uv sync
   ```

### 3. Migraciones de Base de Datos
La base de datos se gestiona exclusivamente a través de Alembic. No modifiques las tablas manualmente con DBeaver.
```bash
# Aplica los últimos cambios a tu base de datos:
uv run alembic upgrade head
```

### 4. Lanzar el Servidor Local
Para arrancar el servidor en modo desarrollo:
```bash
uv run uvicorn backend.main:app --reload
```
Abre `http://127.0.0.1:8000/` en tu navegador. 

## 🛡️ Estructura y Flujos (Roles)
1.  **Administrador (`/admin`):** Gestión de catálogos, altas/bajas de técnicos y volcado de datos.
2.  **Técnico (`/tecnico`):** Control presupuestario, asignación de horas de servicio y generación de Facturas a grupos del CSIC o externos.
3.  **Cliente (`/cliente`):** Realización de peticiones, historial de facturación y perfil (Gestión de IP, Proyecto, etc.).

## 🐳 Despliegue en Servidor (Próximamente)
Este proyecto está preparado para dockerizarse mediante `docker-compose`. Las instrucciones de despliegue en producción se centralizarán a través del orquestador de contenedores para garantizar que Frontend, Backend y la Base de Datos compartan la misma red y persistan sus volúmenes correctamente.

*(Consulta `COMMANDS.md` para ver el Cheat Sheet de comandos útiles).*

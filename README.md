# Sistema de Gestión de Ofertas (SGO)

Este repositorio contiene el código fuente del Sistema de Gestión de Ofertas (SGO) desarrollado para el IMN.

## Arquitectura del Sistema

*   **Backend:** Python 3.13 con framework FastAPI.
*   **Base de Datos:** PostgreSQL con SQLAlchemy ORM y migraciones con Alembic.
*   **Gestor de Dependencias:** `uv`.
*   **Frontend:** Interfaz nativa servida estáticamente (HTML5, CSS3, Vanilla JS).
*   **Seguridad:** Autenticación por JSON Web Tokens (JWT) y Control de Acceso Basado en Roles (RBAC).
*   **Trazabilidad:** Documentos PDF persistentes con hash `sha256` y trazabilidad RG-12 en base de datos.

## Estructura del Repositorio

*   `/backend`: Lógica de servidor, modelos de datos, esquemas de validación y rutas de API.
*   `/frontend`: Plantillas HTML, estilos CSS y scripts de cliente interactivos.
*   `/alembic`: Sistema de control de versiones para la base de datos PostgreSQL.
*   `/docs_oficiales`: Plantillas oficiales necesarias para generar documentos.

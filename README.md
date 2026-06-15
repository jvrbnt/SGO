# Sistema de Gestion de Ofertas (SGO)

Codigo fuente del Sistema de Gestion de Ofertas (SGO) para uso interno del IMN(CSIC).

## Arquitectura

- **Backend:** Python 3.13, FastAPI, SQLAlchemy.
- **Base de datos:** PostgreSQL con migraciones Alembic.
- **Frontend:** HTML, CSS y JavaScript nativo servido por el backend.
- **Despliegue:** Docker Compose con servicios `db`, `web` y `nginx`.
- **Seguridad:** autenticacion JWT, roles y comprobaciones de propiedad de recursos.
- **Trazabilidad:** documentos persistentes con hash `sha256` y registros RG-12 en base de datos.

## Estructura

- `backend`: API, modelos, seguridad, flujo de negocio y generacion documental.
- `frontend`: plantillas, estilos y scripts de cliente.
- `alembic`: migraciones de base de datos.
- `docs_oficiales`: plantillas oficiales necesarias para documentos.
- `demo_scripts`: scripts de carga de datos de prueba.
- `tests`: pruebas automaticas.

## Operacion

La guia de mantenimiento, despliegue y verificacion se entrega fuera del repositorio para evitar mezclar documentacion operativa interna con codigo fuente.

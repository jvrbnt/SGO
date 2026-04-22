# Sistema de Gestión de Ofertas (SGO) - MiNa

El Sistema de Gestión de Ofertas (SGO) es una plataforma integral desarrollada para la Sala Blanca (MiNa) del Instituto de Micro y Nanotecnología (IMN-CNM), perteneciente al CSIC.

Su propósito principal es digitalizar y unificar el flujo de trabajo entre investigadores, técnicos y la administración, optimizando la solicitud de servicios, el control presupuestario y la facturación de los trabajos realizados en las instalaciones.

## Arquitectura del Sistema

*   **Backend:** Python 3.13 con framework FastAPI.
*   **Base de Datos:** PostgreSQL con SQLAlchemy ORM.
*   **Gestor de Dependencias:** `uv`.
*   **Frontend:** Interfaz nativa servida estáticamente (HTML5, CSS3, Vanilla JS).
*   **Seguridad:** Autenticación por JSON Web Tokens (JWT) y Control de Acceso Basado en Roles (RBAC).

## Características Principales

*   **Catálogo Unificado:** Administración de servicios técnicos y estructuración de tarifas paramétricas (Interno, CSIC, Público, Privado).
*   **Gestión de Accesos:** Interfaces dedicadas para Administración, Técnicos y Clientes (Investigadores).
*   **Trazabilidad:** Ciclo de vida completo y trazable de peticiones (Solicitada → Presupuestada → Aceptada → Facturada → Finalizada).
*   **Motor de Facturación:** Generación agrupada de facturas hacia Investigadores Principales (IP) y vinculación con cuentas y proyectos.

## Contacto Institucional

Para consultas de acceso, credenciales o soporte técnico de la plataforma, por favor contacte con la administración de la Sala Blanca MiNa.
*(Instituto de Micro y Nanotecnología IMN-CNM, CSIC)*

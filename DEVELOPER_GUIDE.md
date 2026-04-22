# Developer Guide

## 1. Package Management (`uv` & `pyproject.toml`)
The project has migrated from `pip` (`requirements.txt`) to `uv` for deterministic dependency management.

*   **`pyproject.toml`**: Defines project metadata and top-level dependencies.
*   **`uv.lock`**: Auto-generated lockfile ensuring reproducible builds across environments. Do not edit manually.
*   **Workflow**: 
    *   To install/sync the environment: `uv sync`
    *   To add a dependency: `uv add <package>`
    *   To run scripts within the environment: `uv run <command>`

## 2. Database Migrations (`Alembic`)
Direct structural modifications via DBeaver or raw SQL are strictly prohibited. All schema changes must go through Alembic to maintain version control and CI/CD compatibility.

*   **`alembic.ini`**: Alembic configuration file. Reads `DATABASE_URL` dynamically from the `.env` file via `env.py`.
*   **`alembic/versions/`**: Directory containing timestamped migration scripts.
*   **Workflow**:
    1.  Modify `models.py`.
    2.  Generate script: `uv run alembic revision --autogenerate -m "description"`
    3.  Verify the generated script in `alembic/versions/` (ensure `alter_column` is used over `drop_column` for renames).
    4.  Apply to database: `uv run alembic upgrade head`

## 3. Security (`JWT` & Environment)
Client-side session storage has been replaced with stateless JSON Web Tokens (JWT). 

*   **`.env` Configuration**: All developers must define `JWT_SECRET_KEY` (64-character hex string) in their local `.env` file. Failure to do so will result in 500 Internal Server Errors during authentication.
*   **Authentication Flow**: The backend issues a Bearer token via `/api/login`. The frontend intercepts all subsequent `fetch` calls to inject the `Authorization: Bearer <token>` header. Session validity is strictly verified on every protected route using `Depends(get_current_user)`.

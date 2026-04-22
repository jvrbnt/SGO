FROM python:3.13-slim

# Evitar que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evitar que Python haga buffer de stdout y stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar 'uv' copiando el binario oficial (método más rápido)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copiar archivos de dependencias
COPY pyproject.toml uv.lock ./

# Instalar dependencias usando uv de forma congelada y sin dependencias de dev
RUN uv sync --frozen --no-dev

# Copiar el resto del código
COPY . .

# Añadir el entorno virtual al PATH
ENV PATH="/app/.venv/bin:$PATH"

# Exponer el puerto
EXPOSE 8000

# Arrancar la aplicación usando Gunicorn manejando workers de Uvicorn
CMD ["gunicorn", "backend.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

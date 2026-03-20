# SGO Project - Cheat Sheet de Comandos

## 1. Configuración del Entorno (Python)
* **Permitir ejecución de scripts en Windows (Oficina):**
  `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
* **Crear entorno virtual:**
  `python -m venv venv`
* **Activar entorno (Windows):**
  `.\venv\Scripts\activate`
* **Activar entorno (Linux/Mac):**
  `source venv/bin/activate`
* **Instalar dependencias:**
  `pip install -r requirements.txt`
* **Congelar dependencias actuales:**
  `pip freeze > requirements.txt`

## 2. Ejecución del Servidor (FastAPI)
* **Ejecución Local:**
  `uvicorn main:app --reload`
* **Ejecución en Red:**
  `uvicorn main:app --host 0.0.0.0 --port 8000`
  *(Acceso desde otros PCs: http://TU_IP_LOCAL:8000)*

## 3. Flujo de Git y Ramas
* **Crear nueva rama de trabajo:**
  `git checkout -b feature/nombre-de-la-tarea`
* **Cambiar de rama:**
  `git checkout nombre-de-la-rama`
* **Traer cambios del servidor sin mezclar:**
  `git fetch origin`
* **Actualizar rama actual con lo que hay en el servidor:**
  `git pull origin main`
* **Fusionar una rama en la actual:**
  `git merge nombre-de-la-rama`
* **Subir rama nueva al servidor (Pull Request):**
  `git push -u origin nombre-de-la-rama`

## 4. Emergencias, Limpieza y Rollbacks
* **Hard Reset (borrar todo lo local y calcar el servidor):**
  `git reset --hard origin/main`
* **Limpiar archivos y carpetas no rastreados (ficheros basura):**
  `git clean -fd`
* **Ver historial de commits (para buscar hashes):**
  `git log --oneline`
* **Revertir un commit específico (crea un commit inverso):**
  `git revert <hash_del_commit>`
* **Deshacer el último commit manteniendo los cambios en los archivos:**
  `git reset --soft HEAD~1`

## 5. Resolución de Conflictos
1. **Identificar archivos en conflicto:** `git status`
2. **Abrir archivos y buscar:** `<<<< HEAD`
3. **Tras limpiar el código:** `git add <archivo>`
4. **Finalizar merge:** `git commit -m "Fix conflicts"`
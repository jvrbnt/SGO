# SGO - checklist segura para el servidor IMN

Esta guia es para aplicar cambios en el Ubuntu Server con Docker sin romper datos.

## Antes de desplegar

1. Hacer backup de PostgreSQL.

   ```bash
   docker compose exec db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup_sgo_$(date +%Y%m%d_%H%M).sql
   ```

2. Comprobar variables obligatorias en `.env`.

   ```env
   DATABASE_URL=postgresql://usuario:password@db:5432/base
   JWT_SECRET_KEY=valor_largo_aleatorio
   SECRET_PEPPER=otro_valor_largo_aleatorio
   ACCESS_TOKEN_EXPIRE_MINUTES=480
   CORS_ORIGINS=
   GENERATED_DOCUMENTS_DIR=data/generated_documents
   ```

   Si la web y la API se sirven desde el mismo dominio/IP, `CORS_ORIGINS` puede quedarse vacio.
   Si hay un frontend externo, poner solo origenes concretos separados por coma.
   `GENERATED_DOCUMENTS_DIR` queda dentro del volumen Docker `./data:/app/data`, asi los PDF generados persisten fuera del contenedor.
   No pongas `AUTO_CREATE_TABLES=true` en produccion: el esquema debe actualizarse con Alembic.

3. Preparar carpeta de documentos persistentes en el servidor.

   ```bash
   mkdir -p data/generated_documents
   ```

   No borrar esta carpeta: contiene copias PDF generadas y registradas con hash para auditoria.

4. Aplicar migraciones antes de levantar la version nueva.

   ```bash
   docker compose run --rm web alembic upgrade head
   ```

5. Reconstruir y levantar.

   ```bash
   docker compose up -d --build
   docker compose logs -f web
   ```

## Pasos especificos sobre la base de datos

1. La base actual tiene datos inventados, aun asi haz backup antes de tocar esquema.
2. Ejecuta `alembic upgrade head`; no uses `Base.metadata.drop_all()` ni borres el volumen `pgdata`.
3. Comprueba que existen estas tablas/columnas nuevas:
   - `clients.display_name`
   - `technicians.display_name`
   - `traceability_entries`
   - `generated_documents`
   - secuencia `offer_ref_seq`
4. Si hay registros de prueba en estados antiguos como `finished`, conviertelos a `completed` antes de pruebas reales:

   ```sql
   UPDATE offers SET status = 'completed' WHERE status = 'finished';
   ```

5. Para una prueba completa, crea una oferta nueva desde la web despues de migrar; asi se valida la secuencia `offer_ref_seq` y no dependes de datos antiguos.

## Prueba manual minima

1. Entrar como cliente y crear una oferta con un servicio del catalogo.
2. Entrar como tecnico, asignarse la oferta y todos sus servicios.
3. Enviar presupuesto al cliente.
4. Entrar como cliente y aceptar el presupuesto.
5. Entrar como tecnico asignado y marcar servicios como hechos.
6. Generar factura y comprobar que el total coincide con los servicios.
7. Marcar factura como pagada.
8. Editar el perfil de cliente/tecnico, cerrar sesion, volver a entrar y comprobar que los cambios persisten.
9. Descargar la trazabilidad CSV de una oferta presupuestada o posterior.
10. Descargar PDF de oferta como cliente y como tecnico; confirmar que aparece un archivo en `data/generated_documents/<año>/offers/`.
11. Descargar PDF de factura como cliente y como tecnico; confirmar que aparece un archivo en `data/generated_documents/<año>/invoices/`.

## Reglas de seguridad que protege el backend

- El cliente solo puede crear ofertas para su propio email.
- Una oferta solo se puede editar mientras esta en `requested`.
- Solo el manager asignado o un admin puede revisar una oferta.
- Todos los servicios activos deben estar asignados y tener precio antes de presupuestar.
- El cliente solo puede aceptar ofertas propias y ya presupuestadas.
- La factura recalcula el total en servidor; no confia en el total enviado por el navegador.
- Una oferta facturada o pagada queda bloqueada.
- Los emails no pueden repetirse entre clientes y tecnicos.
- El perfil editable se guarda en PostgreSQL, no solo en el navegador.
- La trazabilidad queda asociada a cada servicio y puede exportarse como CSV seguro para hoja de calculo.
- Cada PDF generado queda guardado en servidor y registrado en `generated_documents` con `sha256`.

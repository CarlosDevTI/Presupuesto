# Despliegue con Docker

## Servicios
- `backend`: Django + DRF sobre Gunicorn.
- `frontend`: Nginx sirviendo el build de Vite y haciendo proxy de `/api/` al backend.

## Puerto publicado
- `8013` por defecto en la VM.
- Cambia `APP_PORT` en `.env` si el servidor necesita otro puerto.

## Flujo
1. Copia `.env.example` a `.env`.
2. Deja el Excel fuente en `data/Presupuesto Gastos.xlsx`.
3. Ejecuta `docker compose up --build -d`.
4. Abre `http://IP_O_HOST:8013`.

## Persistencia
- `./data` se monta dentro de los contenedores como `/workspace/data`.
- Ahí viven el Excel local, la base SQLite y cualquier salida operativa.

## Notas
- La imagen de frontend no necesita conocer la IP final del backend: usa `/api` relativo y Nginx resuelve el proxy.
- SQLite implica dejar `GUNICORN_WORKERS=1` para evitar problemas de concurrencia innecesarios.
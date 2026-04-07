# Dashboard Presupuestal Corporativo

Proyecto full-stack para analizar presupuesto proyectado vs ejecutado a partir de un Excel jerarquico de cuentas contables.

## Estructura
- `backend/`: Django + DRF + Pandas + OpenPyXL.
- `frontend/`: React + Vite + TypeScript + Tailwind + Recharts + Zustand.
- `data/`: Excel local, SQLite y artefactos operativos no versionados.
- `deploy/`: Compose, entrypoint y configuracion de Nginx para despliegue.
- `docs/`: notas breves de arquitectura y despliegue.

## Estructura final recomendada
```text
presupuesto-dashboard/
  backend/
  frontend/
  data/
  deploy/
  docs/
  .env.example
  docker-compose.yml
  README.md
```

## Reorganizacion aplicada
- El Excel ya no queda suelto en la raiz del workspace. Ahora vive en `data/Presupuesto Gastos.xlsx`.
- La base SQLite local vive en `data/db.sqlite3`.
- Los assets del frontend quedan dentro del proyecto: `frontend/public/logo.png` y `frontend/src/assets/IconoHD.png`.
- Se elimino `desktop.ini` y el directorio externo `assets/` quedo vaciado y fuera del flujo del proyecto.

## Configuracion local
1. Copia `.env.example` a `.env` en la raiz del proyecto.
2. Verifica que el Excel este en `data/Presupuesto Gastos.xlsx`.
3. Backend:
```bash
cd backend
python manage.py migrate
python manage.py ensure_budget_data
python manage.py runserver
```
4. Frontend:
```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

### Que cambia en local
- El backend ahora toma configuracion desde `presupuesto-dashboard/.env`.
- Las rutas del Excel, SQLite y media pasan a ser relativas al proyecto, no absolutas al equipo.
- El frontend usa `/api` relativo y Vite hace proxy automatico a `http://127.0.0.1:8000` en desarrollo.

## Despliegue con Docker
```bash
docker compose up --build -d
```

### Servicios incluidos
- `backend`: Gunicorn sirviendo Django en red interna.
- `frontend`: Nginx publicando la SPA y proxy a `/api/`.

### Puerto publicado
- El proyecto queda expuesto en `http://HOST:8013`.
- Cambia `APP_PORT` en `.env` si la VM necesita otro puerto.

### Que cambia en produccion
- No se usa el servidor de desarrollo de Django ni el de Vite.
- La UI sale desde Nginx.
- La API queda interna entre contenedores y el unico puerto publico es `8013`.
- La carpeta `data/` se monta como volumen para mantener Excel y SQLite fuera de la imagen.

## Archivos de despliegue
- `docker-compose.yml`: orquestacion minima para VM.
- `backend/Dockerfile`: imagen Django + Gunicorn.
- `frontend/Dockerfile`: build Vite + Nginx.
- `deploy/backend-entrypoint.sh`: migraciones y bootstrap del dataset.
- `deploy/nginx/default.conf`: SPA fallback y proxy `/api/`.
- `docs/deploy.md`: notas rapidas de despliegue.

## Ubicacion de la logica clave
- Jerarquia y roll-up: `backend/budget/domain/hierarchy.py` y `backend/budget/domain/rollup.py`
- Normalizacion Excel: `backend/budget/ingestion/header_normalizer.py` y `backend/budget/ingestion/tabular_transform.py`
- Endpoints: `backend/budget/views.py` y `backend/budget/urls.py`
- Carga del dataset activo: `backend/budget/services/dataset_service.py`

## Endpoints principales
- `POST /api/budget/upload/`
- `GET /api/budget/summary/`
- `GET /api/budget/trend/`
- `GET /api/budget/areas/`
- `GET /api/budget/hierarchy/`
- `GET /api/budget/rankings/`
- `GET /api/budget/insights/`
- `GET /api/budget/filters/`

## Cambio de assets
- Logo principal: `frontend/public/logo.png`
- Icono secundario: `frontend/src/assets/IconoHD.png`
- Si cambias el Excel, reemplaza `data/Presupuesto Gastos.xlsx` o ajusta `BUDGET_DEFAULT_EXCEL_PATH` en `.env`.

## Verificacion recomendada
- `cd backend && python manage.py check`
- `cd backend && python manage.py test budget`
- `cd frontend && npm.cmd run build`
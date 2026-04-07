# Arquitectura breve

## Backend
- `budget/ingestion`: lectura del workbook, deteccion de encabezados y normalizacion tabular.
- `budget/domain`: semaforo, filtros, roll-up, KPIs, jerarquia, rankings e insights.
- `budget/services`: bootstrap de dataset, carga del Excel y consultas hacia Pandas/ORM.
- `budget/views.py`: endpoints REST listos para frontend.

## Frontend
- `src/store`: estado global y cache por query.
- `src/services`: capa de acceso HTTP.
- `src/components`: tarjetas KPI, filtros, charts, rankings, insights y tabla jerarquica.
- `src/pages/DashboardPage.tsx`: composicion de la vista ejecutiva.

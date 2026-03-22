# Demo Flask + MongoDB Atlas (MONGODB_TALLER)

App sencilla para cargar y consultar los datasets NDJSON del proyecto en MongoDB Atlas.

## 0) Que hace cada archivo

Analogia del restaurante: la app es una cocina.

- `app.py`:
 Es el cocinero principal. Se conecta a Atlas, crea las rutas web (`/health`, `/seed`, etc.) y devuelve datos.

- `.env`:
 Es una nota privada con secretos y configuracion real (usuario, password, nombres de bases). Sin esto, la app no sabe a que Atlas conectarse.

- `.env.example`:
 Es una plantilla de `.env`. Sirve para copiarla y rellenar datos reales del usuariosin compartir secretos.

- `requirements.txt`:
 Es la lista de ingredientes Python (Flask, pymongo, python-dotenv). Si falta uno, la app no arranca.

- `Atlas.txt`:
 Es una chuleta de comandos de importacion y pasos de Atlas para el taller.

- `comandos.txt`:
 Otra chuleta rapida de comandos de Mongo para practicar en local con mongosh.

- `*.ndjson` (datasets):
 Son las cajas con datos en bruto. Cada linea es un documento JSON.
 La app los usa en `/seed` para cargar datos en Atlas.

 Archivos de datos del proyecto:

- `penascal-socios.socios.ndjson`
- `penascal-proveedores.proveedores.ndjson`
- `penascal-docentes.profesores.ndjson`
- `penascal-matricula.penascal-bilbao.ndjson`
- `penascal-matricula.penascal-vitoria.ndjson`
- `ejemplo.ndjson` (archivo de ejemplo)

## Como encaja todo (version muy simple)

1. Arrancas la app (`app.py`).
2. `app.py` lee `.env` para saber a que Atlas conectarse.
3. Llamas a `POST /seed`.
4. La app lee los `.ndjson` y mete los documentos en Atlas.
5. Luego consultas con endpoints (`/api/socios`, `/api/proveedores`, etc.).
6. El navegador muestra resultados reales desde la nube.

Si falla algo, casi siempre es una de estas 3 cosas:

- URI/credenciales mal en `.env`
- IP no permitida en Atlas
- Usuario sin permisos en Database Access

## 1) Preparacion de entorno de desarrollo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` y pon tu cadena real de Atlas en `MONGODB_URI`.

Variables de base usadas por la app (alineadas con Atlas):

- `ATLAS_DB_MATRICULA=penascal-matricula`
- `ATLAS_DB_DOCENTES=penascal-docentes`
- `ATLAS_DB_SOCIOS=penascal-socios`
- `ATLAS_DB_PROVEEDORES=penascal-proveedores`

## 2) Ejecutar

```bash
flask --app app run --debug
```

Abre: <http://127.0.0.1:5000>

## 3) Cargar datos a Atlas

En la pagina principal pulsa `POST /seed` o ejecuta:

```bash
curl -X POST http://127.0.0.1:5000/seed
```

Colecciones que se cargan en Atlas:

- `penascal-socios.socios`
- `penascal-proveedores.proveedores`
- `penascal-docentes.profesores`
- `penascal-matricula.penascal-bilbao`
- `penascal-matricula.penascal-vitoria`

## 4) Endpoints de demo

- `GET /health`
- `GET /api/collections`
- `GET /api/socios?ciudad=Bilbao`
- `GET /api/proveedores?ciudad=Vitoria`
- `GET /api/join/proveedores-socios`
- `GET /api/matricula/resumen`

## 5) Nota sobre $lookup

Como Atlas en este taller usa bases separadas, el endpoint `GET /api/join/proveedores-socios` hace el join en la app (por `ciudad`) en lugar de usar `$lookup` directo entre bases.

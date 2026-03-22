import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGODB_URI")
DB_MATRICULA = os.getenv("ATLAS_DB_MATRICULA", "penascal-matricula")
DB_DOCENTES = os.getenv("ATLAS_DB_DOCENTES", "penascal-docentes")
DB_SOCIOS = os.getenv("ATLAS_DB_SOCIOS", "penascal-socios")
DB_PROVEEDORES = os.getenv("ATLAS_DB_PROVEEDORES", "penascal-proveedores")

client = MongoClient(MONGO_URI) if MONGO_URI else None


@app.errorhandler(PyMongoError)
def handle_pymongo_error(exc):
  message = str(exc)
  hint = "Verifica usuario/password de Atlas y que el password este URL-encoded si tiene caracteres especiales."
  status = 500
  if isinstance(exc, OperationFailure):
    status = 401
    hint = "Credenciales Atlas invalidas o usuario sin permisos para la base solicitada."
  return jsonify({"ok": False, "error": message, "hint": hint}), status

DATASETS = [
    ("socios", DB_SOCIOS, "socios", "penascal-socios.socios.ndjson"),
    ("proveedores", DB_PROVEEDORES, "proveedores", "penascal-proveedores.proveedores.ndjson"),
    ("docentes", DB_DOCENTES, "profesores", "penascal-docentes.profesores.ndjson"),
    ("matricula_bilbao", DB_MATRICULA, "penascal-bilbao", "penascal-matricula.penascal-bilbao.ndjson"),
    ("matricula_vitoria", DB_MATRICULA, "penascal-vitoria", "penascal-matricula.penascal-vitoria.ndjson"),
]

INDEX_HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MongoDB Atlas Demo</title>
  <style>
    :root {
      --bg: #f4efe6;
      --card: #fffdf8;
      --ink: #1f2933;
      --accent: #0f766e;
      --accent-2: #c2410c;
      --line: #d6cec2;
    }
    body {
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      background: radial-gradient(circle at top right, #f8e4c9, var(--bg));
      color: var(--ink);
    }
    .wrap {
      max-width: 900px;
      margin: 32px auto;
      padding: 0 16px;
    }
    .hero {
      border: 1px solid var(--line);
      background: var(--card);
      border-radius: 18px;
      padding: 20px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
    }
    h1 {
      margin: 0 0 8px;
      font-size: 1.8rem;
    }
    .row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 14px;
      margin-top: 16px;
    }
    .card {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
      background: #fff;
    }
    button {
      border: 0;
      border-radius: 8px;
      padding: 8px 12px;
      background: var(--accent);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
    }
    button.secondary {
      background: var(--accent-2);
    }
    pre {
      background: #111827;
      color: #e5e7eb;
      padding: 12px;
      border-radius: 10px;
      overflow: auto;
      min-height: 180px;
    }
    code {
      color: #0b5f59;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>Demo Flask + MongoDB Atlas</h1>
      <p>
        Bases Atlas:
        <code>matricula={{ db_matricula }}</code>,
        <code>docentes={{ db_docentes }}</code>,
        <code>socios={{ db_socios }}</code>,
        <code>proveedores={{ db_proveedores }}</code>
      </p>
      <p>1) Carga datos con <code>/seed</code> y 2) prueba endpoints de consulta y agregacion.</p>
      <div class="row">
        <div class="card">
          <h3>Seed de datos</h3>
          <p>Importa NDJSON de MONGODB_TALLER a Atlas.</p>
          <button onclick="run('/seed', 'POST')">POST /seed</button>
        </div>
        <div class="card">
          <h3>Socios por ciudad</h3>
          <p>Filtra por Bilbao o Vitoria.</p>
          <button onclick="run('/api/socios?ciudad=Bilbao')">GET /api/socios?ciudad=Bilbao</button>
        </div>
        <div class="card">
          <h3>Join proveedores-socios</h3>
          <p>Relacion por ciudad entre bases separadas.</p>
          <button class="secondary" onclick="run('/api/join/proveedores-socios')">GET /api/join/proveedores-socios</button>
        </div>
      </div>
    </section>
    <h3>Salida</h3>
    <pre id="out">Pulsa un boton para ejecutar una llamada.</pre>
  </div>
<script>
  async function run(url, method = 'GET') {
    const out = document.getElementById('out');
    out.textContent = 'Cargando...';
    try {
      const res = await fetch(url, { method });
      const data = await res.json();
      out.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      out.textContent = String(err);
    }
  }
</script>
</body>
</html>
"""


def read_ndjson(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def serialize(doc):
    out = dict(doc)
    if "_id" in out:
        out["_id"] = str(out["_id"])
    return out


def require_client():
    if client is None:
        return None, (
            jsonify(
                {
                    "ok": False,
                    "error": "Falta MONGODB_URI. Crea .env desde .env.example y configura Atlas.",
                }
            ),
            500,
        )
    return client, None


@app.get("/")
def home():
    return render_template_string(
        INDEX_HTML,
        db_matricula=DB_MATRICULA,
        db_docentes=DB_DOCENTES,
        db_socios=DB_SOCIOS,
        db_proveedores=DB_PROVEEDORES,
    )


@app.get("/health")
def health():
    if client is None:
        return jsonify({"ok": False, "error": "MONGODB_URI no configurado"}), 500
    client.admin.command("ping")
    return jsonify(
        {
            "ok": True,
            "databases": {
                "matricula": DB_MATRICULA,
                "docentes": DB_DOCENTES,
                "socios": DB_SOCIOS,
                "proveedores": DB_PROVEEDORES,
            },
        }
    )


@app.post("/seed")
def seed():
    current_client, err = require_client()
    if err:
        return err

    base = Path(__file__).resolve().parent
    imported = {}

    for logical_name, db_name, collection_name, file_name in DATASETS:
        file_path = base / file_name
        if not file_path.exists():
            imported[logical_name] = {"ok": False, "error": f"No existe {file_name}"}
            continue

        docs = read_ndjson(file_path)
        col = current_client[db_name][collection_name]
        col.drop()
        if docs:
            col.insert_many(docs)
        imported[logical_name] = {
            "ok": True,
            "database": db_name,
            "collection": collection_name,
            "count": len(docs),
        }

    return jsonify({"ok": True, "collections": imported})


@app.get("/api/collections")
def list_collections():
    current_client, err = require_client()
    if err:
        return err
    return jsonify(
        {
            "matricula": current_client[DB_MATRICULA].list_collection_names(),
            "docentes": current_client[DB_DOCENTES].list_collection_names(),
            "socios": current_client[DB_SOCIOS].list_collection_names(),
            "proveedores": current_client[DB_PROVEEDORES].list_collection_names(),
        }
    )


@app.get("/api/socios")
def socios():
    current_client, err = require_client()
    if err:
        return err

    ciudad = request.args.get("ciudad")
    query = {"ciudad": ciudad} if ciudad else {}
    rows = [
        serialize(x)
        for x in current_client[DB_SOCIOS].socios.find(
            query, {"_id": 1, "id": 1, "nombre": 1, "tipo": 1, "ciudad": 1}
        ).limit(50)
    ]
    return jsonify({"count": len(rows), "items": rows})


@app.get("/api/proveedores")
def proveedores():
    current_client, err = require_client()
    if err:
        return err

    ciudad = request.args.get("ciudad")
    categoria = request.args.get("categoria")
    query = {}
    if ciudad:
        query["ciudad"] = ciudad
    if categoria:
        query["categoria"] = categoria

    rows = [
        serialize(x)
        for x in current_client[DB_PROVEEDORES].proveedores.find(
            query, {"_id": 1, "id": 1, "nombre": 1, "categoria": 1, "ciudad": 1}
        ).limit(50)
    ]
    return jsonify({"count": len(rows), "items": rows})


@app.get("/api/join/proveedores-socios")
def join_proveedores_socios():
    current_client, err = require_client()
    if err:
        return err

    socios_counts_cursor = current_client[DB_SOCIOS].socios.aggregate(
        [{"$group": {"_id": "$ciudad", "total": {"$sum": 1}}}]
    )
    socios_counts = {x["_id"]: x["total"] for x in socios_counts_cursor}

    proveedores_rows = list(
        current_client[DB_PROVEEDORES]
        .proveedores.find({}, {"_id": 0, "id": 1, "nombre": 1, "ciudad": 1})
        .sort("id", 1)
        .limit(100)
    )
    rows = []
    for proveedor in proveedores_rows:
        rows.append(
            {
                "id": proveedor.get("id"),
                "nombre": proveedor.get("nombre"),
                "ciudad": proveedor.get("ciudad"),
                "total_socios_relacionados": socios_counts.get(proveedor.get("ciudad"), 0),
            }
        )
    return jsonify({"count": len(rows), "items": rows})


@app.get("/api/matricula/resumen")
def matricula_resumen():
    current_client, err = require_client()
    if err:
        return err

    b = current_client[DB_MATRICULA].get_collection("penascal-bilbao").count_documents({})
    v = current_client[DB_MATRICULA].get_collection("penascal-vitoria").count_documents({})
    return jsonify({"bilbao": b, "vitoria": v, "total": b + v})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

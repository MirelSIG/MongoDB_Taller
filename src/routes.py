from pathlib import Path
from flask import Blueprint, jsonify, render_template_string, request
from pymongo.errors import OperationFailure, PyMongoError
from .config import (
    MONGO_URI, DB_MATRICULA, DB_DOCENTES, DB_SOCIOS, DB_PROVEEDORES, DATASETS
)
from .templates import INDEX_HTML
from .utils import read_ndjson, serialize, require_client

bp = Blueprint("main", __name__)


def get_client(app):
    """Función para obtener el cliente de MongoDB desde el contexto de la app."""
    return app.extensions.get("mongo_client")


@bp.get("/")
def home():
    from flask import current_app
    client = get_client(current_app)
    return render_template_string(
        INDEX_HTML,
        db_matricula=DB_MATRICULA,
        db_docentes=DB_DOCENTES,
        db_socios=DB_SOCIOS,
        db_proveedores=DB_PROVEEDORES,
    )


@bp.get("/health")
def health():
    from flask import current_app
    client = get_client(current_app)
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


@bp.post("/seed")
def seed():
    from flask import current_app
    current_client = get_client(current_app)
    current_client, err = require_client(current_client)
    if err:
        return err

    base = Path(__file__).resolve().parent.parent
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

    # Copia de apoyo para demo: $lookup trabaja sobre colecciones en la misma base.
    socios_docs = list(current_client[DB_SOCIOS].socios.find({}, {"_id": 0}))
    socios_lookup_col = current_client[DB_PROVEEDORES].socios
    socios_lookup_col.drop()
    if socios_docs:
        socios_lookup_col.insert_many(socios_docs)
    imported["socios_lookup_en_proveedores"] = {
        "ok": True,
        "database": DB_PROVEEDORES,
        "collection": "socios",
        "count": len(socios_docs),
    }

    return jsonify({"ok": True, "collections": imported})


@bp.get("/api/collections")
def list_collections():
    from flask import current_app
    current_client = get_client(current_app)
    current_client, err = require_client(current_client)
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


@bp.get("/api/socios")
def socios():
    from flask import current_app
    current_client = get_client(current_app)
    current_client, err = require_client(current_client)
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


@bp.get("/api/proveedores")
def proveedores():
    from flask import current_app
    current_client = get_client(current_app)
    current_client, err = require_client(current_client)
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


@bp.get("/api/join/proveedores-socios")
def join_proveedores_socios():
    from flask import current_app
    current_client = get_client(current_app)
    current_client, err = require_client(current_client)
    if err:
        return err

    rows = list(
        current_client[DB_PROVEEDORES].proveedores.aggregate(
            [
                {
                    "$lookup": {
                        "from": "socios",
                        "localField": "ciudad",
                        "foreignField": "ciudad",
                        "as": "socios_relacionados",
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id": 1,
                        "nombre": 1,
                        "ciudad": 1,
                        "total_socios_relacionados": {"$size": "$socios_relacionados"},
                    }
                },
                {"$sort": {"id": 1}},
                {"$limit": 100},
            ]
        )
    )
    return jsonify({"count": len(rows), "items": rows})


@bp.get("/api/test/lookup-cross-db")
def test_lookup_cross_db():
    """Prueba de $lookup entre bases diferentes (Atlas feature)."""
    from flask import current_app
    current_client = get_client(current_app)
    current_client, err = require_client(current_client)
    if err:
        return err

    try:
        # Intento 1: Sintaxis database.collection
        rows = list(
            current_client[DB_PROVEEDORES].proveedores.aggregate(
                [
                    {
                        "$lookup": {
                            "from": f"{DB_SOCIOS}.socios",
                            "localField": "ciudad",
                            "foreignField": "ciudad",
                            "as": "socios_ciudad",
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "id": 1,
                            "nombre": 1,
                            "ciudad": 1,
                            "total_socios": {"$size": "$socios_ciudad"},
                        }
                    },
                    {"$limit": 5},
                ]
            )
        )
        return jsonify({
            "ok": True,
            "metodo": "database.collection syntax",
            "count": len(rows),
            "items": rows,
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e),
            "metodo": "database.collection syntax",
            "hint": "Si falla, Atlas quizá no soporta this syntax o requiere permisos especiales",
        }), 400


@bp.get("/api/matricula/resumen")
def matricula_resumen():
    from flask import current_app
    current_client = get_client(current_app)
    current_client, err = require_client(current_client)
    if err:
        return err

    b = current_client[DB_MATRICULA].get_collection("penascal-bilbao").count_documents({})
    v = current_client[DB_MATRICULA].get_collection("penascal-vitoria").count_documents({})
    return jsonify({"bilbao": b, "vitoria": v, "total": b + v})

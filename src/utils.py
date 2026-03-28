import json
from pathlib import Path
from flask import jsonify


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


def require_client(client):
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

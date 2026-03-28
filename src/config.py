import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_MATRICULA = os.getenv("ATLAS_DB_MATRICULA", "penascal-matricula")
DB_DOCENTES = os.getenv("ATLAS_DB_DOCENTES", "penascal-docentes")
DB_SOCIOS = os.getenv("ATLAS_DB_SOCIOS", "penascal-socios")
DB_PROVEEDORES = os.getenv("ATLAS_DB_PROVEEDORES", "penascal-proveedores")

DATASETS = [
    ("socios", DB_SOCIOS, "socios", "penascal-socios.socios.ndjson"),
    ("proveedores", DB_PROVEEDORES, "proveedores", "penascal-proveedores.proveedores.ndjson"),
    ("docentes", DB_DOCENTES, "profesores", "penascal-docentes.profesores.ndjson"),
    ("matricula_bilbao", DB_MATRICULA, "penascal-bilbao", "penascal-matricula.penascal-bilbao.ndjson"),
    ("matricula_vitoria", DB_MATRICULA, "penascal-vitoria", "penascal-matricula.penascal-vitoria.ndjson"),
]

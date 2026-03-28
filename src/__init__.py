from flask import Flask
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError
from flask import jsonify
from .config import MONGO_URI
from .routes import bp


def create_app():
    app = Flask(__name__)
    
    # Inicializar cliente de MongoDB
    client = MongoClient(MONGO_URI) if MONGO_URI else None
    app.extensions = {"mongo_client": client}
    
    # Manejador de errores de PyMongo
    @app.errorhandler(PyMongoError)
    def handle_pymongo_error(exc):
        message = str(exc)
        hint = "Verifica usuario/password de Atlas y que el password este URL-encoded si tiene caracteres especiales."
        status = 500
        if isinstance(exc, OperationFailure):
            status = 401
            hint = "Credenciales Atlas invalidas o usuario sin permisos para la base solicitada."
        return jsonify({"ok": False, "error": message, "hint": hint}), status
    
    # Registrar blueprint de rutas
    app.register_blueprint(bp)
    
    return app

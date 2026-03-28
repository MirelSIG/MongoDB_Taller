"""
Punto de entrada de la aplicación Flask.
La lógica y módulos están en src/ para mejor organización.
"""
from src import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

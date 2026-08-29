import os

import requests
from flask import Flask, render_template

WS_PEDIDOS = os.environ.get("WS_PEDIDOS", "http://localhost:9090")

app = Flask(__name__)


@app.template_filter("plata")
def plata(monto):
    """48000 -> $48.000, con el separador de miles chileno."""
    return "$" + f"{monto:,}".replace(",", ".")


@app.route("/")
def catalogo():
    try:
        productos = requests.get(f"{WS_PEDIDOS}/productos", timeout=5).json()
    except requests.RequestException as e:
        return render_template("sin_backend.html", detalle=str(e)), 503

    return render_template(
        "catalogo.html",
        disponibles=[p for p in productos if p["stock"] > 0],
        idos=[p for p in productos if p["stock"] == 0],
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
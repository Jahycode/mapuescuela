import os

import requests
from flask import Flask, abort, redirect, render_template, request, session, url_for

WS_PEDIDOS = os.environ.get("WS_PEDIDOS", "http://localhost:9090")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-solo-para-desarrollo")


CONDICIONES = {
    "nuevo": "Como nuevo",
    "bueno": "Bueno",
    "detalles": "Con detalles",
    "restaurar": "Para restaurar",
}

ROTULO_MEDIDA = {
    "libros": "Envío",
    "juguetes": "Edad",
    "otros": "Detalle",
}


@app.template_filter("plata")
def plata(monto):
    """48000 -> $48.000, con el separador de miles chileno."""
    return "$" + f"{monto:,}".replace(",", ".")


@app.template_filter("etiqueta_condicion")
def etiqueta_condicion(codigo):
    """El código vive en la base porque sirve para filtrar; la etiqueta se escribe acá."""
    return CONDICIONES.get(codigo, codigo)


@app.template_filter("rotulo_medida")
def rotulo_medida(categoria):
    """La columna medida guarda cosas distintas segun el tipo de objeto."""
    return ROTULO_MEDIDA.get(categoria, "Medidas")


@app.errorhandler(requests.RequestException)
def sin_backend(e):
    """Si ws-pedidos no responde, una pagina que lo explica en vez de un stack trace."""
    return render_template("sin_backend.html", detalle=str(e)), 503


def productos():
    """La web no guarda nada por su cuenta: el catalogo se le pregunta a ws-pedidos."""
    return requests.get(f"{WS_PEDIDOS}/productos", timeout=5).json()


@app.get("/")
def catalogo():
    todos = productos()
    return render_template(
        "catalogo.html",
        disponibles=[p for p in todos if p["stock"] > 0],
        idos=[p for p in todos if p["stock"] == 0],
        seleccionados=session.get("seleccion", []),
    )


@app.post("/seleccion/<int:producto_id>")
def agregar(producto_id):
    seleccion = session.get("seleccion", [])
    if producto_id not in seleccion:
        seleccion.append(producto_id)
        session["seleccion"] = seleccion
    return redirect(url_for("checkout"))


@app.post("/seleccion/<int:producto_id>/quitar")
def quitar(producto_id):
    session["seleccion"] = [i for i in session.get("seleccion", []) if i != producto_id]
    return redirect(url_for("checkout"))


def ver_checkout(error=None):
    seleccion = session.get("seleccion", [])
    por_id = {p["id"]: p for p in productos()}

    elegidos = [por_id[i] for i in seleccion if i in por_id]
    disponibles = [p for p in elegidos if p["stock"] > 0]

    return render_template(
        "checkout.html",
        elegidos=disponibles,
        tomados=[p for p in elegidos if p["stock"] == 0],
        total=sum(p["precio"] for p in disponibles),
        error=error,
    )

@app.get("/checkout")
def checkout():
    return ver_checkout()

@app.post("/reservar")
def reservar():
    seleccion = session.get("seleccion", [])
    if not seleccion:
        return redirect(url_for("catalogo"))

    respuesta = requests.post(
        f"{WS_PEDIDOS}/pedidos",
        json={
            "clienteNombre": request.form.get("nombre", "").strip(),
            "clienteEmail": request.form.get("correo", "").strip(),
            "modalidadEntrega": "retiro",
            "items": [{"productoId": i} for i in seleccion],
        },
        timeout=5,
    )

    if respuesta.status_code != 201:
        return ver_checkout(error=respuesta.json().get("error")), 400

    session["seleccion"] = []
    return redirect(url_for("seguimiento", pedido_id=respuesta.json()["id"]))

@app.get("/pedido/<int:pedido_id>")
def seguimiento(pedido_id):
    respuesta = requests.get(f"{WS_PEDIDOS}/pedidos/{pedido_id}", timeout=5)

    if respuesta.status_code == 404:
        abort(404)

    return render_template("seguimiento.html", pedido=respuesta.json())




if __name__ == "__main__":
    app.run(port=5000, debug=True)
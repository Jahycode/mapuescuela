import os

import requests
from flask import Flask, abort, redirect, render_template, request, session, url_for
from flowable_client import arrancar_instancia, tareas_pendientes

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

# Cada tarea humana se dibuja segun su grupo. El formKey lo declara el BPMN.
GRUPOS_TAREA = {
    "adjuntarComprobante": "comprobante",
    "revisionDelPago": "comprobante",
    "preparacionDelPedido": "preparar",
    "avisoDeRetiroListo": "entrega",
    "registroDelRetiro": "entrega",
    "datosDelEnvio": "despacho",
    "despachoPorVoluntario": "despacho",
    "gestionDelDespacho": "despacho",
}

# Como se le nombra cada grupo a la voluntaria. El formKey es nombre interno.
ETIQUETA_GRUPO = {
    "comprobante": "Pago",
    "preparar": "Preparación",
    "despacho": "Despacho",
    "entrega": "Entrega",
}

# Desde cuando una tarea se muestra apurada o atrasada. El plazo de pago es de
# 24 horas, asi que a las doce ya va la mitad del reloj corriendo.
APURA_MIN = 4 * 60
ATRASADO_MIN = 12 * 60


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


@app.template_filter("rotulo_grupo")
def rotulo_grupo(grupo):
    """El formKey es nombre interno; en pantalla va la etiqueta."""
    return ETIQUETA_GRUPO.get(grupo, "Tarea")


@app.template_filter("espera")
def espera(minutos):
    """125 -> 2 h 05 min. Los minutos los calcula flowable_client."""
    horas, resto = divmod(minutos, 60)
    return f"{horas} h {resto:02d} min" if horas else f"{resto} min"


@app.errorhandler(requests.RequestException)
def sin_backend(e):
    """Si ws-pedidos no responde, una pagina que lo explica en vez de un stack trace."""
    return render_template("sin_backend.html", detalle=str(e)), 503


def productos():
    """La web no guarda nada por su cuenta: el catalogo se le pregunta a ws-pedidos."""
    return requests.get(f"{WS_PEDIDOS}/productos", timeout=5).json()


def pedidos():
    """La web no guarda nada por su cuenta: el catalogo se le pregunta a ws-pedidos."""
    return requests.get(f"{WS_PEDIDOS}/pedidos", timeout=5).json()

@app.get("/")
def catalogo():
    todos = productos()
    seleccion = session.get("seleccion", [])
    elegidos = [p for p in todos if p["id"] in seleccion]

    return render_template(
        "catalogo.html",
        disponibles=[p for p in todos if p["stock"] > 0],
        idos=[p for p in todos if p["stock"] == 0],
        seleccionados=seleccion,
        elegidos=elegidos,
        total_elegido=sum(p["precio"] for p in elegidos),
    )


@app.post("/seleccion/<int:producto_id>")
def agregar(producto_id):
    seleccion = session.get("seleccion", [])
    if producto_id not in seleccion:
        seleccion.append(producto_id)
        session["seleccion"] = seleccion

    return redirect(url_for("catalogo") + f"#objeto-{producto_id}")


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

    pedido = respuesta.json()
    session["seleccion"] = []

    instancia = arrancar_instancia(pedido["id"], pedido["modalidadEntrega"])

    requests.put(
        f"{WS_PEDIDOS}/pedidos/{pedido['id']}/instancia",
        json={"processInstanceId": instancia},
        timeout=5,
    )

    return redirect(url_for("seguimiento", pedido_id=pedido["id"]))

@app.get("/pedido/<int:pedido_id>")
def seguimiento(pedido_id):
    respuesta = requests.get(f"{WS_PEDIDOS}/pedidos/{pedido_id}", timeout=5)

    if respuesta.status_code == 404:
        abort(404)

    return render_template("seguimiento.html", pedido=respuesta.json())


def urgencia(espera_min):
    """En que tramo cae una tarea segun lo que lleva esperando."""
    if espera_min >= ATRASADO_MIN:
        return "atrasado"
    if espera_min >= APURA_MIN:
        return "apura"
    return "normal"


@app.get("/bandeja")
def bandeja():
    """Las tareas pendientes: el motor dice cuales son, ws-pedidos de que tratan"""
    por_id = {p["id"]: p for p in pedidos()}

    tareas = []
    for tarea in tareas_pendientes():
        pedido = por_id.get(tarea["pedido_id"])
        if pedido is None:
            continue
        tarea["pedido"] = pedido
        tarea["grupo"] = GRUPOS_TAREA.get(tarea["form_key"], "entrega")
        tarea["urgencia"] = urgencia(tarea["espera_min"])
        tareas.append(tarea)

    tareas.sort(key=lambda t: t["espera_min"], reverse=True)

    elegida = request.args.get("tarea")
    seleccionada = next((t for t in tareas if t["id"] == elegida), None)

    # Los objetos solo se piden cuando hay una tarea abierta: la lista no los usa.
    objetos = []
    if seleccionada:
        pedido_id = seleccionada["pedido_id"]
        detalle = requests.get(f"{WS_PEDIDOS}/pedidos/{pedido_id}", timeout=5).json()
        objetos = detalle.get("items", [])

    return render_template(
        "bandeja.html",
        tareas=tareas,
        atrasadas=sum(1 for t in tareas if t["urgencia"] == "atrasado"),
        seleccionada=seleccionada,
        objetos=objetos,
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)

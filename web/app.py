import os
import time
from datetime import datetime

from dotenv import load_dotenv

# Antes de importar flowable_client: lee las variables al cargarse.
load_dotenv()

import requests
from flask import (Flask, Response, abort, flash, redirect, render_template, request,
                   session, url_for)
from flowable_client import (
    arrancar_instancia,
    completar_tarea,
    fin_del_proceso,
    instancia_de_tarea,
    tarea_activa,
    tareas_pendientes,
)

WS_PEDIDOS = os.environ.get("WS_PEDIDOS", "http://localhost:9090")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-solo-para-desarrollo")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


CONDICIONES = {
    "nuevo": "Como nuevo",
    "bueno": "Bueno",
    "detalles": "Con detalles",
    "restaurar": "Para restaurar",
}

TIPOS_DE_CUENTA = ("Cuenta Corriente", "Cuenta Vista", "Cuenta RUT", "Cuenta de Ahorro")

CATEGORIAS = {
    "muebles": "Muebles",
    "libros": "Libros",
    "juguetes": "Juguetes",
    "otros": "Otros",
}

ROTULO_MEDIDA = {
    "libros": "Envío",
    "juguetes": "Edad",
    "otros": "Detalle",
}

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

# Quienes atienden la bandeja. Cada accion queda firmada con este nombre.
# Quienes atienden la bandeja, con su clave. No es un sistema de autenticacion:
# no hay hash, ni roles, ni recuperacion. Es una llave para que la pantalla que
# aprueba pagos no quede abierta a quien tenga el link. Cambiarlo por una tabla
# de usuarios seria reemplazar este diccionario y la comparacion de mas abajo.
VOLUNTARIAS = {
    "Ana Millán": "ana",
    "Diego Paredes": "diego",
    "Rosa Yáñez": "rosa",
}
# Las dos formas de entrega que el proceso sabe manejar.
MODALIDADES = ("retiro", "despacho")

ERRORES = {
    "mensaje": "Para no aprobar el pago hay que escribirle algo al cliente.",
    "envio": "Faltan el transportista o la dirección.",
}

# Como se le nombra cada grupo a la voluntaria. El formKey es nombre interno.
ETIQUETA_GRUPO = {
    "comprobante": "Pago",
    "preparar": "Preparación",
    "despacho": "Despacho",
    "entrega": "Entrega",
}

# En que tramo de la barra cae cada tarea. Va por formKey y no por grupo:
# los grupos existen para los iconos y agrupan de otra manera.
TRAMO_DEL_FORM = {
    "adjuntarComprobante": 0,
    "revisionDelPago": 0,
    "preparacionDelPedido": 1,
    "avisoDeRetiroListo": 2,
    "gestionDelDespacho": 2,
    "registroDelRetiro": 3,
    "despachoPorVoluntario": 3,
    "datosDelEnvio": 3,
}

NOMBRES_DE_TRAMO = {
    "retiro": ("Pago", "Preparación", "Listo para retirar", "Retiro"),
    "despacho": ("Pago", "Preparación", "Despacho", "Entrega"),
}

# Los tres finales buenos del modelo. Los malos los escribe el worker.
DESENLACE_DEL_FINAL = {
    "EndNoneEvent_31": "RETIRADO",
    "EndNoneEvent_37": "DESPACHADO_VOLUNTARIO",
    "EndNoneEvent_41": "DESPACHADO_COURIER",
}

VENTAS_CERRADAS = ("RETIRADO", "DESPACHADO_VOLUNTARIO", "DESPACHADO_COURIER")

ROTULO_DESENLACE = {
    "RETIRADO": "Retirado en la sede",
    "DESPACHADO_VOLUNTARIO": "Lo llevó un voluntario",
    "DESPACHADO_COURIER": "Salió por courier",
    "RECHAZADO": "Pago no aprobado",
    "CANCELADO_VENCIMIENTO": "Se venció el plazo",
    "SIN_STOCK": "El objeto ya no estaba",
}

MESES = ("ene", "feb", "mar", "abr", "may", "jun",
         "jul", "ago", "sep", "oct", "nov", "dic")

# Desde cuando una tarea se muestra apurada o atrasada. El plazo de pago es de
# 24 horas, asi que a las doce ya va la mitad del reloj corriendo.
# Cuantos vendidos se muestran en el catalogo.
IDOS_A_LA_VISTA = 8

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


@app.template_filter("iniciales")
def iniciales(nombre):
    """Ana Millán -> AM, para el circulito del encabezado."""
    return "".join(parte[0] for parte in nombre.split()[:2]).upper()


@app.template_filter("rotulo_grupo")
def rotulo_grupo(grupo):
    """El formKey es nombre interno; en pantalla va la etiqueta."""
    return ETIQUETA_GRUPO.get(grupo, "Tarea")


@app.template_filter("espera")
def espera(minutos):
    """125 -> 2 h 05 min. Los minutos los calcula flowable_client."""
    horas, resto = divmod(minutos, 60)
    return f"{horas} h {resto:02d} min" if horas else f"{resto} min"


@app.template_filter("rotulo_desenlace")
def rotulo_desenlace(valor):
    return ROTULO_DESENLACE.get(valor, valor)


@app.template_filter("fecha")
def fecha(marca):
    """De la marca ISO que manda ws-pedidos a algo corto: 2 sep, 14:30."""
    if not marca:
        return "—"

    momento = datetime.fromisoformat(marca[:19])
    return f"{momento.day} {MESES[momento.month - 1]}, {momento:%H:%M}"


def destino_seguro(ruta):
    """Solo rutas de esta aplicacion. Un 'volver' que empiece con http:// o con //
    mandaria a otro sitio, y el enlace lo escribe quien quiera."""
    if ruta and ruta.startswith("/") and not ruta.startswith("//"):
        return ruta
    return url_for("bandeja")


@app.before_request
def pedir_la_llave():
    """Todo lo interno pide la llave; el catalogo y la pagina del pedido no.
    Va por prefijo y en un solo lugar: con un decorador por ruta, la que se
    agregue manana queda abierta y nadie se entera."""
    if not (request.path.startswith("/bandeja") or request.path.startswith("/admin")):
        return None

    if "voluntaria" in session:
        return None

    # full_path deja un '?' colgando cuando no hay parametros.
    return redirect(url_for("entrar", volver=request.full_path.rstrip("?")))


@app.get("/entrar")
def entrar():
    return render_template(
        "entrar.html", voluntarias=VOLUNTARIAS, elegida=None, error=None,
        volver=request.args.get("volver", ""),
    )


@app.post("/entrar")
def validar_la_llave():
    quien = request.form.get("voluntaria", "")
    clave = request.form.get("clave", "")

    if not clave or VOLUNTARIAS.get(quien) != clave:
        return render_template(
            "entrar.html", voluntarias=VOLUNTARIAS, elegida=quien,
            error="Esa clave no es. Intenta de nuevo.",
            volver=request.form.get("volver", ""),
        ), 401

    session["voluntaria"] = quien
    return redirect(destino_seguro(request.form.get("volver")))


@app.post("/salir")
def salir():
    """Devuelve a la entrada y no al catalogo: lo normal al salir es que entre otra."""
    session.pop("voluntaria", None)
    return redirect(url_for("entrar"))


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

    # Los vendidos son prueba social, no un inventario: con cien la pagina se hace
    # impasable. Se muestran los ultimos y el total dice el resto.
    idos = [p for p in todos if p["stock"] == 0]
    idos.sort(key=lambda p: p["id"], reverse=True)
    # Solo los que siguen disponibles: otra persona pudo llevarse alguno.
    elegidos = [p for p in todos if p["id"] in seleccion and p["stock"] > 0]

    return render_template(
        "catalogo.html",
        org=organizacion(),
        disponibles=[p for p in todos if p["stock"] > 0],
        idos=idos[:IDOS_A_LA_VISTA],
        idos_total=len(idos),
        seleccionados=[p["id"] for p in elegidos],
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
    tomados = [p for p in elegidos if p["stock"] == 0]

    # Esta es la unica pantalla que avisa que un objeto se perdio, asi que
    # es acá donde hay que sacarlo de la seleccion: si no, el catalogo lo
    # sigue contando para siempre. Reasignar es lo que marca la sesion.
    if tomados:
        session["seleccion"] = [p["id"] for p in disponibles]

    return render_template(
        "checkout.html",
        org=organizacion(),
        elegidos=disponibles,
        tomados=tomados,
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

    modalidad = request.form.get("entrega")
    if modalidad not in MODALIDADES:
        modalidad = "retiro"

    respuesta = requests.post(
        f"{WS_PEDIDOS}/pedidos",
        json={
            "clienteNombre": request.form.get("nombre", "").strip(),
            "clienteEmail": request.form.get("correo", "").strip(),
            "modalidadEntrega": modalidad,
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

    pedido = respuesta.json()

    instancia = pedido.get("processInstanceId")
    tarea = tarea_activa(instancia) if instancia else None

    return render_template(
        "seguimiento.html", pedido=pedido, tarea=tarea, org=organizacion()
    )


def cerrar_pedido(pedido_id, final):
    """Los tres finales buenos no pasan por el worker: el desenlace lo escribe
    la web cuando el motor confirma en que evento de fin termino."""
    valor = DESENLACE_DEL_FINAL.get(final)
    if valor is None:
        return

    requests.post(
        f"{WS_PEDIDOS}/pedidos/{pedido_id}/desenlace",
        json={"valor": valor},
        timeout=5,
    ).raise_for_status()


def esperar_la_siguiente(instancia, segundos=6):
    """Si el paso que sigue es automatico, el motor tarda en publicar la tarea
    humana posterior. Esperamos acá en vez de mandar a la bandeja vacia."""
    limite = time.monotonic() + segundos

    while True:
        siguiente = tarea_activa(instancia)
        if siguiente:
            return siguiente
        if fin_del_proceso(instancia)["terminado"] or time.monotonic() >= limite:
            return None
        time.sleep(0.4)


def seguir_en_el_pedido(instancia, pedido_id, hecho):
    """Deja abierta la siguiente tarea del mismo pedido. Si el proceso termino,
    escribe el desenlace en la base antes de soltar a la lista."""
    siguiente = esperar_la_siguiente(instancia) if instancia else None

    if siguiente:
        flash(f"{hecho} Sigue: «{siguiente['nombre']}».")
        return redirect(url_for("bandeja", tarea=siguiente["id"]))

    fin = fin_del_proceso(instancia) if instancia else {"terminado": True, "final": None}

    if not fin["terminado"]:
        flash(f"{hecho} El sistema sigue trabajando en el paso siguiente.")
        return redirect(url_for("bandeja", espera=1))

    cerrar_pedido(pedido_id, fin["final"])
    flash(f"{hecho} Este pedido quedó cerrado.")
    return redirect(url_for("bandeja"))


def urgencia(espera_min):
    """En que tramo cae una tarea segun lo que lleva esperando."""
    if espera_min >= ATRASADO_MIN:
        return "atrasado"
    if espera_min >= APURA_MIN:
        return "apura"
    return "normal"


def fases_del_pedido(form_key, modalidad):
    """Los cuatro tramos por los que pasa todo pedido, y en cual va este."""
    actual = TRAMO_DEL_FORM.get(form_key, 0)
    nombres = NOMBRES_DE_TRAMO["despacho" if modalidad == "despacho" else "retiro"]

    return [
        {
            "numero": i + 1,
            "nombre": nombre,
            "estado": "hecho" if i < actual else ("ahora" if i == actual else "pendiente"),
        }
        for i, nombre in enumerate(nombres)
    ]


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
    fases = []
    if seleccionada:
        pedido_id = seleccionada["pedido_id"]
        detalle = requests.get(f"{WS_PEDIDOS}/pedidos/{pedido_id}", timeout=5).json()
        objetos = detalle.get("items", [])
        fases = fases_del_pedido(
            seleccionada["form_key"], seleccionada["pedido"].get("modalidadEntrega")
        )

    return render_template(
        "bandeja.html",
        tareas=tareas,
        atrasadas=sum(1 for t in tareas if t["urgencia"] == "atrasado"),
        seleccionada=seleccionada,
        objetos=objetos,
        fases=fases,
        voluntaria=session["voluntaria"],
        error=ERRORES.get(request.args.get("error")),
        esperando=request.args.get("espera"),
    )


@app.get("/objeto/<int:producto_id>/foto")
def foto_objeto(producto_id):
    """El navegador nunca le pide la imagen a ws-pedidos: la sirve la web, igual
    que todo lo demas. Asi el cliente conoce una sola direccion.

    La plantilla agrega ?v= con el nombre del archivo, que lleva la marca de tiempo
    de la subida. Sin eso, cambiar la foto no cambiaria la direccion y el navegador
    seguiria mostrando la vieja hasta que venza el cache."""
    respuesta = requests.get(f"{WS_PEDIDOS}/productos/{producto_id}/foto", timeout=10)

    if respuesta.status_code != 200:
        abort(404)

    return Response(
        respuesta.content,
        mimetype=respuesta.headers.get("Content-Type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=86400"},
    )


CAMPOS_OBJETO = ("nombre", "categoria", "condicion", "marcaUso")


def dimensiones(medida):
    """De '78×90×45' a ('78', '90', '45'). Si la medida no son numeros
    —los libros dicen 'Encomienda'— devuelve las tres vacias."""
    partes = [p.strip() for p in (medida or "").split("×")]

    if not partes or not all(p.isdigit() for p in partes):
        return ("", "", "")

    return tuple((partes + ["", "", ""])[:3])


def medida_del_formulario(actual=""):
    """Alto, ancho y fondo en centimetros, en ese orden. Paro en el primero
    que venga vacio: '78×45' se leeria como alto por ancho y seria mentira."""
    valores = []

    for campo in ("alto", "ancho", "fondo"):
        valor = request.form.get(campo, "").strip()
        if not valor.isdigit():
            break
        valores.append(valor)

    # Sin numeros no borro lo que hubiera: puede decir 'Encomienda' o '2 a 5 anos'.
    return "×".join(valores) if valores else actual


def organizacion():
    """Los datos de la agrupacion. Viven en ws-pedidos, no en las plantillas."""
    return requests.get(f"{WS_PEDIDOS}/organizacion", timeout=5).json()


CAMPOS_ORGANIZACION = (
    "nombre", "lema", "direccion", "comuna", "correo", "instagram",
    "banco", "tipoCuenta", "numeroCuenta", "rut", "titular",
)


@app.get("/admin/organizacion")
def admin_organizacion():
    return render_template(
        "admin_organizacion.html", org=organizacion(),
        tipos=TIPOS_DE_CUENTA, error=None,
    )


@app.post("/admin/organizacion")
def guardar_organizacion():
    datos = {c: request.form.get(c, "").strip() for c in CAMPOS_ORGANIZACION}
    respuesta = requests.put(f"{WS_PEDIDOS}/organizacion", json=datos, timeout=5)

    if respuesta.status_code != 200:
        return render_template(
            "admin_organizacion.html", org=datos, tipos=TIPOS_DE_CUENTA,
            error=respuesta.json().get("error"),
        ), 400

    flash("Datos de la agrupación guardados.")
    return redirect(url_for("admin_organizacion"))


def objeto_del_formulario(actual=None):
    """Lo que llego escrito, listo para mandarselo a ws-pedidos."""
    actual = actual or {}
    datos = {c: request.form.get(c, "").strip() for c in CAMPOS_OBJETO}

    datos["medida"] = medida_del_formulario(actual.get("medida", ""))

    precio = request.form.get("precio", "").replace(".", "").strip()
    datos["precio"] = int(precio) if precio.isdigit() else 0

    return datos


def guardar_la_foto(producto_id):
    """Sube la foto si venia una. Devuelve el problema, o None si todo bien.
    Va despues de crear el objeto: sin id no hay donde colgarla."""
    archivo = request.files.get("foto")

    if archivo is None or not archivo.filename:
        return None

    respuesta = requests.post(
        f"{WS_PEDIDOS}/productos/{producto_id}/foto",
        data=archivo.read(),
        headers={"Content-Type": archivo.mimetype},
        timeout=20,
    )

    if respuesta.status_code != 201:
        return respuesta.json().get("error", "no se pudo guardar")
    return None


def ver_formulario(objeto=None, error=None, codigo=200):
    alto, ancho, fondo = dimensiones(objeto.get("medida") if objeto else "")

    return render_template(
        "admin_objeto.html", objeto=objeto, error=error,
        categorias=CATEGORIAS, condiciones=CONDICIONES,
        alto=alto, ancho=ancho, fondo=fondo,
    ), codigo


@app.get("/admin/objetos/nuevo")
def nuevo_objeto():
    return ver_formulario()


@app.post("/admin/objetos")
def crear_objeto():
    datos = objeto_del_formulario()
    respuesta = requests.post(f"{WS_PEDIDOS}/productos", json=datos, timeout=5)

    if respuesta.status_code != 201:
        return ver_formulario(datos, respuesta.json().get("error"), 400)

    creado = respuesta.json()
    problema = guardar_la_foto(creado["id"])

    aviso = f"«{creado['nombre']}» quedó en el registro con el N° {creado['id']:04d}."
    flash(aviso + (f" La foto no se guardó: {problema}" if problema else ""))
    return redirect(url_for("admin_objetos"))


@app.get("/admin/objetos/<int:producto_id>")
def editar_objeto(producto_id):
    objetos = requests.get(
        f"{WS_PEDIDOS}/productos", params={"incluirRetirados": "true"}, timeout=5
    ).json()
    objeto = next((o for o in objetos if o["id"] == producto_id), None)

    if objeto is None:
        abort(404)

    return ver_formulario(objeto)


@app.post("/admin/objetos/<int:producto_id>")
def guardar_objeto(producto_id):
    objetos = requests.get(
        f"{WS_PEDIDOS}/productos", params={"incluirRetirados": "true"}, timeout=5
    ).json()
    actual = next((o for o in objetos if o["id"] == producto_id), None)

    if actual is None:
        abort(404)

    datos = objeto_del_formulario(actual)
    respuesta = requests.put(f"{WS_PEDIDOS}/productos/{producto_id}", json=datos, timeout=5)

    if respuesta.status_code != 200:
        return ver_formulario({**datos, "id": producto_id}, respuesta.json().get("error"), 400)

    problema = guardar_la_foto(producto_id)

    aviso = f"Guardé los cambios del N° {producto_id:04d}."
    flash(aviso + (f" La foto no se guardó: {problema}" if problema else ""))
    return redirect(url_for("admin_objetos"))


@app.get("/admin/objetos")
def admin_objetos():
    """Todo el registro, incluidos los retirados, para administrarlo."""
    objetos = requests.get(
        f"{WS_PEDIDOS}/productos", params={"incluirRetirados": "true"}, timeout=5
    ).json()
    objetos.sort(key=lambda o: o["id"], reverse=True)

    return render_template(
        "admin_objetos.html",
        objetos=objetos,
        disponibles=sum(1 for o in objetos if o["stock"] > 0 and not o["retirado"]),
        vendidos=sum(1 for o in objetos if o["stock"] == 0),
        retirados=sum(1 for o in objetos if o["retirado"]),
    )


@app.post("/admin/objetos/<int:producto_id>/retiro")
def retirar_objeto(producto_id):
    """Retirar no borra: los pedidos viejos siguen apuntando a este objeto."""
    retirado = request.form.get("retirado") == "si"

    requests.post(
        f"{WS_PEDIDOS}/productos/{producto_id}/retiro",
        json={"retirado": retirado},
        timeout=5,
    ).raise_for_status()

    flash("Objeto retirado del registro." if retirado
          else "El objeto volvió al registro.")
    return redirect(url_for("admin_objetos"))


@app.get("/bandeja/historico")
def historico():
    """Lo que ya termino: las ventas cerradas y las que se perdieron."""
    cerrados = [p for p in pedidos() if p.get("desenlace")]
    cerrados.sort(key=lambda p: p.get("desenlaceEn") or "", reverse=True)

    vendidos = [p for p in cerrados if p["desenlace"] in VENTAS_CERRADAS]

    return render_template(
        "historico.html",
        cerrados=cerrados,
        ventas=VENTAS_CERRADAS,
        vendidos=len(vendidos),
        recaudado=sum(p["montoTotal"] for p in vendidos),
        perdidos=len(cerrados) - len(vendidos),
    )


@app.post("/bandeja/<tarea_id>/completar")
def completar(tarea_id):
    """Las seis tareas que no deciden nada: se cierran y el proceso sigue solo."""
    pedido_id = int(request.form["pedido_id"])
    instancia = instancia_de_tarea(tarea_id)
    completar_tarea(tarea_id)
    return seguir_en_el_pedido(instancia, pedido_id, "Tarea cerrada.")


@app.post("/bandeja/<tarea_id>/revision")
def revisar_pago(tarea_id):
    """Primero queda escrito quien decidio, despues avanza el motor. Ese orden importa:
    si ws-pedidos esta caido el proceso no avanza, en vez de avanzar sin dejar rastro."""
    pedido_id = int(request.form["pedido_id"])
    mensaje = request.form.get("mensaje", "").strip()

    # Sin una decision explicita no se hace nada. Es lo que hace inofensivo
    # apretar Enter dentro del formulario.
    decision = request.form.get("decision")
    if decision not in ("APROBADO", "CANCELADO"):
        return redirect(url_for("bandeja", tarea=tarea_id))

    aprobado = decision == "APROBADO"

    if not aprobado and not mensaje:
        return redirect(url_for("bandeja", tarea=tarea_id, error="mensaje"))

    revision = {
        "revisor": session["voluntaria"],
        "decision": "APROBADO" if aprobado else "CANCELADO",
    }
    if mensaje:
        revision["mensaje"] = mensaje

    leido = request.form.get("montoLeido", "").replace(".", "").strip()
    if leido.isdigit():
        revision["montoLeido"] = int(leido)

    requests.post(
        f"{WS_PEDIDOS}/pedidos/{pedido_id}/revision", json=revision, timeout=5
    ).raise_for_status()

    variables = [{"name": "esAprobado", "type": "boolean", "value": aprobado}]
    if not aprobado:
        variables.append({"name": "motivoRechazo", "value": mensaje})
    instancia = instancia_de_tarea(tarea_id)
    completar_tarea(tarea_id, variables)

    aviso = (
        f"Pago aprobado. Queda registrado a nombre de {revision['revisor']}."
        if aprobado
        else f"Pedido N° {pedido_id:04d} cancelado. Le vamos a avisar al cliente."
    )
    return seguir_en_el_pedido(instancia, pedido_id, aviso)


@app.post("/bandeja/<tarea_id>/despacho")
def elegir_despacho(tarea_id):
    """El gateway compara con 'COURIER'; cualquier otra cosa cae al voluntario por defecto."""
    tipo = request.form.get("tipoDespacho")
    if tipo not in ("COURIER", "VOLUNTARIO"):
        abort(400)

    pedido_id = int(request.form["pedido_id"])
    instancia = instancia_de_tarea(tarea_id)
    completar_tarea(tarea_id, [{"name": "tipoDespacho", "value": tipo}])

    aviso = "Va por courier." if tipo == "COURIER" else "Lo lleva un voluntario."
    return seguir_en_el_pedido(instancia, pedido_id, aviso)


@app.post("/bandeja/<tarea_id>/envio")
def registrar_envio(tarea_id):
    """Igual que la revision: primero queda escrito el envio, despues avanza el motor."""
    pedido_id = int(request.form["pedido_id"])

    envio = {
        "transportista": request.form.get("transportista", "").strip(),
        "direccion": request.form.get("direccion", "").strip(),
    }

    if not envio["transportista"] or not envio["direccion"]:
        return redirect(url_for("bandeja", tarea=tarea_id, error="envio"))

    numero = request.form.get("numeroSeguimiento", "").strip()
    if numero:
        envio["numeroSeguimiento"] = numero

    requests.post(
        f"{WS_PEDIDOS}/pedidos/{pedido_id}/envio", json=envio, timeout=5
    ).raise_for_status()

    instancia = instancia_de_tarea(tarea_id)
    completar_tarea(tarea_id)

    return seguir_en_el_pedido(instancia, pedido_id, "Datos del envío registrados.")

@app.post("/pedido/<int:pedido_id>/comprobante")
def subir_comprobante(pedido_id):
    """Guarda el comprobante y recien despues avanza el proceso, en ese orden."""
    archivo = request.files.get("comprobante")
    if archivo is None or not archivo.filename:
        flash("No llegó ninguna foto. Elige el archivo y vuelve a intentar.")
        return redirect(url_for("seguimiento", pedido_id=pedido_id))

    subida = requests.post(
        f"{WS_PEDIDOS}/pedidos/{pedido_id}/comprobante",
        data=archivo.read(),
        headers={"Content-Type": archivo.mimetype},
        timeout=15,
    )
    subida.raise_for_status()

    pedido = requests.get(f"{WS_PEDIDOS}/pedidos/{pedido_id}", timeout=5).json()
    instancia = pedido.get("processInstanceId")
    tarea = tarea_activa(instancia) if instancia else None

    if tarea and tarea["form_key"] == "adjuntarComprobante":
        completar_tarea(tarea["id"])

    flash("Recibimos tu comprobante. Te avisamos apenas lo revisemos.")
    return redirect(url_for("seguimiento", pedido_id=pedido_id))


if __name__ == "__main__":
    app.run(port=5000, debug=True)

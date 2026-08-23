import time
from config import ESPERA
from flowable_client import tomar, completar, fallar, soltar
from pedidos_client import descontar_stock, registrar_desenlace, registrar_notificacion

def descontar_inventario(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    stock_ok = descontar_stock(variables["pedidoId"])

    print(f"   pedido {variables['pedidoId']} -> stockOk = {stock_ok}")
    return [{"name": "stockOk", "value": stock_ok}]

def registrar_rechazo(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    registrar_desenlace(variables["pedidoId"], "RECHAZADO", variables.get("motivoRechazo"))
    print(f"   pedido {variables['pedidoId']} -> RECHAZADO")
    # time.sleep(15)
    return None

def notificar_cliente(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    registrar_notificacion(variables["pedidoId"], "PAGO_RECHAZADO")
    print(f"   pedido {variables['pedidoId']} -> aviso PAGO_RECHAZADO")
    return None

def cancelar_pedido_vencido(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    registrar_desenlace(variables["pedidoId"], "CANCELADO_VENCIMIENTO", "No llego el comprobante en el plazo")
    print(f"   pedido {variables['pedidoId']} -> CANCELADO_VENCIMIENTO")
    return None

def notificar_falta_stock(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    registrar_desenlace(variables["pedidoId"], "SIN_STOCK", "No habia unidades disponibles")
    registrar_notificacion(variables["pedidoId"], "SIN_STOCK")
    print(f"   pedido {variables['pedidoId']} -> SIN_STOCK")
    return None

HANDLERS = {
    "descontarInventario": descontar_inventario,
    "registrarRechazo": registrar_rechazo,
    "notificarCliente": notificar_cliente,
    "cancelarPedidoVencido": cancelar_pedido_vencido,
    "notificarFaltaStock": notificar_falta_stock,
}

print("Worker arriba.")

job = None

try:
    
    while True:
        hubo_trabajo = False

        for topic, handler in HANDLERS.items():
            job = None
            try:
                jobs = tomar(topic)
                if not jobs:
                    continue

                job = jobs[0]
                print(f"-> {topic}")

                variables = handler(job)
                completar(job["id"], variables)
                job = None
                hubo_trabajo = True

            except Exception as e:
                print(f"   ERROR en {topic}: {type(e).__name__}: {e}")

                if job is not None:
                    try:
                        fallar(job["id"], f"{type(e).__name__}: {e}"[:200])
                        print("   avise al motor: un reintento menos")
                    except Exception as e2:
                        print(f"   no pude avisarle al motor: {type(e2).__name__}: {e2}")
                    job = None

        if not hubo_trabajo:
            time.sleep(ESPERA)

except KeyboardInterrupt:
    print("\nApagando el worker...")
    if job is not None:
        try:
            soltar(job["id"])
            print(f"   devolvi a la cola el trabajo {job['id'][:8]}")
        except Exception as e:
            print(f"   no pude devolverlo: {type(e).__name__}: {e}")
    print("Detenido.")
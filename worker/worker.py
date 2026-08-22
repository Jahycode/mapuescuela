import time
from config import ESPERA
from flowable_client import tomar, completar
from pedidos_client import descontar_stock

def descontar_inventario(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    stock_ok = descontar_stock(variables["pedidoId"])

    print(f"   pedido {variables['pedidoId']} -> stockOk = {stock_ok}")
    return [{"name": "stockOk", "value": stock_ok}]

def registrar_rechazo(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    print(f" [pendiente] registrar el rechazo del pedido {variables['pedidoId']}")
    return None

def notificar_cliente(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    print(f" [pendiente] notificar a {variables['clienteEmail']}")
    return None

def cancelar_pedido_vencido(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    print(f" [pendiente] cancelar el pedido vencido {variables['pedidoId']}")
    return None

def notificar_falta_stock(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    print(f" [pendiente] notificar al cliente la falta de stock del pedido {variables['pedidoId']}")
    return None

HANDLERS = {
    "descontarInventario": descontar_inventario,
    "registrarRechazo": registrar_rechazo,
    "notificarCliente": notificar_cliente,
    "cancelarPedidoVencido": cancelar_pedido_vencido,
    "notificarFaltaStock": notificar_falta_stock,
}

print("Worker arriba.")

while True:
    hubo_trabajo = False

    for topic, handler in HANDLERS.items():
        jobs = tomar(topic)
        if not jobs:
            continue

        job = jobs[0]
        print(f"-> {topic}")
        variables = handler(job)
        completar(job["id"], variables)
        hubo_trabajo = True

    if not hubo_trabajo:
        time.sleep(ESPERA)
    
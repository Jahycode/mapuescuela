import requests
from config import WS_PEDIDOS

def descontar_stock(pedido_id):
    respuesta = requests.post(f"{WS_PEDIDOS}/pedidos/{pedido_id}/descontar-stock")
    respuesta.raise_for_status()
    return respuesta.json()["stockOk"]

def registrar_desenlace(pedido_id, valor, motivo=None):
    cuerpo = {"valor": valor}
    if motivo:
        cuerpo["motivo"] = motivo
    respuesta = requests.post(f"{WS_PEDIDOS}/pedidos/{pedido_id}/desenlace", json=cuerpo)
    respuesta.raise_for_status()  

def registrar_notificacion(pedido_id, tipo):
    respuesta = requests.post(f"{WS_PEDIDOS}/pedidos/{pedido_id}/notificaciones", json={"tipo": tipo})
    respuesta.raise_for_status()
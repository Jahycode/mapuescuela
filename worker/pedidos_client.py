import requests
from config import WS_PEDIDOS

def descontar_stock(pedido_id):
    respuesta = requests.post(f"{WS_PEDIDOS}/pedidos/{pedido_id}/descontar-stock")
    respuesta.raise_for_status()
    return respuesta.json()["stockOk"]
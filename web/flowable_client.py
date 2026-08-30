import os

import requests

FLOWABLE = os.environ.get("FLOWABLE", "http://localhost:8080/flowable-rest/service")
AUTH = ("rest-admin", "test")
PROCESO = "ventaMapuescuela"
PLAZO_PAGO = os.environ.get("PLAZO_PAGO", "PT24H")


def arrancar_instancia(pedido_id, modalidad_entrega):
    """Arranca el proceso en Flowable y devuelve el id de la instancia."""
    respuesta = requests.post(
        f"{FLOWABLE}/runtime/process-instances",
        auth=AUTH,
        json={
            "processDefinitionKey": PROCESO,
            "variables": [
                {"name": "pedidoId", "value": pedido_id, "type": "integer"},
                {"name": "plazoPago", "value": PLAZO_PAGO, "type": "string"},
                {"name": "modalidadEntrega", "value": modalidad_entrega.upper(), "type": "string"},
            ],
        },
        timeout=10,
    )
    respuesta.raise_for_status()
    return respuesta.json()["id"]
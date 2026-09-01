import os 
from datetime import datetime, timezone
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


def tareas_pendientes():
    """Devuelve las tareas humanas pendientes del proceso, ya normalizadas."""
    respuesta = requests.get(
        f"{FLOWABLE}/runtime/tasks",
        auth=AUTH,
        params={
            "processDefinitionKey": PROCESO,
            "includeProcessVariables": "true",
        },
        timeout=10,
    )
    respuesta.raise_for_status()

    ahora = datetime.now(timezone.utc)
    pendientes = []

    for tarea in respuesta.json()["data"]:
        variables = {v["name"]: v["value"] for v in tarea.get("variables", [])}
        if "pedidoId" not in variables:
            continue

        creada = datetime.fromisoformat(tarea["createTime"])
        pendientes.append({
            "id": tarea["id"],
            "nombre": tarea["name"],
            "form_key": tarea.get("formKey"),
            "pedido_id": variables["pedidoId"],
            "espera_min": int((ahora - creada).total_seconds() // 60),
        })

    return pendientes
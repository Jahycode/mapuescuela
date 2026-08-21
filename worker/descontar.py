import requests

FLOWABLE = "http://localhost:8080/flowable-rest"
WS_PEDIDOS = "http://localhost:9090"
AUTH = ("rest-admin", "test")
WORKER_ID = "worker-valentin"

cuerpo = {
    "topic": "descontarInventario",
    "workerId": WORKER_ID,
    "lockDuration": "PT30M",
    "numberOfTasks": 1
}

respuesta = requests.post(f"{FLOWABLE}/external-job-api/acquire/jobs", auth=AUTH, json=cuerpo)
respuesta.raise_for_status()

job = respuesta.json()[0]

variables = {v["name"]: v["value"] for v in job["variables"]}
pedido_id = variables["pedidoId"]

print("Pedido a descontar:", pedido_id)

r2 = requests.post(f"{WS_PEDIDOS}/pedidos/{pedido_id}/descontar-stock")
r2.raise_for_status()

stock_ok = r2.json()["stockOk"]
print("stockOk =", stock_ok)

cuerpo_fin = {
    "workerId": WORKER_ID,
    "variables": [{"name": "stockOk", "value": stock_ok}]
}

r3 = requests.post(f"{FLOWABLE}/external-job-api/acquire/jobs/{job['id']}/complete",
                   auth=AUTH, json=cuerpo_fin)
r3.raise_for_status()

print(r3.status_code)








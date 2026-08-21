import requests
import time

FLOWABLE = "http://localhost:8080/flowable-rest"
WS_PEDIDOS = "http://localhost:9090"
AUTH = ("rest-admin", "test")
WORKER_ID = "worker-valentin"
ESPERA = 3

def tomar(topic):
    cuerpo = {
        "topic": topic,
        "workerId": WORKER_ID,
        "lockDuration": "PT5M",
        "numberOfTasks": 1
    }
    respuesta = requests.post(f"{FLOWABLE}/external-job-api/acquire/jobs", auth=AUTH, json=cuerpo)
    respuesta.raise_for_status()
    return respuesta.json()

def completar(job_id, variables=None):
    cuerpo = {"workerId": WORKER_ID}
    if variables:
        cuerpo["variables"] = variables
    respuesta = requests.post(f"{FLOWABLE}/external-job-api/acquire/jobs/{job_id}/complete",
                              auth=AUTH, json=cuerpo)
    respuesta.raise_for_status()

def descontar_inventario(job):
    variables = {v["name"]: v["value"] for v in job["variables"]}
    pedido_id = variables["pedidoId"]

    respuesta = requests.post(f"{WS_PEDIDOS}/pedidos/{pedido_id}/descontar-stock")
    respuesta.raise_for_status()
    stock_ok = respuesta.json()["stockOk"]

    print(f"   pedido {pedido_id} -> stockOk = {stock_ok}")
    return [{"name": "stockOk", "value": stock_ok}]

print("Worker arriba.")

while True:
    jobs = tomar("descontarInventario")

    if not jobs:
        time.sleep(ESPERA)
        continue

    job = jobs[0]
    print(f"-> tomé un job de descontarInventario")

    variables = descontar_inventario(job)
    completar(job["id"], variables)

    print("   completado")
    
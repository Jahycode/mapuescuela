import requests

url = "http://localhost:8080/flowable-rest/external-job-api/acquire/jobs"
auth = ("rest-admin", "test")
cuerpo = {
    "topic": "cancelarPedidoVencido",
    "workerId": "worker-valentin",
    "lockDuration": "PT30M",
    "numberOfTasks": 1
}

respuesta = requests.post(url, auth=auth, json=cuerpo)

respuesta.raise_for_status()

jobs = respuesta.json()
print(jobs)
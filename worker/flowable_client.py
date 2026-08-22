import requests
from config import FLOWABLE, AUTH, WORKER_ID, LOCK

def tomar(topic):
    cuerpo = {
        "topic": topic,
        "workerId": WORKER_ID,
        "lockDuration": LOCK,
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

def listar_jobs():
    respuesta = requests.get(f"{FLOWABLE}/external-job-api/jobs",
                             auth=AUTH, params={"size": 100})
    respuesta.raise_for_status()
    return respuesta.json()["data"]
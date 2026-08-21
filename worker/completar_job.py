import requests

url = "http://localhost:8080/flowable-rest/external-job-api/acquire/jobs/88281fc9-9aa8-11f1-9e2d-9ef42df0c7d1/complete"
auth = ("rest-admin", "test")
cuerpo = {"workerId": "worker-valentin"}

respuesta = requests.post(url, auth=auth, json=cuerpo)
respuesta.raise_for_status()

print(respuesta.status_code)

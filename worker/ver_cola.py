import requests

class VerCola:

    url: str = "http://localhost:8080/flowable-rest/external-job-api/jobs"
    auth=("rest-admin", "test")

    def __init__(self, url: str = None):
        self.url = url if url is not None else self.url

    def get_data(self):
        respuesta = requests.get(self.url, auth=self.auth)
        if respuesta.status_code == 200:
            return respuesta.json()
        else:
            respuesta.raise_for_status()

milink = VerCola()

print(milink.get_data())

import os

from dotenv import load_dotenv

load_dotenv()

# El external-job-api cuelga de la raiz, no de /service como el resto de la API.
FLOWABLE = os.environ.get("FLOWABLE_BASE_URL", "http://localhost:8080/flowable-rest")
WS_PEDIDOS = os.environ.get("WS_PEDIDOS", "http://127.0.0.1:9090")

AUTH = (
    os.environ.get("FLOWABLE_USER", "rest-admin"),
    os.environ.get("FLOWABLE_PASS", "test"),
)

WORKER_ID = os.environ.get("WORKER_ID", "worker-mapuescuela")
ESPERA = int(os.environ.get("WORKER_ESPERA", "3"))
LOCK = "PT5M"
REINTENTO = "PT30S"

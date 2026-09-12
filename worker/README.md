# worker/ — El programa que ejecuta las tareas automáticas

El motor de Flowable no ejecuta las tareas automáticas por sí solo: publica un trabajo identificado
con un *topic* y espera. Este worker es el programa que le pregunta al motor si hay algo pendiente,
lo toma, hace la pega llamando a `ws-pedidos`, y le avisa al motor que terminó.

Atiende los cinco topics del modelo, que están descritos en `bpmn/README.md`.

Lo bueno de este modelo es que el worker puedo escribirlo en el lenguaje que quiera aunque el motor
sea Java, y si se cae, el proceso no se rompe: los trabajos quedan esperando hasta que vuelva.

## Qué hay en cada archivo

| Archivo | Qué contiene |
|---|---|
| `worker.py` | El ciclo principal y un handler por topic. Es lo que se ejecuta |
| `config.py` | Las direcciones y credenciales, en un solo lugar |
| `flowable_client.py` | Lo único que sabe de la API de external workers del motor |
| `pedidos_client.py` | Lo único que sabe de las rutas de `ws-pedidos` |
| `ver_cola.py` | Herramienta para mirar qué trabajos hay esperando |

La separación entre los dos clientes es a propósito: son dos integraciones que van a cambiar por
motivos distintos, y así ningún handler tiene una dirección escrita adentro.

## Cómo se ejecuta

Necesita el motor y el web service arriba. Desde esta carpeta, con el entorno virtual activo:

```
python worker.py
```

Se queda corriendo, preguntando cada tres segundos. Se detiene con `Ctrl+C`.

La primera vez hay que crear el entorno y las dependencias:

```
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Lo que ya resuelve

Los cinco handlers llaman a `ws-pedidos` de verdad. Al apagarlo con `Ctrl+C` devuelve a la cola el
trabajo que tuviera reservado, y si uno falla lo reporta al motor —que descuenta un reintento— sin
detener el ciclo de los demás.

La configuración sale de variables de entorno, con valores por defecto que sirven en un computador.

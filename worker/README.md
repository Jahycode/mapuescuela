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

## Lo que falta

Los cuatro handlers que no son el de inventario dejan constancia en pantalla pero todavía no llaman
a nada, porque los endpoints que necesitan no existen aún en `ws-pedidos`. Se reconocen por la marca
`[pendiente]` en el log.

Falta también devolver los trabajos reservados al apagar el worker, capturar los fallos para que uno
no detenga el ciclo completo, y leer la configuración desde el archivo de variables de entorno en vez
de tenerla escrita en `config.py`.

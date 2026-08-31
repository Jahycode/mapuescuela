# Cómo probar el sistema completo

Recorrido de punta a punta, desde que un cliente entra al catálogo hasta que el proceso
descuenta el inventario solo. Toma unos diez minutos y sirve tanto para comprobar que todo
sigue funcionando como para ensayar el video técnico.

---

## 1. Levantar las cuatro piezas, en este orden

El orden importa: cada una depende de la anterior.

**El motor.**

```
docker start flowable
```

Comprobar con el bloque **0** de `docs/flowable-api.http`. Debe responder con la versión del motor.

**El web service.**

```
cd ws-pedidos
.\gradlew.bat run
```

Espera a que diga `Tablas listas.` y después `ws-pedidos escuchando en http://localhost:9090/`.
Si dice que no pudo crear las tablas, no levanta, y ahí hay que mirar el error.

**El worker.**

```
cd worker
.\.venv\Scripts\python.exe worker.py
```

Sin esto las tareas automáticas quedan esperando para siempre. Es el error más fácil de cometer:
todo parece funcionar hasta que el proceso llega a "Descontar inventario" y se queda ahí.

**La web.**

```
cd web
.\.venv\Scripts\python.exe app.py
```

Y abrir <http://localhost:5000>.

## 2. Empezar limpio (antes de grabar)

Con `ws-pedidos` apagado, borrar la carpeta `ws-pedidos/data/`. Al siguiente arranque el catálogo
se recrea con los diez objetos de siembra, todos en stock 1.

Las instancias viejas de Flowable **no** se borran con eso: viven en el contenedor. Se pueden
listar con el bloque **4** de `flowable-api.http` y las que sobren se borran una por una con
`DELETE /runtime/process-instances/{id}`. Conviene hacerlo antes de grabar, porque las tareas de
versiones antiguas del modelo aparecen sin `formKey` y ensucian la vista.

---

## 3. El recorrido

### Paso 1 · El catálogo, en el navegador

<http://localhost:5000>

**Qué mirar:** diez objetos, cada uno con su número, su origen ("La donó una señora de Machalí…")
y sus marcas de uso. Los precios con separador de miles chileno.

**Por qué importa:** nada de eso está escrito en el HTML. Sale de `GET /productos` del web service,
y se puede comprobar abriendo <http://localhost:9090/productos> al lado.

### Paso 2 · Elegir dos objetos

Apretar **Reservar** en dos fichas. La segunda vez el botón de la primera ya dice "Ya está en tu lista".

**Qué mirar en el checkout:** los dos objetos con sus precios, el total sumado, y los tres umbrales
que explican que reservar no es comprar.

### Paso 3 · Reservar

Llenar nombre y correo, y apretar **Reservar y ver los datos para transferir**.

**Qué mirar:** la página del pedido, con el número `MAP-00XX`, el monto exacto y el mensaje que hay
que poner en la transferencia.

**Qué pasó por detrás, en un solo clic:**

1. La web llamó a `POST /pedidos` del web service, que calculó el total y guardó los items.
2. Llamó a Flowable para arrancar una instancia del proceso.
3. Llamó a `PUT /pedidos/{id}/instancia` para dejar amarrado el pedido con su instancia.

### Paso 4 · Comprobar que el proceso arrancó

En `ws-pedidos/api-pedido.http`, ajustar `@pedidoId` al número del pedido y correr el bloque **4**.

**Qué mirar:** el campo `processInstanceId`. Si viene con un identificador, el proceso arrancó.
Si viene vacío, el pedido quedó huérfano y algo falló al llamar a Flowable.

Copiar ese identificador y usarlo en el bloque **5** de `flowable-api.http`.

**Qué mirar:** la tarea activa se llama *Adjuntar comprobante de transferencia* y trae
`"formKey": "adjuntarComprobante"`. Ese `formKey` es lo que le va a decir a la bandeja qué pantalla
mostrar.

Con el bloque **8** se ven las variables de la instancia: `pedidoId` como número,
`modalidadEntrega` en MAYÚSCULAS y `plazoPago` en `PT24H`. Y con el bloque **10**, el timer de las
24 horas esperando.

### Paso 5 · Subir el comprobante

Bloque **7** de `api-pedido.http`. Sube `comprobante-de-prueba.png` como cuerpo crudo.

**Qué mirar:** responde 201 con el nombre que **generó el servidor**, no el del archivo.
Con el bloque **9** se puede ver la imagen de vuelta.

### Paso 6 · Cerrar la tarea del cliente

Bloque **6** de `flowable-api.http`, con el id de la tarea del paso 4.

**Qué mirar:** al volver a correr el bloque **5**, la tarea activa cambió a
*Revisar comprobante de pago*, con `"formKey": "revisionDelPago"`. El token avanzó.

### Paso 7 · La voluntaria revisa y aprueba

Primero se registra la revisión en el web service, con el bloque **10** de `api-pedido.http`.
Después se completa la tarea en el motor con el bloque **7** de `flowable-api.http`, que manda
`esAprobado = true`.

**Qué mirar:** esa variable es la que lee el gateway *¿Pago aprobado?* para decidir el camino.

### Paso 8 · El proceso sigue solo

Acá no hay que hacer nada. En la terminal del worker debería aparecer:

```
-> descontarInventario
   pedido XX -> stockOk = True
```

**Qué pasó:** el gateway mandó el token a "Descontar inventario", que es una tarea de external
worker. El motor la dejó en la cola, el worker la tomó, llamó a `POST /pedidos/{id}/descontar-stock`
y le devolvió `stockOk` al proceso.

### Paso 9 · La comprobación final

Recargar <http://localhost:5000>.

**Los dos objetos ya no están en el catálogo.** Bajaron a la sección de los que encontraron casa,
y nadie los movió a mano: su stock quedó en cero porque el proceso lo decidió.

Ese es el recorrido completo: navegador → web service → motor → worker → web service → navegador.

---

## 4. Cuando algo no funciona

| Síntoma | Causa casi siempre |
|---|---|
| La web muestra "No pude hablar con uno de los servicios" | `ws-pedidos` o Flowable apagados |
| El pedido se crea pero `processInstanceId` viene vacío | Flowable no respondió al arrancar la instancia |
| El proceso se queda en "Descontar inventario" | **El worker no está corriendo** |
| Las tareas salen con `formKey: null` | Son instancias viejas, de una versión del modelo anterior a los formKey |
| El stock no baja al aprobar | Revisar que `esAprobado` haya viajado como booleano, no como texto |
| Tildes rotas en el catálogo | Falta `options.encoding = "UTF-8"` en `build.gradle.kts` |

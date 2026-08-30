# Acta 13 — El cliente ya puede reservar, y el web service cubre el pago

- **Fecha:** domingo 30 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Durante esta sesión cerré el flujo del cliente en la web —elegir objetos, reservar y ver el pedido— y
agregué al web service los endpoints del pago, que era la parte del proceso que ningún servicio cubría.

## Lo que hice

### El checkout y la página del pedido

La selección de objetos vive en la sesión de Flask entre el catálogo y el checkout. `POST /reservar`
crea el pedido llamando a `POST /pedidos` del web service, limpia la selección y redirige a
`/pedido/{id}`.

Probé el recorrido completo con una sesión real: elegí el velador y el lote de novelas, el checkout
sumó $54.500, el pedido quedó creado y la página del pedido mostró los datos para transferir con el
monto exacto y el mensaje **MAP-0001**.

Dos detalles del orden que importan. La selección se limpia **después** de confirmar que el pedido se
creó: si se limpiara antes y la creación fallara, el cliente volvería con la lista vacía y sin entender
por qué. Y cuando la creación falla, devuelvo la misma página con el error en vez de redirigir, porque
un redirect provoca un `GET` nuevo y limpio que borraría el nombre y el correo que acababa de escribir.

### Los endpoints del comprobante

Evalué tres formas de que el archivo llegue al web service y elegí la que menos código pide: **el
cuerpo crudo**, con `Content-Type: image/png` y los bytes tal cual, en vez de `multipart/form-data`.

Descarté multipart con argumento. Lo que aporta de más es poder mandar campos junto al archivo y
conservar el nombre original, y acá no sirve ninguna de las dos cosas: el cliente sube solo la foto —el
monto y la decisión los manda la voluntaria después, en otra llamada— y **el nombre original hay que
descartarlo igual**. Si alguien sube algo llamado `../../config/algo` y lo guardo con ese nombre, escribo
fuera de mi carpeta. El servidor genera el nombre siempre.

Quedaron tres endpoints: `POST /pedidos/{id}/comprobante` que valida tipo, tamaño máximo de 5 MB y que
el pedido exista; `GET /pedidos/{id}/comprobantes` con el historial en JSON; y
`GET /pedidos/{id}/comprobante` que devuelve los bytes del más reciente con su `Content-Type`.

Verifiqué la vuelta completa: subí un PNG, lo bajé y `cmp` confirmó que era byte por byte el mismo.

### El registro de la revisión

Tabla `revision` con quién revisó, qué decidió, qué monto leyó del comprobante y el mensaje para el
cliente. La decisión es un vocabulario cerrado —`APROBADO`, `OTRA_FOTO`, `CANCELADO`— validado en Java
con un `Set`, no con un `CHECK` en la tabla, porque ese `CHECK` sobre texto ya me reventó en H2 cuando
lo intenté con `desenlace`.

El endpoint exige mensaje cuando la decisión no es aprobar. Esa regla estaba en el diseño de la
pantalla, pero puesta en el servicio se cumple aunque alguien llame a la API con `curl` saltándose la
interfaz.

## Cierre

La sesión dejó al cliente reservando de verdad y al web service cubriendo los cuatro puntos que la
rúbrica nombra: registro, pedido, pago y estado. Pero lo que más me sirvió fue releer la pauta real:
llevaba dos días priorizando la web sobre la base de una lista de criterios que yo mismo había
idealizado, y resultó que valía la quinta parte de lo que suponía.

## Estado de la Entrega 2

| Criterio | Estado |
|---|---|
| Modelo BPMN ejecutable (20) | ✅ |
| Uso de tareas BPMN y External Workers (15) | ✅ |
| Proceso ejecutándose en Flowable (15) | ✅ las seis salidas recorridas |
| Web Services que cubren el proceso (15) | ✅ registro, pedido, pago y estado |
| Funcionamiento y prueba de Web Services (10) | ✅ |
| Interfaces de usuario (5) | ◐ el cliente reserva; falta la bandeja |
| Repositorio GitHub (5) | ✅ |
| Trabajo en equipo y gestión (5) | ✅ actas al día |
| Video para emprendedora (5) | ☐ |
| Video para profesor (5) | ☐ |

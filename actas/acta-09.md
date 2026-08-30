# Acta 09 — Los tres endpoints que faltaban para poder empezar la web

- **Fecha:** lunes 24 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Durante esta sesión implementé los tres endpoints que faltaban para comenzar el desarrollo de la web:

- `GET /productos`
- `GET /pedidos/{id}`
- `PUT /pedidos/{id}/instancia`

Con estos endpoints, el web service queda con ocho endpoints disponibles, por lo que ya es posible
comenzar con las pantallas.

## Lo que hice

### `GET /productos`

Implementé el catálogo de productos, que será la información inicial que mostrará la web.

Fue el único endpoint de los tres que requirió una estructura nueva. Creé `Producto.java` y
`ProductoResource.java`, utilizando un `@Path("/productos")` independiente, ya que los productos no
dependen de los pedidos.

Un detalle importante fue comprobar nuevamente el funcionamiento del escaneo de Jersey: no fue
necesario registrar manualmente la nueva clase, porque `App.java` ya configura el escaneo del paquete
`cl.mapuescuela.pedidos` y Jersey encuentra el recurso automáticamente.

### `GET /pedidos/{id}`

Este endpoint devuelve la información completa de un pedido. Será utilizado por la pantalla de
seguimiento, que necesita datos como el nombre del cliente, el monto y el desenlace del pedido.

### `PUT /pedidos/{id}/instancia`

Este endpoint permite guardar en `process_instance_id` el identificador de la instancia de Flowable
asociada al pedido.

La necesidad aparece porque la relación inicialmente queda establecida en una sola dirección: al iniciar
Flowable se envía el ID del pedido como variable, por lo que la instancia sabe a qué pedido corresponde,
pero el pedido todavía no conoce el ID de su instancia. Este endpoint permite completar esa relación
para que la web pueda consultar posteriormente el estado del proceso.

Elegí PUT en lugar de POST porque no se está creando un nuevo recurso. La instancia ya existe y el
endpoint únicamente actualiza una columna del pedido. Además, la operación es idempotente: enviar
nuevamente el mismo identificador produce el mismo estado final. Lo comprobé ejecutando la operación
dos veces.

## Error encontrado

El principal aprendizaje de la sesión apareció al implementar el `PUT`.

Inicialmente lo había construido al revés: recibía el ID de la instancia y realizaba un `SELECT` para
comprobar si existía un pedido asociado. El método compilaba y respondía `200`, pero no modificaba
absolutamente nada en la base de datos.

El error quedó en evidencia al hacer una pregunta sencilla:

> Después de que el endpoint responde correctamente, ¿qué cambió en la base de datos?

La respuesta era: nada.

El problema no estaba en una línea de código incorrecta, sino en que la implementación no cumplía el
propósito del endpoint. En vez de consultar desde la instancia hacia el pedido, debía actualizar el
pedido con el identificador de la instancia mediante un `UPDATE`.

Este caso me sirvió para entender que probar que un endpoint responde `200` no es suficiente. También
hay que verificar que el efecto producido sea exactamente el esperado.

## Pendientes y decisiones

- `listarProductos()` quedó temporalmente dentro de `PedidoDAO`, ya que este DAO ya contenía otros
  métodos relacionados con productos. Lo correcto sería crear un `ProductoDAO` independiente si esta
  parte continúa creciendo.
- `POST /pedidos/{id}/desenlace`, implementado anteriormente, tiene una lógica similar a la
  actualización de la instancia: modifica información de un recurso existente y puede repetirse sin
  generar uno nuevo. Por consistencia, debería ser `PUT`. No lo modificaré por ahora porque ya está
  implementado y probado.
- Con los ocho endpoints disponibles, el siguiente paso es comenzar el desarrollo de la web.
- Los endpoints adicionales se implementarán a medida que aparezcan necesidades concretas de las
  pantallas, evitando desarrollar funcionalidades antes de que exista un consumidor que las requiera.

## Cierre

La sesión permitió completar la capa necesaria para comenzar la web y, más importante, dejar clara una
idea para las siguientes etapas: un endpoint no se valida solamente porque compile y responda
correctamente; debe comprobarse que produzca el efecto que su contrato promete.

## Estado de la Entrega 2

| Criterio | Estado |
|---|---|
| Modelo BPMN ejecutable | ✅ |
| Uso de tareas BPMN y external workers | ✅ |
| Proceso ejecutándose en Flowable | ✅ las seis salidas recorridas |
| Funcionamiento y prueba de web services | ✅ |
| Repositorio GitHub | ✅ |
| Gestión y planificación | ✅ |
| Web services que cubren el proceso | ✅ ocho endpoints |
| Interfaces de usuario | ☐ **lo siguiente** |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |

# Acta 16 — Una venta cerrada por fin deja rastro en mi base

- **Fecha:** jueves 10 de septiembre de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Leí la rúbrica del examen final y recorrí el sistema con ojo de usuario, anotando todo lo que se sentía
incompleto. Salieron once correcciones. La que más pesa no es visual: hasta hoy mi base de datos solo
guardaba los pedidos que se caían, nunca los que se vendían.

## Lo que hice

### El desenlace de las ventas buenas

Mi tabla `pedido` tiene una columna `desenlace` y hasta hoy solo se llenaba con `RECHAZADO`,
`CANCELADO_VENCIMIENTO` y `SIN_STOCK`. Un pedido entregado quedaba en `NULL`, igual que uno a medio
camino.

Agregué `fin_del_proceso()` en `web/flowable_client.py`, que consulta
`GET /history/historic-process-instances/{id}` y devuelve dos cosas: si la instancia terminó y en qué
evento de fin. Con eso, `cerrar_pedido()` traduce el `endActivityId` a un valor de negocio —
`EndNoneEvent_31` es `RETIRADO`, `_37` es `DESPACHADO_VOLUNTARIO`, `_41` es `DESPACHADO_COURIER`— y lo
manda a `POST /pedidos/{id}/desenlace`.

La alternativa era agregar tres *service task* al BPMN, una por cada final bueno, y que las tomara el
worker como ya hace con los malos. La descarté porque obliga a redesplegar el modelo y a rehacer las
pruebas de los seis caminos, y porque el motor ya sabe la respuesta sin que yo agregue nada. Es
coherente con el ADR-006: la fuente de la verdad es el motor.

La lista blanca `DESENLACES` de `PedidoResource.java` tenía los seis valores desde el acta 13,
esperando a que alguien los usara.

### La tabla `envio`

*Registrar datos de envío* era un botón que decía «Listo» y no registraba nada. Creé la tabla `envio`
(`transportista`, `numero_seguimiento`, `direccion`), con su `POST /pedidos/{id}/envio` y su `GET`, y la
pantalla que los llena en la bandeja.

Acá apareció un hueco del diseño: **el cliente nunca da una dirección**. Mi checkout pide nombre, correo
y modalidad, así que en un pedido con despacho nadie sabe dónde mandarlo. Por ahora la escribe la
voluntaria en este formulario, que es como coordinan hoy por WhatsApp. Pedirla en el checkout sería lo
correcto, pero implica un campo condicional que solo aparece con despacho.

### El histórico

Pantalla nueva en `/bandeja/historico`: los pedidos cerrados, con cuántas ventas se concretaron y cuánto
se recaudó. Los lee de `GET /pedidos` filtrando por `desenlace`.

Podría haberlos leído del historial de Flowable. Elegí mi propia base porque el historial del motor es
un registro de ejecución, no del negocio: se purga y no tiene ni el monto ni el cliente.

### Las pantallas que avisan

Cerrar una tarea no decía nada. Agregué mensajes con `flash()` que nombran lo que viene: «Tarea cerrada.
Sigue: *Marcar listo para retiro*». Cuando el paso siguiente es automático el mensaje lo dice y la página
se recarga sola a los cuatro segundos, más de lo que tarda el worker en su ciclo de tres.

También puse una barra de tres fases y moví el monto y el mensaje de la revisión a un `<dialog>` que se
abre solo al cancelar. Ese modal lleva su propio formulario, separado del de aprobar, para que el campo
obligatorio no quede nunca escondido: es el problema del acta 14, cuando un `required` dentro de un
elemento invisible bloqueaba el envío sin mostrar nada.

## Error encontrado

Construí el histórico, lo abrí, y mostraba siete pedidos: tres rechazados, tres vencidos y uno sin
stock. Cero ventas. Me quedé mirándolo:

> ¿El histórico solo refleja tareas que fallaron?

No era la pantalla. Era que **todo lo que escribe el desenlace vive en el worker**, y el worker solo
corre en los caminos que terminan mal. Los tres finales buenos de mi modelo desembocan en tareas
humanas —*Registrar retiro*, *Registrar despacho por voluntario*, *Registrar datos de envío*— que se
cierran desde la bandeja y no publican ningún trabajo automático. El modelo estaba bien, el worker
estaba bien, y aun así mi base no podía responder cuánto habíamos vendido.

Lo incómodo es que nada lo señalaba: los seis caminos del acta 15 se recorrieron completos y todos
llegaron a su evento de fin correcto. La prueba miraba el motor, y en el motor estaba todo.

Lo que queda: **quien escribe un dato decide qué casos quedan registrados.** Concentré la persistencia
de los desenlaces en el worker sin notar que el worker atiende solo la mitad del diagrama. Un registro
incompleto no se ve incompleto hasta que alguien lo lee para otra cosa.

## Pendientes y decisiones

- **La publicación no se modela en BPMN.** Mi AS-IS separa publicar de vender, así que era tentador
  hacer un segundo proceso. No lo haré: publicar es una persona llenando un formulario, sin espera de
  terceros, sin plazos y sin decisiones que se puedan perder. Modelarlo sería usar el motor porque lo
  tengo, no porque haga falta.
- El monto leído queda **opcional** al cancelar un pago. Si el motivo es que la foto está borrosa no hay
  monto que escribir, y exigirlo bloquearía la cancelación.
- Lo que sigue son tres pantallas de administración: cargar un objeto, editarlo o retirarlo, y los datos
  de la agrupación. Hoy el catálogo son diez objetos escritos en `PedidoDAO`, y el RUT y la cuenta
  bancaria están dentro de tres plantillas HTML aunque `.env.example` tiene esas variables hace meses.
- El README raíz dice que la base es SQL Server, habla de un carrito que descarté y da por pendiente la
  migración a open source, que ya está hecha. Y no hay guía de instalación: el comando con que creé el
  contenedor de Flowable no está escrito en ninguna parte.

## Cierre

El sistema dejó de tener una memoria sesgada hacia lo que sale mal. Antes de hoy podía decir con detalle
por qué se perdió una venta y no podía decir cuántas se cerraron, que es justamente el dato por el que
la agrupación llevaría un sistema en vez de un cuaderno. Lo que viene ya no es el proceso: es que ellas
puedan cargar sus propias cosas sin que yo recompile nada.

## Estado del Examen

| Criterio | Estado |
|---|---|
| MVP y valor de negocio (25) | ◐ funciona completo, pero el catálogo y los datos de la agrupación no se pueden editar |
| Ejecución integral del proceso en Flowable (15) | ✅ tareas humanas, external workers, cuatro compuertas y el temporizador |
| Integración de web services y base de datos (15) | ✅ seis tablas y quince endpoints; las seis salidas del proceso quedan persistidas |
| Interfaces de usuario y experiencia (15) | ◐ catálogo, checkout, seguimiento, bandeja e histórico; faltan las de administración |
| Uso de IA y tecnologías complementarias (5) | ◐ está el ADR-010, pero no aparece en el README ni en los videos |
| Documentación, repositorio y entregables (10) | ◐ repositorio ordenado y actas al día; falta el manual de instalación |
| Video demo para la emprendedora (8) | ☐ |
| Sustentación técnica para el profesor (7) | ☐ |

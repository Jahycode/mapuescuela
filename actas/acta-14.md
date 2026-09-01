# Acta 14 — Las voluntarias ya resuelven tareas desde una pantalla

- **Fecha:** lunes 31 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Cerré la Entrega 2 grabando los dos videos, leí la rúbrica de la Entrega 3 y empecé la pieza que esa
rúbrica premia: la bandeja de las voluntarias. Hasta hoy el proceso solo avanzaba porque yo le mandaba
peticiones al motor desde un archivo `.http`; ahora hay una pantalla que lista las tareas pendientes y
las completa.

## Lo que hice

### Los dos videos y el cierre de la Entrega 2

Grabé el video técnico y el de la emprendedora, y con eso quedaron cubiertos los diez puntos que
faltaban. Antes de grabar limpié las instancias vivas del motor: las que venían de despliegues anteriores
devuelven `formKey: null` para siempre, porque el `formKey` se resuelve contra la versión con la que
arrancó la instancia.

### La rúbrica de la Entrega 3

Cambió el foco. La Entrega 2 premiaba tener las piezas; la 3 premia que el proceso completo se pueda
usar. Tres criterios que suman 40 puntos —cobertura del proceso, ejecución de extremo a extremo e
interfaces— dependen de lo mismo: que las ocho tareas humanas se puedan completar desde una pantalla.
El criterio de ejecución pide explícitamente «incluyendo formularios», y mis ocho `formKey` estaban
declarados en el BPMN pero nadie los leía.

### La bandeja: el cruce entre el motor y el web service

La bandeja necesita dos cosas que viven separadas. El motor sabe **cuáles** tareas hay pendientes; el
web service sabe **de qué se tratan**. Lo único que las une es la variable `pedidoId`.

Resolví el cruce con dos llamadas y una unión en memoria:
`GET /runtime/tasks?processDefinitionKey=ventaMapuescuela&includeProcessVariables=true` trae las tareas
con sus variables adentro, y `GET /pedidos` trae todos los pedidos, que indexo por `id`. La alternativa
era pedirle al web service cada pedido dentro del bucle, y la descarté porque con veinte tareas serían
veintiuna llamadas en vez de dos: el problema N+1, que no se nota probando con dos registros.

Filtro por `processDefinitionKey` y no por `assignee` porque el modelo asigna las tareas con
`${initiator}`, y como todas las instancias las arranca la web contra el motor, el responsable de
absolutamente todas es `rest-admin`. Filtrar por responsable no separaría nada.

El prototipo hacía todo esto en el navegador con las tareas escritas a mano. La pasé a renderizado en
el servidor, porque mantener sincronizado en el cliente un estado que viene de dos servicios es más
trabajo que volver a pintar la página. Elegir una tarea es un enlace a `?tarea=<id>`, así que cada una
tiene su propia URL.

### Las acciones

Las ocho tareas humanas no necesitan ocho formularios, sino tres. Seis no deciden nada y se cierran con
`{"action": "complete"}`. «Revisar comprobante» manda `esAprobado`. «Gestionar despacho» manda
`tipoDespacho`.

Aprobar un pago son **dos escrituras en sistemas distintos** sin transacción que las cubra: registrar la
revisión en el web service y completar la tarea en el motor. Elegí registrar primero y completar
después. Al revés, si falla el registro, el proceso avanza y descuenta inventario sin que quede escrito
quién aprobó. En el orden que elegí, lo peor que pasa es que quede una revisión duplicada si la
voluntaria reintenta, y una fila de auditoría de más se detecta mirando la tabla; una que falta, no. De
yapa da un seguro: si el web service está caído, el `raise_for_status()` corta la función antes de tocar
el motor.

## Error encontrado

Puse los dos botones de la revisión dentro del mismo formulario, compartiendo `name="decision"` con
valores distintos —`APROBADO` y `CANCELADO`—, que es la forma de tener dos acciones sin anidar
formularios. Funcionaba: probé aprobar y probé cancelar, y las dos hicieron lo suyo.

El problema salió al explicar por qué funcionaba:

> ¿Cómo sabe el servidor cuál de los dos botones apretó la voluntaria?

La respuesta es que el navegador manda solo el botón pulsado. Pero al buscar el caso límite en la
especificación de HTML apareció el otro camino: cuando el formulario se envía con **Enter** desde un
campo de texto, el navegador usa el *primer* botón de submit. O sea que apretar Enter en el campo del
monto aprobaba la transferencia. Ninguna prueba lo habría mostrado, porque yo siempre apretaba el botón.

La causa de fondo no era el Enter sino la guarda: tenía
`aprobado = request.form.get("decision") == "APROBADO"`, que colapsa tres situaciones en dos —aprobar,
cancelar y *no haber decidido nada* caían todas en «no aprobado»—. Lo corregí comparando contra un
conjunto cerrado, y agregué un botón de submit oculto adelante que se lleva el Enter sin mandar valor.
Comprobé los dos casos: el formulario sin decisión, y el peor, con el mensaje ya escrito. Los dos
rebotan sin registrar nada.

Lo que queda: un formulario con dos botones tiene una tercera entrada que no diseñé, y es una tecla.

## Pendientes y decisiones

- Falta la pantalla del cliente para subir su comprobante. El endpoint existe desde el acta 13, pero
  hoy solo se puede usar desde un archivo `.http`.
- **El modelo no tiene «pedirle otra foto».** El gateway del pago tiene dos salidas: `esAprobado == true`
  y el rechazo por defecto. Mi prototipo ofrecía tres opciones, y la bandeja hoy ofrece las dos que el
  proceso sabe ejecutar. Agregar el bucle de vuelta a «Adjuntar comprobante» sumaría en el criterio de
  gateways, pero implica redesplegar el modelo y decidí no tocarlo con la bandeja recién terminada.
- Las pruebas cubren el camino feliz. Faltan los alternativos —pago rechazado, plazo vencido, sin
  stock, retiro contra despacho—, que es documentar más que programar.

## Cierre

Con la bandeja el sistema dejó de necesitarme para avanzar: antes de hoy cada paso posterior a la
reserva lo empujaba yo a mano, y ahora una persona sin acceso al motor puede mirar qué hay pendiente y
resolverlo. Esa es la diferencia entre un proceso que ejecuta y uno que se usa, que es justo lo que la
rúbrica de la Entrega 3 está midiendo.

## Estado de la Entrega 3

| Criterio | Estado |
|---|---|
| Cobertura del proceso de negocio (20) | ◐ el cliente reserva y la voluntaria resuelve; falta subir el comprobante |
| Uso de BPMN, Flowable y automatización (15) | ✅ |
| Proceso ejecutándose en Flowable (15) | ✅ la bandeja lee el `formKey` y decide la pantalla |
| Integración de Web Services con el proceso (15) | ✅ |
| Funcionamiento integral y pruebas (10) | ◐ el camino feliz probado; faltan los alternativos |
| Interfaces de usuario (5) | ◐ catálogo, checkout, seguimiento y bandeja |
| Repositorio GitHub (5) | ✅ |
| Trabajo en equipo y gestión (5) | ✅ actas al día |
| Video para emprendedora (5) | ☐ hay que rehacerlo; el de la Entrega 2 quedó grabado |
| Video para profesor (5) | ☐ hay que rehacerlo |

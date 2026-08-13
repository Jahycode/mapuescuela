# Acta 03 — Los tres escenarios corriendo y arranque del web service

- **Fecha:** miércoles 12 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## Haciendo de worker a mano

Ayer el proceso quedó detenido en una tarea automática, esperando un worker que todavía no existe.
En vez de dejarlo ahí, busqué si el motor permitía atender esos trabajos manualmente, y encontré que
Flowable expone una API para eso. La descubrí en el Swagger que el propio contenedor publica en
`/flowable-rest/docs/`, que documenta exactamente la versión que tengo instalada.

El mecanismo tiene dos pasos: uno pide trabajo de un topic y el motor se lo reserva por un tiempo, y
el otro avisa que terminó y le devuelve variables al proceso. La reserva existe para que, si mañana
tengo varios workers corriendo, dos no procesen el mismo pedido; y si uno se cae, la reserva vence
sola y otro lo puede tomar.

Agregué esos dos pasos al archivo de peticiones. Son literalmente lo que va a hacer el worker cuando
lo programe, así que me sirvió para entender el mecanismo antes de escribir una línea de código.

Con eso cerré el pedido que había quedado colgado y **quedó demostrado el escenario del vencimiento
completo**, desde el checkout hasta el final de cancelación.

## El rechazo, que apareció sin buscarlo

Al iniciar otro pedido me equivoqué: completé la tarea de revisión del pago sin mandar la variable de
la decisión. El resultado fue que el gateway no encontró esa variable y se fue por el **flujo
default**, que en mi modelo apunta al rechazo.

No lo tomé como error, porque es justamente para lo que dejé los default apuntando al camino seguro.
Si hubiera puesto la aprobación como default, ese pedido se habría aprobado **sin que nadie revisara
el pago**. Y si no hubiera marcado ningún default, el motor habría fallado y la instancia quedaba
rota.

Aproveché el desvío y lo llevé hasta el final: **escenario de rechazo demostrado**, incluyendo que la
rama encadena dos tareas automáticas seguidas y el token pasa por las dos sin problema.

## El camino feliz

Después recorrí el proceso completo hasta el final de retiro: adjuntar el comprobante, revisar y
aprobar el pago, descontar el inventario haciendo de worker, preparar el pedido, marcarlo listo y
registrar el retiro. **Los cuatro gateways evaluaron con la variable correcta y ninguno cayó al
default.**

Me quedó clara una distinción que antes mezclaba: hay tareas humanas que solo se cierran, tareas
humanas que además comunican una decisión, y tareas automáticas que ejecuta un programa por topic.
Solo mandan variables las que **producen información nueva** — si el dato ya venía del checkout, no
hay que repetirlo.

## Arranque del web service en Java

Revisé el `ws-socios` del ejemplo del profesor para copiar el patrón: Jersey con JAX-RS sobre un
servidor embebido, y las anotaciones que definen la ruta y el verbo de cada operación. Es lo mismo
que llevo dos días consumiendo en Flowable, pero ahora escribiendo el lado que recibe.

Armé la estructura del proyecto y los archivos de configuración. Tomé tres decisiones distintas a las
del ejemplo, a propósito:

- **Java 24** en vez de 21, que es la versión que tengo instalada.
- **Las librerías disponibles también al compilar**, no solo al ejecutar. El ejemplo del profesor las
  declara solo para ejecución y por eso tiene que cargar Jersey por reflexión; declarándolas completas
  puedo usar imports normales y el código queda más corto y más fácil de explicar.
- **Las versiones directas** en el archivo de configuración en vez de un catálogo aparte, para no
  saltar entre dos archivos.

No instalé Gradle: copié el *wrapper* del repositorio del profesor, que es un conjunto de archivos
estándar que descarga la versión correcta por sí solo. Así cualquiera que clone mi repo compila con
exactamente la misma versión sin instalar nada.

## Documentación

Dejé un solo `README.md` por carpeta explicando en general qué hay en cada una, en vez de varios
archivos hablando de lo mismo. La explicación detallada la voy a dar en los videos. De paso corregí
el README del worker, que listaba un topic que ya no existe y le faltaban dos.

## Estado de la entrega

| Criterio | Estado |
|---|---|
| Modelo AS-IS | ✅ |
| Modelo TO-BE | ✅ |
| Repositorio GitHub | ✅ |
| Actas | ✅ |
| Proceso ejecutable en Flowable | ✅ (los tres escenarios) |
| Coherencia BPMN ↔ Flowable | ✅ |
| Formularios en Flowable | ☐ |
| Avance en web services | 🔨 en construcción |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |
| Tag `entrega-1` | ☐ |

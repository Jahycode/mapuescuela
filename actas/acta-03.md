# Acta 03 — Los tres escenarios corriendo y arranque del web service

- **Fecha:** miércoles 12 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## Cómo atendí manualmente las tareas automáticas

La sesión anterior terminó con el proceso detenido en una tarea automática, esperando un programa
externo que todavía no existe. En lugar de dejarlo así, busqué si el motor permitía atender esos
trabajos de forma manual, y encontré que Flowable expone una interfaz para eso. La descubrí revisando
la documentación que el propio contenedor publica, que tiene la ventaja de corresponder exactamente a
la versión que tengo instalada y no a otra.

El mecanismo funciona en dos pasos. Primero se solicita trabajo de un topic determinado y el motor lo
reserva por un tiempo definido; después se informa que el trabajo terminó y se devuelven las
variables que correspondan. Esa reserva existe para que, si en el futuro hay varios programas
trabajando en paralelo, dos no procesen el mismo pedido, y para que si uno falla la reserva expire
sola y otro pueda retomarlo.

Agregué esos dos pasos al archivo de peticiones que uso para probar. Corresponden literalmente a lo
que hará el programa cuando lo desarrolle, así que me sirvieron para entender el mecanismo antes de
escribir una sola línea de código. Con eso completé el pedido que había quedado pendiente y quedó
demostrado el escenario del vencimiento de principio a fin.

## El escenario de rechazo, que apareció sin buscarlo

Al iniciar otro pedido cometí un error: completé la tarea de revisión del pago sin enviar la variable
que contiene la decisión. Como consecuencia, el gateway no encontró esa variable y tomó el flujo por
defecto, que en mi modelo corresponde al rechazo.

No lo tomé como una falla, porque es precisamente para lo que dejé los flujos por defecto apuntando
al camino más conservador. Si hubiera configurado la aprobación como valor por defecto, ese pedido se
habría aprobado sin que nadie revisara el pago. Y si no hubiera marcado ningún flujo por defecto, el
motor habría fallado y la instancia habría quedado en un estado inconsistente.

Aproveché el desvío y lo llevé hasta el final, con lo que quedó demostrado también el escenario de
rechazo. De paso comprobé que esa rama encadena dos tareas automáticas seguidas y que el token pasa
por ambas sin inconvenientes.

## El camino principal

Después recorrí el proceso completo hasta el final de retiro: adjuntar el comprobante, revisar y
aprobar el pago, descontar el inventario atendiendo manualmente la tarea automática, preparar el
pedido, marcarlo como listo y registrar el retiro. Los cuatro gateways evaluaron correctamente con su
variable y ninguno tuvo que recurrir al flujo por defecto.

En el camino me quedó clara una distinción que antes mezclaba. Existen tareas humanas que solamente
se cierran, tareas humanas que además comunican una decisión al proceso, y tareas automáticas que
ejecuta un programa identificado por su topic. Solo envían variables aquellas que producen
información nueva; si el dato ya venía desde el checkout, no hay necesidad de repetirlo.

## Arranque del web service en Java

Revisé el ejemplo de web service del profesor para adoptar el mismo patrón: la especificación de
Jakarta para servicios REST, una implementación compatible y un servidor embebido dentro de la propia
aplicación. Las anotaciones definen la ruta y el verbo de cada operación, que es exactamente lo mismo
que llevo días consumiendo en Flowable, pero ahora escribiendo el lado que recibe las peticiones.

Armé la estructura del proyecto y los archivos de configuración. Tomé tres decisiones distintas a las
del ejemplo, de forma deliberada:

- Utilicé la versión de Java que tengo instalada en lugar de la del ejemplo, para no depender de una
  instalación adicional.
- Declaré las librerías de manera que estén disponibles también al compilar y no solo al ejecutar. El
  ejemplo del profesor las declara solo para ejecución, y por eso debe cargarlas de forma indirecta;
  declarándolas completas puedo utilizar importaciones normales y el código queda más corto y más
  fácil de explicar.
- Puse las versiones directamente en el archivo de configuración en lugar de mantenerlas en un
  catálogo aparte, para no tener que revisar dos archivos.

No instalé la herramienta de construcción en el equipo. En su lugar copié el conjunto de archivos
estándar que la descarga automáticamente, con lo que cualquier persona que clone el repositorio puede
compilar con exactamente la misma versión sin instalar nada.

## Documentación

Dejé un solo archivo de documentación por carpeta, explicando de forma general qué contiene cada una,
en lugar de mantener varios archivos hablando del mismo tema. La explicación detallada la daré en los
videos. Además corregí la documentación del componente que consumirá las tareas automáticas, que
mencionaba un topic que ya no existe y omitía otros dos.

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

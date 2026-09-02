# Acta 15 — El cliente cierra su parte y los seis caminos quedan probados

- **Fecha:** martes 1 de septiembre de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Cerré dos criterios de la Entrega 3 en la misma sesión. El cliente ya puede subir su comprobante desde
la web, con lo que ninguna tarea humana necesita un archivo `.http` para avanzar; y los seis finales
del proceso quedaron recorridos y documentados con evidencia comprobable.

## Lo que hice

### La pantalla del comprobante

El endpoint `POST /pedidos/{id}/comprobante` existe desde el acta 13, pero recibe el archivo como
**cuerpo crudo** y un formulario HTML manda `multipart/form-data`. Los dos formatos no se parecen, así
que había que decidir dónde traducir.

Elegí hacerlo en la web y no tocar el endpoint. Flask recibe el multipart —que es lo natural para un
formulario—, saca los bytes con `archivo.read()` y los reenvía con el `Content-Type` que declaró el
navegador. La alternativa era cambiar el web service para que aceptara multipart, y la descarté porque ese
endpoint ya está probado y porque el argumento del acta 13 sigue valiendo: de multipart no necesito
nada de lo que aporta.

Subir el comprobante son otra vez **dos escrituras en sistemas distintos**, así que apliqué el mismo
orden que la revisión: primero guardar el archivo, y solo si eso resultó, completar la tarea en el
motor. El `raise_for_status()` es la línea que lo hace cumplir.

### El estado real en la página de seguimiento

La página tenía la insignia «Esperando el pago» escrita a mano. Le habría dicho «te quedan 24 horas
para transferir» a alguien que ya había pagado.

Agregué `tarea_activa()` al cliente de Flowable y ahora la página muestra cuatro estados según el
`formKey`: el formulario de subida, el «estamos revisando», el «pago aprobado» y un mensaje neutro
cuando no hay tarea humana.

En la ruta que recibe el archivo le pregunto la tarea al motor en vez de mandarla en un campo oculto:
un identificador guardado en el HTML se vence si el cliente deja la página abierta. Esa consulta
habilitó además una guarda que resultó clave: solo completo la tarea si sigue siendo la de adjuntar. Sin ella, un doble clic completaría «Revisar comprobante» sin mandar
`esAprobado`, el gateway caería a su flujo por defecto y **el cliente rechazaría su propio pago**.

### Los seis escenarios

Recorrí los seis finales desde la web y la bandeja, sin un solo comando al motor, y los dejé en
`docs/pruebas-de-escenarios.md`. La evidencia no son capturas: es una consulta al historial que
devuelve seis instancias terminadas con seis `endActivityId` distintos.

El escenario de falta de stock lo monté como la carrera real en vez de fabricar un pedido con un
objeto agotado: dos sesiones distintas reservando el mismo estante. Las dos reservas se crearon, el
stock siguió en 1 —porque reservar no descuenta— y al aprobar la primera bajó a 0 y la segunda terminó
con `stockOk = false`. Así queda probado en un solo escenario que la reserva no toca el inventario y
que el descuento es atómico.

Para el vencimiento arranqué la web con `PLAZO_PAGO=PT2M`: ese valor sale de una variable de entorno
justamente para poder probar el temporizador sin tocar el BPMN.

## Error encontrado

Al preparar el documento de pruebas me di cuenta de que no sabía cómo llegar a dos de los seis
finales:

> ¿Cómo llego a «Despachado por courier» desde la web?

La respuesta era que no se podía. En `app.py` la modalidad de entrega estaba escrita fija como
`"retiro"`, así que toda la rama de despacho del modelo —el gateway de modalidad, «Gestionar
despacho», la elección entre courier y voluntario, «Registrar datos de envío» y dos finales
distintos— era **inalcanzable desde la interfaz**. Solo se llegaba arrancando la instancia a mano.

Lo que hace incómodo este error es que nada lo señalaba. El modelo estaba bien, la bandeja resolvía
esas tareas sin problema y las pruebas contra el motor pasaban, porque desde un archivo `.http` sí se
alcanzan.

Lo corregí habilitando la segunda opción en el checkout y leyendo `request.form` con una lista blanca,
en vez de la constante. El cambio fue chico porque la rama ya estaba completa: no hubo que construir nada, solo dejar de
bloquear la entrada. También cambié la frase de la pantalla que decía «por ahora solo hacemos retiro».

Lo que queda: **un modelo puede tener ramas correctas, ejecutables y probadas que ningún usuario puede
alcanzar**, y eso no aparece en ninguna prueba hecha contra el motor. La única forma de detectarlo es
preguntarse, por cada final, cómo llega ahí una persona usando el sistema.

## Pendientes y decisiones

- Cuando la modalidad que llega no está en la lista blanca, **caigo a retiro** en vez de devolver un
  400. Es el camino que no compromete nada: no pide dirección ni genera costo de envío, y la voluntaria
  lo ve en la bandeja. Si algún día el despacho tuviera precio, la decisión correcta sería la contraria.
- **`ws-pedidos` no valida la modalidad de entrega.** La columna es un `VARCHAR(20)` y acepta cualquier
  texto, así que la lista blanca vive solo en la web. Por el criterio de que cada sistema valida lo
  suyo, debería estar también en el servicio; lo dejé fuera porque implica recompilar y la prioridad
  es la entrega.
- Cuando no hay tarea humana activa, la página no distingue entre «el proceso terminó» y «hay una
  automática corriendo». Separarlas requiere consultar el historial y mirar si tiene `endTime`.
- Las credenciales siguen escritas en `worker/config.py` y ese archivo está en el repositorio.

## Cierre

Con estas dos piezas el sistema dejó de tener partes que solo yo puedo operar. Antes de hoy el cliente
llegaba hasta la reserva y de ahí en adelante todo lo empujaba yo desde un archivo de peticiones;
ahora cada final del proceso se alcanza usando el sistema, y hay un documento que lo demuestra en una
sola consulta. Lo que queda de la Entrega 3 ya no es construir, es grabar.

## Estado de la Entrega 3

| Criterio | Estado |
|---|---|
| Cobertura del proceso de negocio (20) | ✅ el cliente reserva, paga y adjunta; la voluntaria resuelve el resto |
| Uso de BPMN, Flowable y automatización (15) | ✅ |
| Proceso ejecutándose en Flowable (15) | ✅ los seis finales alcanzados desde la interfaz |
| Integración de Web Services con el proceso (15) | ✅ |
| Funcionamiento integral y pruebas (10) | ✅ seis escenarios documentados con evidencia del historial |
| Interfaces de usuario (5) | ✅ catálogo, checkout, seguimiento y bandeja |
| Repositorio GitHub (5) | ✅ |
| Trabajo en equipo y gestión (5) | ✅ actas al día |
| Video para emprendedora (5) | ☐ |
| Video para profesor (5) | ☐ |

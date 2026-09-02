# Pruebas de escenarios

El proceso tiene **seis finales distintos**. Este documento recorre los seis, uno por escenario de
negocio, y deja la evidencia de que cada uno se alcanza de verdad.

La idea es que no haya que creerme: al final hay **una sola consulta** al historial del motor que
muestra las seis instancias terminadas, cada una en un final distinto. Es comprobable en cinco
segundos y no depende de capturas de pantalla.

---

## Los seis finales del modelo

| Final en el BPMN | Qué significa para el negocio |
|---|---|
| `EndNoneEvent_31` · Pedido retirado | El cliente pagó, se le aprobó y retiró en la sede |
| `EndNoneEvent_37` · Despachado por voluntario | Igual, pero lo llevó un voluntario |
| `EndNoneEvent_41` · Despachado por courier | Igual, pero salió por encomienda |
| `EndNoneEvent_19` · Pedido cancelado | La voluntaria revisó el comprobante y no lo aprobó |
| `EndNoneEvent_44` · Cancelado por vencimiento | Pasaron las 24 horas y nadie transfirió |
| `EndNoneEvent_51` · Cancelado por falta de stock | El objeto ya se lo había llevado otra persona |

Los tres primeros son ventas cerradas y los tres últimos son las formas de perderla. Que el proceso
distinga entre ellas es lo que permite saber después **por qué** se cayó un pedido.

---

## Preparación

Los cuatro servicios arriba, en este orden. Sin el worker, tres de los seis escenarios se quedan a
medio camino esperando una tarea automática que nadie toma.

```
docker start flowable
cd ws-pedidos ; .\gradlew.bat run
cd worker     ; .\.venv\Scripts\python.exe worker.py
```

La web va aparte, porque el escenario del vencimiento necesita que el plazo de pago sea corto. En
producción son 24 horas; para probar, dos minutos:

```
cd web ; $env:PLAZO_PAGO="PT2M" ; .\.venv\Scripts\python.exe app.py
```

Ese valor sale de una variable de entorno justamente para esto: el temporizador del modelo lee
`plazoPago`, que la web pone al arrancar cada instancia. No hay que tocar el BPMN ni el código.

**Anota la hora antes de empezar**, en UTC. La consulta final filtra por ella para no mezclar estas
pruebas con instancias viejas.

---

## Escenario 1 · El cliente retira

**Qué representa.** La venta que sale bien y es el caso más común: alguien compra, paga y pasa a
buscar su cosa.

1. Elegir un objeto en el catálogo y reservarlo con la modalidad **retiro**.
2. En la página del pedido, subir el comprobante.
3. En la bandeja, abrir la tarea de revisión y **aprobar el pago**.
4. Esperar a que el worker descuente el inventario. El proceso llega solo a «Preparar pedido».
5. Cerrar «Preparar pedido», «Marcar listo para retiro» y «Registrar retiro».

**Resultado esperado:** `EndNoneEvent_31` · Pedido retirado. Y el objeto desaparece del catálogo,
porque su stock quedó en cero.

---

## Escenario 2 · La voluntaria no aprueba el pago

**Qué representa.** Llegó un comprobante que no calza: el monto está mal, la fecha no corresponde o la
imagen no se entiende.

1. Reservar y subir el comprobante, igual que en el escenario 1.
2. En la bandeja, **cancelar el pedido** escribiendo el motivo. El mensaje es obligatorio: el endpoint
   lo exige y el formulario también.
3. El worker toma «Registrar rechazo» y después «Notificar cliente».

**Resultado esperado:** `EndNoneEvent_19` · Pedido cancelado.

Vale la pena mirar que **el inventario nunca se tocó**. El descuento ocurre después del gateway del
pago, así que un rechazo no tiene que devolver nada: los objetos nunca salieron del catálogo.

---

## Escenario 3 · Se vence el plazo

**Qué representa.** Alguien reserva, dice que va a transferir y no lo hace. Es el problema que
originó todo el proyecto.

1. Reservar un objeto y **no hacer nada más**. No subir comprobante.
2. Esperar a que se cumpla el `plazoPago`.
3. El temporizador adjunto a «Adjuntar comprobante» interrumpe la tarea y el worker toma
   «Cancelar pedido».

**Resultado esperado:** `EndNoneEvent_44` · Pedido cancelado por vencimiento.

Este es el único escenario donde **nadie hace nada** y el proceso avanza igual. Es también el que
demuestra por qué el plazo se modeló como temporizador adjunto y no como un paso de espera: si el
cliente hubiera pagado a los cinco minutos, el temporizador se habría cancelado solo.

---

## Escenario 4 · Dos personas, un solo objeto

**Qué representa.** El caso que la agrupación ya vive hoy y resuelve a mano: dos personas alcanzan a
reservar la misma cosa, y solo una se la puede llevar.

1. Desde **dos sesiones distintas**, reservar el mismo objeto. Las dos reservas se crean sin problema.
2. Comprobar que el stock **sigue en 1**: reservar no descuenta nada.
3. Al primer cliente: subir comprobante y aprobar. El worker descuenta y el stock baja a 0.
4. Al segundo cliente: subir comprobante y aprobar también.

**Resultado esperado:** el primero llega a «Preparar pedido» con `stockOk = true`; el segundo termina
en `EndNoneEvent_51` · Cancelado por falta de stock, con `stockOk = false`.

Este escenario prueba de una vez las dos decisiones que sostienen el inventario: que la reserva **no**
descuenta —para que nadie pierda su objeto mientras decide— y que el descuento es una operación
atómica en el web service, así que dos aprobaciones simultáneas no pueden dejar el stock en negativo.

---

## Escenario 5 · Lo lleva un voluntario

**Qué representa.** El cliente no puede ir a la sede y alguien de la agrupación se lo acerca.

1. Reservar con la modalidad **despacho**.
2. Subir comprobante y aprobar el pago.
3. Cerrar «Preparar pedido». El gateway de modalidad manda el pedido a «Gestionar despacho» en vez de
   a «Marcar listo para retiro».
4. En esa tarea, elegir **Lo lleva un voluntario**.
5. Cerrar «Registrar despacho por voluntario».

**Resultado esperado:** `EndNoneEvent_37` · Despachado por voluntario.

---

## Escenario 6 · Sale por courier

**Qué representa.** El cliente está lejos y hay que mandarlo por encomienda.

Igual que el escenario 5 hasta el paso 4, pero eligiendo **Va por courier**. El proceso agrega un paso
más, «Registrar datos de envío», que es donde la voluntaria anota la dirección y el número de
seguimiento.

**Resultado esperado:** `EndNoneEvent_41` · Despachado por courier.

Los escenarios 5 y 6 son los que prueban el **segundo gateway anidado**: primero se decide retiro o
despacho, y solo dentro del despacho se decide quién lo lleva.

---

## La evidencia

Una sola petición al historial del motor, filtrando desde la hora en que se empezó:

```
GET http://localhost:8080/flowable-rest/service/history/historic-process-instances
    ?processDefinitionKey=ventaMapuescuela
    &startedAfter=2026-09-02T01:55:38Z
    &finished=true
Authorization: Basic rest-admin:test
```

El campo que importa de cada instancia es **`endActivityId`**: dice en qué evento de fin terminó. Si
los seis escenarios se corrieron bien, salen seis instancias con seis valores distintos.

### Corrida del 1 de septiembre de 2026

| Pedido | Escenario | `endActivityId` | Duración |
|---|---|---|---|
| MAP-0069 | 1 · El cliente retira | `EndNoneEvent_31` | 32 s |
| MAP-0070 | 2 · Pago no aprobado | `EndNoneEvent_19` | 19 s |
| MAP-0068 | 3 · Plazo vencido | `EndNoneEvent_44` | 129 s |
| MAP-0074 | 4 · Sin stock | `EndNoneEvent_51` | 50 s |
| MAP-0071 | 5 · Despacho por voluntario | `EndNoneEvent_37` | 34 s |
| MAP-0072 | 6 · Despacho por courier | `EndNoneEvent_41` | 34 s |

**Seis finales distintos de seis posibles.** Los 129 segundos del escenario 3 son el plazo de dos
minutos más lo que tardó el worker en tomar la cancelación.

El pedido MAP-0073 es el cliente que sí alcanzó a llevarse el objeto en disputa del escenario 4. Queda
en «Preparar pedido» a propósito: no se cerró para que la consulta de instancias terminadas devuelva
exactamente los seis escenarios.

---

## Qué no cubren estas pruebas

Para que quede claro dónde termina la evidencia:

- **No prueban las notificaciones.** El worker registra que hay que avisarle al cliente, pero todavía
  no se manda ningún correo ni mensaje.
- **No prueban la concurrencia real.** El escenario 4 monta la carrera en secuencia, un cliente
  después del otro. La atomicidad del descuento está resuelta en un `UPDATE ... WHERE stock >= 1`
  dentro de una transacción, pero no hay una prueba con dos peticiones simultáneas de verdad.
- **No prueban «pedirle otra foto» al cliente**, porque el modelo todavía no tiene esa rama: el
  gateway del pago solo distingue entre aprobar y rechazar.
- **No son automáticas.** Hay que correrlas a mano siguiendo estos pasos. Para el tamaño del proyecto
  es un costo razonable, pero conviene decirlo.

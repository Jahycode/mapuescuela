# Modelo BPMN del proceso de venta

Acá está documentado el modelo que corre en Flowable: qué hace cada paso, qué variables usa y qué
topics tiene que atender el worker. Es mi referencia de trabajo, así que este sí lo dejo detallado.

| Archivo | Qué es |
|---|---|
| [`ventaMapuescuela.bpmn`](ventaMapuescuela.bpmn) | El proceso automatizado (TO-BE). Es el que se despliega |
| [`ventaManualAsIs.bpmn`](ventaManualAsIs.bpmn) | Cómo venden hoy (AS-IS). Solo documenta, no se ejecuta |

## El flujo

```
(●) Pedido creado
     │
     ▼
[👤 Adjuntar comprobante] ──⏰ 24 h──▶ [⚙ Cancelar pedido] ──▶ (◉) Pedido cancelado por vencimiento
     │
     ▼
[👤 Revisar comprobante de pago]
     │
     ▼
 <✕ ¿Pago aprobado?>
     ├─ No (default) ─▶ [⚙ Registrar rechazo] ─▶ [⚙ Notificar cliente] ─▶ (◉) Pedido cancelado
     │
     └─ Sí ─▶ [⚙ Descontar inventario]
                  │
                  ▼
              <✕ ¿Había stock?>
                  ├─ No (default) ─▶ [⚙ Notificar falta de stock] ─▶ (◉) Cancelado por falta de stock
                  │
                  └─ Sí ─▶ [👤 Preparar pedido]
                              │
                              ▼
                          <✕ ¿Modalidad de entrega?>
                              ├─ Retiro ─▶ [👤 Marcar listo] ─▶ [👤 Registrar retiro] ─▶ (◉) Pedido retirado
                              │
                              └─ Despacho (default) ─▶ [👤 Gestionar despacho]
                                                            │
                                                            ▼
                                                        <✕ ¿Voluntario o courier?>
                                                            ├─ Courier ─▶ [👤 Registrar datos de envío] ─▶ (◉) Despachado por courier
                                                            └─ Voluntario (default) ─▶ [👤 Registrar despacho] ─▶ (◉) Despachado por voluntario
```

`👤` tarea humana · `⚙` external worker (automática) · `✕` gateway exclusivo · `⏰` boundary timer interruptor

En total: **8 tareas humanas, 5 automáticas, 4 gateways y 6 finales distintos**.

## Por qué cada final es distinto

Podría haber cerrado todo en un solo círculo, pero los dejé separados a propósito: en el historial
del motor puedo distinguir si un pedido terminó bien, si se venció, si lo rechazaron o si no había
stock. Eso me sirve para el seguimiento del cliente y para las demostraciones.

## Variables del proceso

| Variable | Tipo | Quién la escribe | Cuándo |
|---|---|---|---|
| `pedidoId` | número | La web | Al iniciar la instancia |
| `clienteNombre`, `clienteEmail` | texto | La web | Al iniciar |
| `montoTotal` | número | La web | Al iniciar |
| `modalidadEntrega` | `RETIRO` o `DESPACHO` | La web | Al iniciar (el cliente eligió en el checkout) |
| `plazoPago` | duración ISO-8601 | La web | Al iniciar. `PT24H` real, `PT2M` para demostrar el vencimiento sin esperar un día |
| `esAprobado` | booleano | El voluntario | Al revisar el comprobante |
| `motivoRechazo` | texto | El voluntario | Solo si rechaza |
| `stockOk` | booleano | El worker | Al terminar de descontar inventario |
| `tipoDespacho` | `VOLUNTARIO` o `COURIER` | El voluntario | Al gestionar el despacho |

## Topics que tiene que atender el worker

| Topic | Qué hace | Devuelve |
|---|---|---|
| `cancelarPedidoVencido` | Cancela el pedido porque se acabó el plazo | — |
| `registrarRechazo` | Deja registrado que el pago fue rechazado y por qué | — |
| `notificarCliente` | Le avisa al cliente que su pedido se canceló | — |
| `descontarInventario` | Baja el stock del artículo | `stockOk` |
| `notificarFaltaStock` | Le avisa al cliente que el artículo ya no estaba y hay que devolverle | — |

> El descuento de stock tiene que ser **una sola operación atómica** en la base de datos
> (`UPDATE producto SET stock = stock - 1 WHERE id = ? AND stock > 0`), y `stockOk` es simplemente si
> afectó alguna fila. Si consulto primero y descuento después, vuelve el problema de dos clientes
> comprando lo mismo al mismo tiempo.

## Los tres escenarios que voy a demostrar

**1. Camino feliz.** El pedido nace en el checkout y queda esperando el comprobante, con el timer
programado. El cliente lo sube, el timer se cancela solo, el voluntario aprueba, el worker descuenta
el stock y el pedido se entrega. Termina en retiro o en despacho.

**2. Se vence el plazo.** Nadie sube el comprobante. Cuando se cumple `plazoPago`, el timer elimina
la tarea y manda el pedido a cancelación. No hay que devolver stock **porque nunca se descontó**: el
stock solo baja cuando se aprueba el pago.

**3. Rechazo.** El voluntario revisa y rechaza. Como el flujo default del gateway es justamente el
rechazo, aunque la variable llegara vacía el pedido nunca se aprobaría por accidente.

## Decisiones de modelado

**Sin pools ni lanes.** El motor de Flowable no los ejecuta — lo dijo el profesor en clase — así que
los roles los manejo en la aplicación. El diagrama queda 100 % ejecutable.

**Un timer pegado a la tarea, no un paso de "esperar 24 horas".** Si hubiera puesto una espera en el
flujo, el proceso se quedaría parado las 24 horas aunque el cliente pague en cinco minutos. Con el
boundary timer, el proceso avanza apenas llega el comprobante y el timer se cancela solo.

**Los flujos default apuntan siempre al camino seguro** (rechazar, no hay stock, despachar). Si una
variable llegara nula, el proceso nunca va a aprobar un pago ni entregar un producto por accidente.

**Cada rama de entrega termina en su propio final,** sin unirlas antes. Si las hubiera cerrado con un
gateway paralelo, la instancia quedaría esperando eternamente un token que nunca va a llegar.

**Los CRUD no son procesos BPMN.** Mantener productos, categorías o usuarios no tiene coordinación ni
esperas ni decisiones de negocio: son mantenedores de la aplicación. El enunciado lo pide así.

## Comparación con el proceso actual

Las mejoras del TO-BE respecto al AS-IS están en [`AS-IS-vs-TO-BE.md`](AS-IS-vs-TO-BE.md).

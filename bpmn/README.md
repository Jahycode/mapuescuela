# Modelo BPMN — Proceso de Venta Mapuescuela

Archivo: [`venta-mapuescuela.bpmn`](venta-mapuescuela.bpmn) · `process id="ventaMapuescuela"` · ejecutable en Flowable.

## Vista general del flujo

```
(●) Pedido creado
 │
 ▼
[👤 Adjuntar comprobante] ──⏰ 24h vence──▶ [⚙ cancelarPedidoVencido] ──▶ (◉) Cancelado por vencimiento
 │ comprobante subido
 ▼
[👤 Revisar comprobante]
 ▼
<✕ ¿Pago aprobado?>
 ├─ NO (default) ──▶ [⚙ registrarRechazo] ──▶ (◉) Cancelado por rechazo
 └─ SÍ ──▶ [⚙ descontarInventario]
            ▼
          <✕ ¿Stock disponible?>
            ├─ NO (default) ──▶ [⚙ cancelarPorStock] ──▶ (◉) Cancelado por falta de stock
            └─ SÍ ──▶ [👤 Preparar pedido]
                       ▼
                     <✕ ¿Modalidad?>
                       ├─ RETIRO ──▶ [👤 Listo p/ retiro] ─▶ [👤 Registrar retiro] ─┐
                       └─ DESPACHO (default) ──▶ [👤 Registrar despacho] ───────────┤
                                                                                    ▼
                                                                          (◉) Pedido finalizado
```

`👤` = tarea humana (user task) · `⚙` = external worker task (automática) · `✕` = gateway exclusivo · `⏰` = boundary timer interruptor

## Diccionario de elementos

| Id | Nombre | Tipo BPMN | Responsable | Efecto de negocio |
|---|---|---|---|---|
| `startPedidoCreado` | Pedido creado (checkout) | Start Event (none) | Web (cliente) | Nace la instancia; el pedido ya existe en BD con sus ítems |
| `utAdjuntarComprobante` | Adjuntar comprobante | User Task | Cliente (vía web) | Espera del pago; estado *Pendiente de pago* |
| `timerPlazoPago` | Plazo de pago vencido | **Interrupting Boundary Timer Event** (`timeDuration = ${plazoPago}`) | Motor | A las 24 h elimina la tarea y desvía a cancelación |
| `ewCancelarVencido` | Cancelar por vencimiento | Service Task `external-worker` topic `cancelarPedidoVencido` | Worker | Pedido → *Cancelado* (stock intacto: nunca se descontó) |
| `utRevisarComprobante` | Revisar comprobante | User Task | Voluntario | Decide con `esAprobado` (+ `motivoRechazo`); estado *Pago en revisión* |
| `gwAprobado` | ¿Pago aprobado? | Exclusive Gateway (default → rechazo) | Motor | Bifurca según `esAprobado` |
| `ewRegistrarRechazo` | Registrar rechazo y notificar | Service Task `external-worker` topic `registrarRechazo` | Worker | *Pago rechazado* → *Cancelado* + notificación |
| `ewDescontarInventario` | Descontar inventario | Service Task `external-worker` topic `descontarInventario` | Worker → WS Java | *Pago aprobado*; descuento atómico (`UPDATE ... WHERE stock >= cantidad`); produce `stockOk` |
| `gwStock` | ¿Stock disponible? | Exclusive Gateway (default → sin stock) | Motor | Caso borde de artículos únicos |
| `ewCancelarPorStock` | Cancelar por falta de stock | Service Task `external-worker` topic `cancelarPorStock` | Worker | *Cancelado* + notificación de devolución |
| `utPrepararPedido` | Preparar pedido | User Task | Voluntario | Estado *En preparación* |
| `gwModalidad` | ¿Modalidad de entrega? | Exclusive Gateway (default → despacho) | Motor | Según `modalidadEntrega` |
| `utMarcarListoRetiro` | Listo para retiro | User Task | Voluntario | Estado *Listo para retiro* |
| `utRegistrarRetiro` | Registrar retiro | User Task | Voluntario | El cliente retiró en Padre Hurtado |
| `utRegistrarDespacho` | Registrar despacho | User Task | Voluntario | Estado *Enviado*: courier + N° seguimiento + fecha |
| `gwUnionEntrega` | Entrega gestionada | Exclusive Gateway (unión) | Motor | Une los caminos alternativos (llega solo uno; **no** es paralelo) |
| `endFinalizado` / `endCancelado*` | Fines diferenciados | End Events | Motor | 4 desenlaces distinguibles en el histórico |

## Variables del proceso

| Variable | Tipo | Quién la escribe | Cuándo |
|---|---|---|---|
| `pedidoId` | int | Web | Al iniciar la instancia |
| `clienteNombre`, `clienteEmail` | string | Web | Al iniciar |
| `montoTotal` | int | Web | Al iniciar |
| `modalidadEntrega` | string (`RETIRO`\|`DESPACHO`) | Web | Al iniciar (el cliente la eligió en el checkout) |
| `plazoPago` | string ISO-8601 (`PT24H` / `PT2M` en demo) | Web (desde config) | Al iniciar — **parametrizado para poder demostrar el vencimiento** |
| `esAprobado` | boolean | Voluntario (al completar revisión) | Decisión del pago |
| `motivoRechazo` | string | Voluntario | Solo si rechaza |
| `stockOk` | boolean | Worker `descontarInventario` | Resultado del descuento |

## Topics de external workers

| Topic | Qué hace el worker | A quién llama |
|---|---|---|
| `cancelarPedidoVencido` | Cancela pedido (motivo vencimiento) + notifica | `ws-pedidos` |
| `registrarRechazo` | Marca rechazo, cancela + notifica | `ws-pedidos` |
| `descontarInventario` | Descuento condicional atómico por línea; devuelve `stockOk` | `ws-pedidos` |
| `cancelarPorStock` | Cancela (motivo sin stock) + notifica | `ws-pedidos` |

## Estados del pedido (derivados del motor)

El motor es la **fuente de la verdad** del flujo: la BD guarda el `processInstanceId` y el estado se
deriva de dónde está el token (consulta a `runtime/tasks` / `history/historic-activity-instances`):

| Estado del enunciado | Se deriva de |
|---|---|
| Pendiente de pago | Token en `utAdjuntarComprobante` |
| Pago en revisión | Token en `utRevisarComprobante` |
| Pago rechazado | Histórico pasó por `ewRegistrarRechazo` |
| Pago aprobado | Histórico pasó por `ewDescontarInventario` |
| En preparación | Token en `utPrepararPedido` |
| Listo para retiro | Token en `utRegistrarRetiro` (ya se marcó listo) |
| Enviado | Histórico pasó por `utRegistrarDespacho` |
| Finalizado | Instancia terminó en `endFinalizado` |
| Cancelado | Instancia terminó en cualquiera de los 3 fines de cancelación (con su motivo) |

## Los 3 escenarios de demostración (recorrido del token)

1. **Camino feliz:** el token nace en el checkout → espera en *Adjuntar comprobante* (el timer queda
   programado) → el cliente sube el comprobante (el timer se elimina solo) → espera en *Revisar* →
   voluntario aprueba → el worker descuenta stock (`stockOk=true`) → *Preparar* → retiro o despacho
   → **Pedido finalizado**.
2. **Vencimiento (24 h):** el token espera en *Adjuntar comprobante* y nadie sube nada → al cumplirse
   `plazoPago`, el **boundary timer interruptor** elimina la tarea y lleva el token por
   `ewCancelarVencido` → **Cancelado por vencimiento**. No se libera stock **porque nunca se
   descontó** (regla del caso: el stock solo baja al aprobar el pago).
3. **Rechazo:** el voluntario completa la revisión con `esAprobado=false` → el gateway (cuyo flujo
   **default** es el rechazo, a prueba de variables faltantes) lleva el token por
   `ewRegistrarRechazo` → **Cancelado por rechazo**, con notificación del motivo al cliente.

## Decisiones de modelado (resumen — detalle en `docs/DECISIONES.md`)

- **Sin pools/lanes:** el motor de Flowable no los ejecuta (indicación del profesor); los roles se
  gestionan en la aplicación. El diagrama queda 100 % ejecutable.
- **Boundary timer interruptor** y no un paso "esperar 24 h" en el flujo: el proceso avanza apenas
  llega el comprobante; el timer solo actúa si se cumple el plazo.
- **Gateways con flujo default hacia el camino seguro** (rechazo / sin stock / despacho): si una
  variable llega nula, el proceso nunca aprueba ni entrega por accidente.
- **La unión de retiro/despacho es un gateway exclusivo**, no paralelo: llega un solo camino;
  cerrar con paralelo dejaría la instancia esperando un token que jamás llegará (deadlock).
- **Los CRUD (productos, categorías, usuarios) no son procesos BPMN**: no tienen coordinación,
  esperas ni decisiones de negocio — son mantenedores de la aplicación (criterio del enunciado).

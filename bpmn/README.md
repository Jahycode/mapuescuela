# bpmn/ — Los modelos del proceso de venta

Acá están los dos modelos BPMN del proyecto, hechos en Flowable Design.

| Archivo | Qué es |
|---|---|
| `ventaManualAsIs.bpmn` | Cómo venden **hoy**: Instagram, WhatsApp y cuaderno. Solo documenta, no se ejecuta |
| `ventaMapuescuela.bpmn` | El proceso **automatizado**. Es el que se despliega y corre en Flowable |

## El proceso automatizado

```
(●) Pedido creado
     ▼
[👤 Adjuntar comprobante] ──⏰ 24 h──▶ [⚙ Cancelar pedido] ──▶ (◉) Cancelado por vencimiento
     ▼
[👤 Revisar comprobante]
     ▼
 ◈ ¿Pago aprobado?
     ├─ No ──▶ [⚙ Registrar rechazo] ─▶ [⚙ Notificar cliente] ─▶ (◉) Pedido cancelado
     └─ Sí ──▶ [⚙ Descontar inventario]
                    ▼
                ◈ ¿Había stock?
                    ├─ No ──▶ [⚙ Notificar falta de stock] ──▶ (◉) Cancelado por falta de stock
                    └─ Sí ──▶ [👤 Preparar pedido]
                                   ▼
                               ◈ ¿Modalidad de entrega?
                                   ├─ Retiro ───▶ [👤 Marcar listo] ─▶ [👤 Registrar retiro] ─▶ (◉) Pedido retirado
                                   └─ Despacho ─▶ [👤 Gestionar despacho] ─▶ ◈ ¿Voluntario o courier? ─▶ (◉) Despachado
```

8 tareas humanas, 5 automáticas, 4 gateways, un temporizador y 6 finales distintos.

## El contrato con el worker

Las tareas automáticas no las ejecuta el motor: publica un trabajo por *topic* y lo toma un programa
externo.

| Topic | Devuelve |
|---|---|
| `cancelarPedidoVencido` | — |
| `registrarRechazo` | — |
| `notificarCliente` | — |
| `descontarInventario` | `stockOk` |
| `notificarFaltaStock` | — |

Variables que maneja el proceso: `pedidoId`, `clienteNombre`, `clienteEmail`, `montoTotal`,
`modalidadEntrega` y `plazoPago` llegan desde el checkout; `esAprobado` y `motivoRechazo` las escribe
el voluntario al revisar; `stockOk` la devuelve el worker; `tipoDespacho` se decide al gestionar el
despacho.

## Por qué está modelado así

- **Sin pools ni lanes**, porque el motor no los ejecuta. Los roles los maneja la aplicación.
- **Un temporizador pegado a la tarea** en vez de un paso "esperar 24 horas": el proceso avanza apenas
  llega el comprobante, y el timer se cancela solo.
- **Los flujos default apuntan siempre al camino seguro** (rechazar, asumir sin stock, despachar). Si
  una variable llega vacía, el proceso nunca aprueba un pago ni entrega un producto por accidente.
- **Cada rama de entrega termina en su propio final**, sin unirlas antes. Así el sistema sabe en qué
  terminó cada pedido con solo mirar dónde cerró la instancia.

## Qué mejora respecto al proceso actual

| Problema de hoy | Cómo lo resuelve |
|---|---|
| No hay plazo para pagar y el producto queda bloqueado | Temporizador de 24 h que cancela solo |
| Instagram no sirve de catálogo | Catálogo con precio y disponibilidad al día |
| El cuaderno se puede perder | Base de datos consultable y respaldable |
| Se puede vender dos veces el mismo artículo | Stock descontado al aprobar, con rama para el quiebre |
| El cliente no puede consultar su pedido | Página de seguimiento con token |

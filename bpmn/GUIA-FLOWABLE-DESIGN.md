# Guía: dibujar el proceso en Flowable Design

> Objetivo: reproducir `venta-mapuescuela.bpmn` en **Flowable Design** (versión licenciada del
> convenio) con tus credenciales de alumno. El XML de este repo es la **referencia**: al terminar,
> tu modelo debe tener los mismos elementos, ids, topics y condiciones.

## Antes de empezar

1. Entra a Flowable Design con tus credenciales (URL del anuncio del profesor).
2. Crea una **App** (ej. `Mapuescuela`) y dentro un **Process model**: nombre `Venta de artículos
   Mapuescuela`, key **`ventaMapuescuela`** (la key es crítica: la usa la web para iniciar instancias).

## Orden de dibujo recomendado (espina primero, ramas después)

### 1. La espina del camino feliz
1. **Start event** (círculo simple) → renómbralo `Pedido creado (checkout)`.
2. **User task** `Adjuntar comprobante de transferencia` (id sugerido: `utAdjuntarComprobante`).
3. **User task** `Revisar comprobante de pago` (`utRevisarComprobante`).
4. **Exclusive gateway** `¿Pago aprobado?` (`gwAprobado`).
5. En la paleta busca **External Worker task** → `Descontar inventario`
   (`ewDescontarInventario`) y en sus propiedades pon **Topic = `descontarInventario`**.
6. **Exclusive gateway** `¿Stock disponible?` (`gwStock`).
7. **User task** `Preparar pedido` (`utPrepararPedido`).
8. **Exclusive gateway** `¿Modalidad de entrega?` (`gwModalidad`).
9. Rama retiro: **User task** `Marcar pedido listo para retiro` → **User task** `Registrar retiro
   del pedido`. Rama despacho: **User task** `Registrar despacho (empresa, N° seguimiento, fecha)`.
10. **Exclusive gateway** de unión `Entrega gestionada` (`gwUnionEntrega`) → **End event**
    `Pedido finalizado`.

### 2. El timer de 24 horas (lo más importante)
1. Arrastra un **Boundary timer event** y suéltalo **sobre el borde** de la tarea
   `Adjuntar comprobante` (debe quedar "pegado" a la tarea).
2. En propiedades: **Time duration** = `${plazoPago}` (expresión, no un valor fijo).
3. Verifica que **Cancel activity / Interrupting = true** (interruptor). Es lo que hace que al
   vencer el plazo la tarea se elimine y el pedido se cancele.
4. Desde el timer, conecta a un **External Worker task** `Cancelar pedido por vencimiento`
   (topic `cancelarPedidoVencido`) → **End event** `Pedido cancelado por vencimiento`.

### 3. Las ramas de rechazo y sin stock
1. De `gwAprobado`: **External Worker task** `Registrar rechazo y notificar` (topic
   `registrarRechazo`) → **End event** `Pedido cancelado por rechazo de pago`.
2. De `gwStock`: **External Worker task** `Cancelar por falta de stock` (topic `cancelarPorStock`)
   → **End event** `Pedido cancelado por falta de stock`.

### 4. Las condiciones de los gateways (y los defaults)
En cada flecha que sale de un gateway, en **Condition**:

| Gateway | Flecha | Condición |
|---|---|---|
| `¿Pago aprobado?` | hacia Descontar inventario | `${vars:equals(esAprobado, true)}` |
| `¿Pago aprobado?` | hacia Registrar rechazo | **marcar como Default flow** (sin condición) |
| `¿Stock disponible?` | hacia Preparar pedido | `${vars:equals(stockOk, true)}` |
| `¿Stock disponible?` | hacia Cancelar por stock | **Default flow** |
| `¿Modalidad?` | hacia Listo para retiro | `${vars:equals(modalidadEntrega, 'RETIRO')}` |
| `¿Modalidad?` | hacia Registrar despacho | **Default flow** |

> ¿Por qué los default apuntan al camino "malo"? Si la variable llega nula o mal escrita, el
> proceso **nunca aprueba ni entrega por accidente**: se va al camino seguro.

### 5. Validar y exportar
1. Usa la **validación de Design** (te marcará si falta un metadato — es justo la gracia de la
   herramienta que destacó el profesor).
2. Exporta el BPMN y guárdalo en este repo reemplazando `venta-mapuescuela.bpmn` (el de Design
   traerá metadatos `design:*` extra y el diagrama visual — perfecto, ese pasa a ser el oficial).
3. Commit: `git add bpmn/ && git commit -m "Modelo de venta dibujado en Flowable Design"`.

## Checklist final (antes de dar por bueno el modelo)

- [ ] Key del proceso = `ventaMapuescuela` y es ejecutable
- [ ] 6 user tasks, 4 external worker tasks (con sus 4 topics exactos), 4 gateways exclusivos
- [ ] Boundary timer **interruptor** sobre `Adjuntar comprobante` con `${plazoPago}`
- [ ] 3 condiciones `vars:equals` + 3 default flows
- [ ] 5 end events con nombre (finalizado + 3 cancelaciones + ninguno genérico sin nombre)
- [ ] La unión de retiro/despacho es un gateway **exclusivo** (no paralelo)
- [ ] Validación de Design sin errores

# Análisis del proceso: AS-IS → TO-BE

Este documento acompaña a los dos modelos BPMN del proyecto y justifica las mejoras propuestas.
Sigue el ciclo de vida de BPM visto en la Unidad 1: *descubrimiento del proceso* → **modelo del
estado actual (AS-IS)** → *análisis de puntos débiles* → **modelo de estado objetivo (TO-BE)**.

| Modelo | Archivo / Key | Propósito |
|---|---|---|
| **AS-IS** | `ventaManualAsIs` | Cómo vende Mapuescuela **hoy**: Instagram + WhatsApp + cuaderno |
| **TO-BE** | `ventaMapuescuela` | Cómo venderá con el sistema, con el proceso automatizado en Flowable |

## 1. Proceso actual (AS-IS)

```
(●) Se recibe artículo donado
      ↓
[👤 Publicar producto en Instagram]
[👤 Cliente comenta o escribe interesado]
[👤 Coordinación por WhatsApp (precio, disponibilidad, entrega)]
[👤 Cliente transfiere y envía captura por WhatsApp]
[👤 Revisar el pago en el chat]
      ↓
   ◇ ¿Pagó? ──No──▶ (◉ Venta no concretada)
      │ Sí
[👤 Anotar la venta en el cuaderno]
[👤 Coordinar y realizar la entrega]
      ↓
(◉ Producto entregado)
```

**Característica clave:** *todas* las actividades son humanas. No existe ninguna automatización, y
el estado de cada venta vive en la memoria del voluntario, en el chat de WhatsApp y en un cuaderno.

## 2. Puntos débiles detectados y cómo los resuelve el TO-BE

| # | Problema del AS-IS | Solución en el TO-BE |
|---|---|---|
| 1 | **Sin plazo de pago.** El cliente dice que va a transferir y desaparece; el producto queda bloqueado indefinidamente y nadie lo detecta. | **Evento de temporización (24 h)** adjunto a la espera del comprobante: si vence, el pedido se cancela automáticamente y el producto vuelve a estar disponible. |
| 2 | **Instagram no es un catálogo.** Para saber qué sigue disponible hay que revisar publicaciones antiguas y recordar cuáles ya se vendieron. | **Catálogo digital** con precio, foto, estado y cantidad disponible por producto. |
| 3 | **Registro en cuaderno.** Se puede perder (se pierde todo el historial), no se puede consultar desde otro lugar y el formato depende de quién anote. | **Base de datos** con estructura fija, consultable y respaldable. |
| 4 | **Riesgo de vender dos veces el mismo artículo.** Son artículos usados, muchos únicos; dos personas pueden comprometerlo casi al mismo tiempo. | **Descuento de stock controlado al aprobar el pago**, con una rama del proceso para el caso "sin stock" que cancela y avisa. |
| 5 | **El cliente no puede consultar su pedido.** La información está en el chat y en la cabeza del voluntario; solo él puede responder. | **Página de seguimiento** donde el cliente ve el estado de su pedido en cualquier momento. |

## 3. Mejora estructural: el proceso deja de vivir en la memoria de una persona

Más allá de cada punto, el cambio de fondo es que en el AS-IS **el proceso no existe en ninguna
parte**: es una costumbre repartida entre Instagram, WhatsApp y un cuaderno. En el TO-BE el proceso
está **modelado y ejecutándose en un motor**, que sabe en qué paso va cada venta, qué falta y qué
vence. Esa es la diferencia entre "ordenar el trabajo" y "automatizar un proceso de negocio".

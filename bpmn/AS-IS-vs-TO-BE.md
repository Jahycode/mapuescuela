# Del proceso actual al automatizado

Antes de modelar el proceso nuevo dibujé cómo venden hoy. La idea es que las mejoras se puedan
justificar mostrando qué problema concreto resuelve cada una, en vez de proponer cosas porque sí.

| Modelo | Archivo | Qué muestra |
|---|---|---|
| **AS-IS** | `ventaManualAsIs.bpmn` | Cómo venden hoy: Instagram, WhatsApp y cuaderno |
| **TO-BE** | `ventaMapuescuela.bpmn` | Cómo van a vender con el sistema |

## Cómo venden hoy

```
(●) Se recibe artículo donado
      ▼
[👤 Publicar producto en Instagram]
[👤 Cliente comenta o escribe interesado]
[👤 Coordinación por WhatsApp: precio, disponibilidad, entrega]
[👤 Cliente transfiere y envía captura por WhatsApp]
[👤 Revisar el pago en el chat]
      ▼
   <✕ ¿Pago?> ──No──▶ (◉) Venta perdida
      │ Sí
      ▼
[👤 Anotar la venta en el cuaderno]
[👤 Coordinar y realizar la entrega]
      ▼
(◉) Producto entregado
```

Lo que salta a la vista: **todas las tareas son humanas**. No hay nada automatizado, y el estado de
cada venta vive repartido entre la memoria del voluntario, el chat de WhatsApp y un cuaderno.

## Las cinco mejoras

**1. Hoy no hay plazo para pagar.** El cliente dice que va a transferir y desaparece; el producto
queda bloqueado sin que nadie se dé cuenta. En el modelo nuevo puse un **temporizador de 24 horas**
pegado a la espera del comprobante: si se cumple el plazo, el pedido se cancela solo y el producto
vuelve a estar disponible.

**2. Instagram no es un catálogo.** Para saber qué queda disponible hay que revisar publicaciones
viejas y acordarse de cuáles ya se vendieron. Con un **catálogo digital** cada producto tiene su
precio, su foto y su disponibilidad al día.

**3. El cuaderno se puede perder.** Si se pierde, se pierde todo el historial, y además no se puede
consultar desde otro lugar. Con una **base de datos** el registro es consultable, respaldable y con
un formato fijo, no depende de quién anote.

**4. Se puede vender dos veces el mismo artículo.** Son cosas usadas y muchas son únicas: dos
personas pueden comprometerla casi al mismo tiempo. Por eso el **stock se descuenta al aprobar el
pago**, y modelé una rama para el caso en que ya no quede: el proceso cancela y avisa al cliente en
vez de prometer algo que no existe.

**5. El cliente no puede consultar su pedido.** Toda la información está en el chat y en la cabeza
del voluntario, así que solo él puede responder. Con una **página de seguimiento** el cliente ve en
qué va su pedido cuando quiera.

## El cambio de fondo

Más allá de cada mejora puntual, lo importante es que hoy **el proceso no existe en ninguna parte**:
es una costumbre repartida entre Instagram, WhatsApp y un cuaderno. En el modelo nuevo el proceso
está corriendo en un motor que sabe en qué paso va cada venta, qué falta y qué se venció. Esa es la
diferencia entre ordenar el trabajo y automatizar un proceso de negocio.

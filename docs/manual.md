# Cómo se usa

Este manual es para quienes atienden los pedidos en Mapuescuela. No hace falta saber nada de
programación.

El sistema hace dos cosas: **publica los objetos donados** para que la gente los reserve, y **les va
avisando qué toca hacer** con cada pedido, uno por uno, hasta que se entrega.

---

## Entrar

La dirección de las tareas es `/bandeja`. También hay un enlace al final del catálogo que dice
**«Entrar a las tareas»**.

Eliges tu nombre y escribes tu clave. Todo lo que hagas después queda firmado con ese nombre por
eso importa entrar con el tuyo y no con el de otra persona.

Cuando termines, el botón **Salir** está arriba a la derecha, junto a tus iniciales.

---

## El día a día: la bandeja

Es la pantalla principal. A la izquierda está la lista de lo que hay por hacer, **lo que más lleva
esperando arriba**. Al tocar una tarea, a la derecha aparece de qué se trata: quién está esperando,
qué objetos lleva el pedido y cuánto es.

Cada tarea tiene un color de urgencia. **Apura** después de cuatro horas esperando, **Atrasado**
después de doce.

Arriba de cada pedido hay una barra con cuatro tramos Pago, Preparación, y los dos últimos según sea
retiro o despacho que muestra en cuál va.

Al cerrar una tarea, el sistema te deja directamente en la siguiente del mismo pedido. No hay que
buscarla.

---

## Revisar un pago

Es la única tarea donde decides algo que no se puede deshacer solo, así que va aparte.

Cuando alguien sube su comprobante, aparece la tarea **Revisar comprobante de pago**. Ahí ves el
monto que debería haber transferido y quién es.

**Si el comprobante está bien**, aprietas *Aprobar el pago*. El sistema descuenta los objetos del
catálogo —desaparecen para el resto— y te deja en la tarea siguiente. Eso demora unos segundos.

**Si algo no calza**, aprietas *Cancelar el pedido*. Se abre una ventana donde tienes que escribirle
al cliente por qué. **Ese texto le llega tal cual**, así que conviene ser claro: «el monto no
coincide», «la foto no se entiende», «la fecha es de otro día». También puedes anotar el monto que
leíste en el comprobante; queda guardado junto a tu nombre por si después hay dudas.

Cancelar **no** devuelve nada al catálogo, porque los objetos nunca salieron: el descuento ocurre
recién cuando alguien aprueba.

---

## Los pasos que siguen

Después del pago, las tareas son de trámite y se cierran con *Listo*:

**Preparar pedido** — buscarlo, revisarlo, dejarlo aparte.

Y de ahí depende de cómo lo pidió el cliente:

| Si es retiro | Si es despacho |
|---|---|
| Marcar listo para retiro | Gestionar despacho: eliges si lo lleva un voluntario o va por courier |
| Registrar retiro, cuando lo pasa a buscar | Registrar el despacho o, con courier, anotar los datos del envío |

**Los datos del envío** son transportista, dirección y número de seguimiento. Ojo con esto: el
cliente **no deja su dirección al reservar**, así que hay que pedírsela. El número de seguimiento es
opcional, por si el courier lo entrega después.

Hay una tarea que **no se cierra desde acá**: *Adjuntar comprobante de transferencia*. Esa la cierra
el cliente cuando sube su foto, o se cancela sola si pasan las 24 horas. Aparece en la lista para que
sepas que está pendiente, pero no tiene botón.

---

## Cargar un objeto

En **Objetos**, el botón amarillo *Cargar un objeto*.

Mientras escribes, a la derecha se va armando la ficha tal como va a verse en el catálogo. Si eliges
una foto, la ves ahí mismo antes de guardar sirve para saber cómo queda recortada.

Lo que pide:

- **Qué es** y **el precio** son obligatorios.
- **La categoría y el estado** salen de una lista.
- **Las medidas** solo aparecen si es un mueble, y son opcionales.
- **Detalles y marcas de uso** es donde va todo lo que conviene que el comprador sepa antes de
  reservar: un rayón, una pata suelta, una mancha. Decirlo evita reclamos después.
- **La foto** es opcional, pero sin foto casi nadie compra.

Cada ficha es **un objeto que se vende una vez**. Si llegan cuatro sillas iguales y se venden por
separado, son cuatro fichas. Si se venden juntas, es una que diga «juego de cuatro sillas».

---

## Editar y retirar

En **Objetos** está todo el registro, lo último cargado primero, con su estado: *En venta*,
*Vendido* o *Retirado*. Los que no tienen foto lo dicen en rojo.

**Editar** sirve para corregir cualquier cosa en cualquier momento, incluso de algo ya vendido.

**Retirar** lo saca del catálogo sin borrarlo: se usa cuando un objeto se rompió, lo regalaron o ya
no está. Se puede volver a publicar cuando quieras. Un objeto **vendido** no se retira ese ya se
fue, y marcarlo como retirado haría parecer que ustedes lo sacaron.

---

## Los datos de la agrupación

En **La agrupación** están el nombre, la dirección, el correo y el Instagram que ve el cliente en
todas las pantallas. Cambiar algo ahí lo cambia en todas.

Abajo está **la cuenta para transferir**. Mientras esté vacía, la página del pedido muestra una
cuenta de ejemplo y **avisa al cliente que esa cuenta no recibe transferencias**. Ese aviso
desaparece solo cuando cargues la de verdad.

El banco y el número son obligatorios si vas a cargarla: con uno solo, nadie podría transferir y el
aviso se habría ido igual.

---

## El histórico

En **Histórico** están los pedidos que ya terminaron: cuántas ventas se cerraron, cuánto se recaudó
y cuáles se perdieron, con el motivo de cada una.

Sirve para responder «¿cuánto vendimos este mes?» sin revisar el cuaderno.

---

## Lo que pasa solo

Hay tres cosas que el sistema hace sin que nadie las apriete:

**El plazo de 24 horas.** Desde que alguien reserva, tiene un día para transferir y subir el
comprobante. Si no lo hace, el pedido se cancela solo y los objetos vuelven al catálogo. Mientras
corre el plazo, nadie más puede comprarlos.

**El descuento del inventario.** Ocurre al aprobar un pago, no antes. Por eso dos personas pueden
reservar la misma cosa: la primera que sea aprobada se la lleva, y la segunda se cancela sola
avisando que ya no había.

**El encadenado de tareas.** Al cerrar una, el sistema abre la siguiente del mismo pedido.

---

## Cuando algo se ve raro

| Qué ves | Qué pasa |
|---|---|
| La pantalla dice que no puede hablar con el sistema | Alguna de las piezas está apagada. Ver `docs/instalacion.md` |
| Aprobaste un pago y la lista quedó vacía unos segundos | Normal: el sistema está descontando el inventario y vuelve solo |
| Una tarea lleva días esperando | Probablemente es *Adjuntar comprobante*: depende del cliente, no de ustedes |
| Un pedido se canceló y nadie lo tocó | Se venció el plazo de 24 horas |
| Un objeto desapareció del catálogo | O se vendió, o alguien lo retiró. En **Objetos** aparecen los dos casos |

Si algo se rompe de verdad, nada se pierde: el sistema guarda cada decisión con la hora y el nombre
de quien la tomó.

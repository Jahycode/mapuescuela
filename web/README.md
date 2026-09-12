# web/ — La aplicación web

La cara visible del sistema, en Python con Flask. No guarda estado propio: le pregunta al motor de
Flowable en qué va cada pedido, y usa `ws-pedidos` para todo lo de negocio.

## Las pantallas

**Para quien compra**, sin clave:

| Ruta | Qué es |
|---|---|
| `/` | El catálogo: lo que está en venta y lo que ya encontró casa |
| `/checkout` | Reservar: nombre, correo y si es retiro o despacho |
| `/pedido/<id>` | El seguimiento, con cuatro estados según en qué va |

**Para la agrupación**, detrás de la llave:

| Ruta | Qué es |
|---|---|
| `/bandeja` | Las tareas pendientes del motor, cruzadas con los pedidos |
| `/bandeja/historico` | Lo que ya terminó: ventas cerradas y perdidas |
| `/admin/objetos` | Cargar, editar y retirar objetos del catálogo |
| `/admin/organizacion` | Los datos de la agrupación y la cuenta para transferir |

## Cómo se corre

Está en [`../docs/instalacion.md`](../docs/instalacion.md).

## Lo que hay que saber para tocarla

**Todo lo interno pide llave**, y la guarda vive en un solo `before_request` que mira si la ruta
empieza con `/bandeja` o `/admin`. Una ruta nueva bajo esos prefijos queda protegida sola.

**El navegador nunca habla con `ws-pedidos`.** Incluso las fotos de los objetos pasan por acá, con
`/objeto/<id>/foto`, para que el cliente conozca una sola dirección.

**La paleta y los tamaños son tokens CSS** en el bloque `:root` de cada hoja de estilo. Cambiar
`--violeta` reestiliza la pantalla entera.

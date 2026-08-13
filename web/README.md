# web/ — La aplicación web

**Pendiente para la Entrega 2.**

Es la cara visible del sistema, en Python. Del lado del cliente: el catálogo, la ficha del producto,
el carrito, el checkout y la página donde sigue su pedido con un link con token. Del lado de
Mapuescuela: el panel donde el voluntario ve sus tareas pendientes y las va completando.

No guarda el estado de los pedidos por su cuenta: se lo pregunta al motor de Flowable por REST, y usa
`ws-pedidos` para las operaciones de negocio.

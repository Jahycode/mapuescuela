# Acta 12 — Un pedido con varios objetos y la primera pantalla conectada

- **Fecha:** sábado 29 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Durante esta sesión resolví el choque que había quedado abierto entre el modelo de datos y el diseño de
las pantallas, y con eso levanté la primera pantalla de la web que muestra información real.

El choque era este: la tabla `pedido` apuntaba a un solo producto mediante `producto_id` y guardaba una
`cantidad`, es decir, un pedido era un producto por N unidades. El diseño dice lo contrario: un pedido
lleva varios objetos y cada objeto existe uno solo. El checkout que diseñé lleva dos objetos distintos
en el mismo pedido. Las dos versiones no podían convivir.

## Lo que hice

### La tabla `pedido_item`

Creé una tabla intermedia con `pedido_id`, `producto_id` y `precio`, sin columna de cantidad. Ahora los
items apuntan al pedido, y por eso puede haber varios. De `pedido` salieron `producto_id` y `cantidad`,
lo que obligó a modificar `insertar()`, `mapear()` y `Pedido.java`.

**El precio se guarda en el item en lugar de consultarse a `producto`.** Si se consultara en vivo,
corregir un precio en el catálogo en septiembre reescribiría el pasado de todos los pedidos ya cerrados:
la clienta que acordó $48.000 en agosto vería otra cifra. Un pedido registra un acuerdo, no una
consulta. La columna `monto_total` se mantiene aunque cada línea tenga su precio, porque el total
incluye el despacho y el despacho no es un objeto.

### La reserva con transacción

`descontarStock(productoId, cantidad)` se reemplazó por `reservarObjetos(List<PedidoItem>)`, que abre
una transacción con `setAutoCommit(false)`, recorre los items ejecutando
`UPDATE producto SET stock = stock - 1 WHERE id = ? AND stock >= 1`, y hace `rollback()` completo si
alguno no afecta una fila.

Esto es necesario porque si un pedido lleva dos objetos y el segundo ya está tomado, el primero no puede
quedar reservado: quedaría en stock 0 sin que nadie lo haya comprado, desaparecería del catálogo y nadie
sabría por qué. Lo probé creando un pedido con la cómoda, que estaba libre, y el velador, que ya había
reservado antes. La reserva bajó la cómoda, se topó con el velador y deshizo todo: la cómoda quedó en
stock 1.

### La base H2 en archivo

Cambié `Db.java` de `jdbc:h2:mem:pedidos` a `jdbc:h2:./data/pedidos`, para que los pedidos sobrevivan a
los reinicios. Venía tropezando seguido con pedidos que Flowable creía vivos y que en mi base ya no
existían, porque el motor persiste y mi base no.

El cambio obligó a proteger la carga inicial del catálogo: los `INSERT INTO producto` se ejecutaban en
cada arranque y, con la base naciendo vacía cada vez, daba lo mismo. Con la base en archivo, al tercer
reinicio habría tenido doce productos en vez de cuatro. Ahora hay un `SELECT COUNT(*)` previo.

### La web en Python

Levanté `web/app.py` con Flask. Consulta `GET /productos` al web service, separa los objetos con stock
de los que están en cero, y se los pasa a una plantilla Jinja que reutiliza el CSS del prototipo. **La
web no tiene base de datos propia: todo lo pregunta.**

### La creación de las tablas al arranque

Al levantar la web por primera vez, `GET /productos` respondió con un 500 y el log decía
`Table "PRODUCTO" not found (this database is empty)`.

La creación de las tablas estaba escrita en un bloque `static` dentro de `PedidoResource`. Un bloque
`static` se ejecuta cuando la clase se carga por primera vez, y eso ocurre recién cuando llega una
petición a `/pedidos`. Como la primera pantalla de la web pide `/productos`, que atiende
`ProductoResource`, ese bloque nunca se ejecutaba y la base quedaba vacía. Venía funcionando por
casualidad, porque siempre probaba primero los pedidos.

Moví la creación a `App.main()`, antes de arrancar el servidor, que es donde corresponde: crear las
tablas es responsabilidad del arranque de la aplicación, no de una clase que atiende direcciones. Donde
estaba, el momento en que se creaban dependía de a qué URL le pegaran primero. Aproveché de agregar que
si la creación falla el servicio no levante, en vez de levantar y fallar en cada petición.

## Error encontrado

Cuando había que decidir qué pasaba con la columna `stock`, mi respuesta fue mantenerla porque nada
impide que se donen dos sillas parecidas, y en ese caso el stock sería 2.

Estaba equivocado, y la prueba estaba en mi propio catálogo. Cuando llegaron dos sillas de comedor
juntas las registré como el **N° 0149, "Par de sillas de comedor"**: una fila, un número, un precio. Y
la silla de mimbre tiene su propio N° 0145. Ya había decidido dos veces que dos objetos donados son dos
filas y no una con stock 2.

Y tiene que ser así, porque dos objetos donados nunca son intercambiables: el 0149 dice "una tiene el
asiento hundido" y el 0145 "al mimbre del respaldo le falta un tramo". Con una sola fila en stock 2 no
puedo escribir a cuál de las dos le pasa qué, y esa descripción es justamente lo que el catálogo promete
que una tienda con inventario no puede dar.

La columna se queda igual, pero por otra razón: es lo único que impide que dos personas que aprietan
"Reservar" en el mismo segundo se lleven el mismo objeto, porque la resta y la comprobación viajan en
una sola sentencia. Con stock 1 funciona idéntico; lo que cambia es qué significa el número, que ya no
es "cuántas quedan" sino "sigue disponible".

Tenía razón en la conclusión y no en el motivo, y el dato que lo resolvió estaba en algo que yo mismo
había hecho.

## Pendientes y decisiones

- A `producto` le faltan las columnas descriptivas que el catálogo promete mostrar: origen, marcas de
  uso, condición y medidas. La plantilla ya las espera con condicionales.
- El botón "Reservar" todavía no hace nada.
- `stock = 0` no distingue "reservado" de "vendido", así que los dos casos caen hoy en la misma sección.
- Faltan las columnas de dirección que el checkout recolecta.

## Cierre

La sesión alineó el modelo de datos con el diseño y dejó el catálogo funcionando contra información
real: los dos objetos que reservé probando aparecen en la sección de los que ya encontraron casa, no
porque estén escritos en el HTML sino porque su stock quedó en cero. Lo que queda como criterio es que
el patrón de una sola sentencia atómica resuelve una fila, y que en cuanto la operación involucra
varias filas que deben ocurrir juntas o ninguna, hace falta una transacción.

## Estado de la Entrega 2

| Criterio | Estado |
|---|---|
| Modelo BPMN ejecutable | ✅ |
| Modelo descriptivo AS-IS | ✅ |
| Uso de tareas BPMN y external workers | ✅ |
| Proceso ejecutándose en Flowable | ✅ las seis salidas recorridas |
| Funcionamiento y prueba de web services | ✅ |
| Repositorio GitHub | ✅ |
| Gestión y planificación | ✅ |
| Web services que cubren el proceso | ✅ modelo nuevo, reserva de varios objetos a la vez |
| Interfaces de usuario | ◐ catálogo conectado; faltan checkout, seguimiento y bandeja |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |

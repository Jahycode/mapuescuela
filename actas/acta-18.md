# Acta 18 — La agrupación ya no necesita que yo recompile nada

- **Fecha:** viernes 11 de septiembre de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Hasta ayer el catálogo eran diez objetos escritos a mano dentro de una clase Java, y los datos de la
agrupación estaban dentro de tres plantillas HTML. Eso significaba que para publicar un mueble o
corregir una cuenta bancaria hacía falta yo. Hoy las voluntarias cargan objetos, los editan, los
retiran y cambian sus propios datos, todo desde una pantalla.

Es el criterio que más pesa del examen veinticinco puntos y su nivel más alto habla de un MVP
«listo para ser utilizado». Sin esto no lo estaba.

## Lo que hice

### Los objetos, por REST

`ProductoResource` pasó de tener un solo `GET` a seis endpoints: crear, editar, retirar o volver a
publicar, subir una foto y servirla. `Producto` ganó dos columnas, `retirado` y `foto`.

**Retirar no borra.** `pedido_item` apunta a `producto` con una clave foránea, así que un `DELETE`
rompería los pedidos viejos. Y `retirado` es distinto de `stock = 0`: lo primero significa que la
agrupación lo sacó, lo segundo que alguien lo compró. Por eso el botón de retirar solo aparece
mientras el objeto siga en stock — marcar como retirado algo vendido lo contaría en la columna
equivocada del resumen.

Las columnas nuevas entraron con `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`. Hasta ahora cada cambio
de esquema obligaba a borrar la base y perder los datos, porque `CREATE TABLE IF NOT EXISTS` no
agrega columnas a una tabla que ya existe.

Probé los veintidós casos: los seis endpoints, las validaciones, los 404, y que el `PUT` no toque
`stock` ni `retirado` aunque lleguen en el JSON.

### Las pantallas

`/admin/objetos` lista todo el registro con el estado de cada uno y avisa en rojo cuáles no tienen
foto. El formulario sirve para cargar y para editar: cambia el destino y el texto del botón, nada
más.

Al costado del formulario hay una **vista previa** que arma la ficha del catálogo mientras se escribe,
y que muestra la foto elegida antes de subirla. Sirve para ver cómo queda recortada, que es donde se
pierden las fotos mal encuadradas.

Las fotos las sirve Flask desde `/objeto/<id>/foto` y las trae de `ws-pedidos` por detrás: **el
navegador nunca conoce el puerto 9090**. La dirección lleva el nombre del archivo como parámetro, y
como ese nombre incluye la marca de tiempo de la subida, reemplazar una foto cambia la dirección y el
caché se entera solo.

### Los datos de la agrupación

Tabla `organizacion` de una sola fila, con su `GET` y su `PUT`, y la pantalla `/admin/organizacion`.
El catálogo, el checkout y la página del pedido leen de ahí.

La siembra lleva **solo lo que se puede comprobar** en su Facebook y sus afiches, y la cuenta
bancaria va vacía. Mientras lo esté, la página del pedido muestra datos de ejemplo y avisa que esa
cuenta no recibe transferencias. El aviso desaparece solo cuando la carguen: nadie tiene que
acordarse de quitarlo.

La cuenta se guarda entera o vacía. Con banco y sin número, nadie podría transferir y el aviso se
habría ido igual, mostrando datos incompletos como si fueran buenos.

## Error encontrado

Estaba probando el catálogo con la barra que dice «1 objeto elegido» cuando reservé, desde otra
sesión, el mismo estante que tenía seleccionado. El checkout avisó correctamente que ya no estaba
disponible. Pero al volver:

> ¿Por qué el catálogo sigue diciendo que tengo uno elegido?

Porque la selección vive en la sesión y **nadie la limpiaba**. El objeto ya no existía para la venta,
y la barra seguía contándolo y ofreciendo reservarlo. Peor: el botón de reservar seguía ahí con total
$0, y apretarlo habría mandado un pedido vacío al web service.

Lo arreglé en dos partes. El catálogo ahora cuenta solo los que siguen disponibles, y el checkout
saca de la sesión los que se perdieron. La limpieza va **en el checkout y no en el catálogo** a
propósito: el checkout es la única pantalla que avisa que perdiste algo, y si limpiara antes el
objeto desaparecería en silencio sin que nadie supiera por qué.

Lo que queda: **un dato guardado en la sesión sigue siendo verdad para la aplicación aunque haya
dejado de serlo en la base.** No basta con leer bien; hay que decidir quién lo corrige y en qué
pantalla, porque ahí es donde se le puede explicar a la persona.

## Pendientes y decisiones

- **El campo «de dónde salió» se fue del formulario y su dato se borró.** Era la línea que le daba
  historia a cada objeto, pero quien carga uno no va a escribirla, y dejar un campo que no se puede
  mantener es peor que no tenerlo. La columna sigue en la base, vacía, por si vuelve.
- **La medida son tres números en centímetros y solo aparece en muebles.** En un libro o un juguete
  no significa nada; ahí esa columna dice «Encomienda» o «2 a 5 años», así que si los tres campos
  vienen vacíos se conserva lo que hubiera en vez de borrarlo.
- Los vendidos del catálogo se limitan a los últimos ocho y la nota dice de cuántos son en total. El
  texto ya prometía «los últimos» y el código mostraba todos: con cien ventas esa sección sería una
  pared.

## Cierre

El sistema dejó de tener una parte que solo yo puedo operar. Lo que hasta ayer requería abrir un
archivo Java, cambiar un arreglo de textos y recompilar, hoy es un formulario con una vista previa al
lado. Lo que queda para que esto sea entregable de verdad ya no es funcionalidad: es que alguien
distinto de mí pueda levantarlo y entender cómo se usa.

## Estado del Examen

| Criterio | Estado |
|---|---|
| MVP y valor de negocio (25) | ✅ la agrupación administra su catálogo y sus datos |
| Ejecución integral del proceso en Flowable (15) | ✅ |
| Integración de web services y base de datos (15) | ✅ ocho tablas y veintidós endpoints |
| Interfaces de usuario y experiencia (15) | ✅ nueve pantallas con identidad propia |
| Uso de IA y tecnologías complementarias (5) | ◐ el ADR-010 sigue sin aparecer en el README |
| Documentación, repositorio y entregables (10) | ◐ falta el manual de instalación y el de uso |
| Video demo para la emprendedora (8) | ☐ |
| Sustentación técnica para el profesor (7) | ☐ |

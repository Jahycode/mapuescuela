# Acta 09 — Los tres endpoints que faltaban para poder empezar la web

- **Fecha:** lunes 24 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Hoy cerré los tres endpoints que la aplicación web no puede esquivar: el catálogo, el pedido por
identificador y el que vincula un pedido con su instancia del proceso. Con esos, lo siguiente ya es la
web.

Lo hice de una forma distinta a propósito. Pedí un ejemplo resuelto del primero y **los otros dos los
escribí yo**, para comprobar si podía producir la solución y no solo entenderla cuando me la explican.
Me equivoqué varias veces y esa es la parte que más vale registrar, así que va con detalle.

## El catálogo, que fue el ejemplo

`GET /productos` trae lo que la primera pantalla necesita mostrar. Es el único de los tres con
estructura nueva: una clase para el producto, que no existía, y un recurso aparte con su propia ruta
base, porque `/productos` no cuelga de `/pedidos`.

Lo que me llamó la atención es que **no hay que registrar la clase nueva en ninguna parte**. El
arranque le dice a la librería que recorra el paquete y ahí la encuentra sola. Es lo mismo que había
descubierto en la Entrega 1 con las anotaciones, pero esta vez lo vi funcionando con una clase que
acababa de crear.

Quedó una imprecisión que anoto en vez de disimular: el método que lista productos vive en el DAO de
pedidos, que ya tenía otros dos métodos de productos. Lo correcto sería un DAO propio. Lo dejo así
mientras la lógica de productos sea esta, y se separa cuando crezca.

## El pedido por identificador, primero de los míos

Este es corto y aun así me equivoqué en tres cosas.

La primera fue no ponerle ruta al método. Le puse el verbo y el tipo de respuesta, pero no la ruta, así
que quedaba registrado en la misma dirección que el método que lista todos los pedidos. Dos métodos, el
mismo verbo, la misma dirección: la librería no habría sabido cuál llamar.

La segunda fue devolver el identificador del pedido en lugar del pedido. Visto de fuera es evidente:
quien llama escribió ese número en la dirección, ya lo sabe. Devolvérselo no le entrega nada. La página
de seguimiento necesita el nombre, el monto, el desenlace — todo lo que estaba en el objeto que tenía
en la mano.

Y la tercera fue el nombre del método, que describía el parámetro y no la acción.

Al corregir la ruta me pasé para el otro lado y le puse un verbo dentro de la dirección, algo como
"buscar-pedido". Funcionaba, pero sobraba: **la dirección nombra un recurso y el verbo del protocolo
dice qué hacerle**. Pedir el pedido 7 ya se expresa entero con el verbo de lectura más la dirección del
pedido; agregarle "buscar" es repetirlo.

Me sirvió compararlo con uno que sí tengo con verbo en la dirección, el de descontar stock. Ese está
bien porque descontar no corresponde a ningún sustantivo: no existe "el descuento" como cosa. Cuando no
hay sustantivo razonable, el verbo en la dirección es la salida práctica. Pero cuando el recurso existe
—y el pedido existe— el verbo es ruido.

## El de la instancia, y el error que más me enseñó

Este vincula un pedido con la instancia del proceso que le corresponde. Hace falta porque el vínculo
nace en una sola dirección: al arrancar la instancia le paso el identificador del pedido, así que la
instancia sabe de qué pedido es, pero el pedido no sabe nada de la instancia. La página de seguimiento
necesita justamente esa dirección inversa.

Lo escribí entero y estaba equivocado de raíz: **construí la consulta inversa**. Mi método recibía un
identificador de instancia y respondía si existía algún pedido con él. Iba de la instancia al pedido,
cuando lo que hacía falta era del pedido a la instancia.

La pregunta que lo dejó claro fue una sola: *después de que mi endpoint responde correctamente, ¿qué
cambió en la base?* Nada. Mi método hacía una consulta, no una modificación. El trabajo era escribir un
valor en una columna y yo estaba mirando si alguien ya lo tenía.

Es un error que no se ve leyendo el código, porque cada línea por separado estaba bien escrita. Se ve
preguntando para qué servía.

### De dónde llega cada dato

El otro error de fondo fue pedir el identificador de la instancia desde la dirección, cuando viene en el
cuerpo de la petición. Son dos fuentes distintas y cada una se recibe de una forma: lo que va en la
dirección se pide con una anotación, y lo que viene en el cuerpo llega como un parámetro suelto que la
librería rellena.

Ya lo tenía hecho bien en dos endpoints anteriores. Lo que no tenía era el concepto separado del
ejemplo, así que al escribir uno nuevo desde cero mezclé las dos formas.

### Hasta dónde vive una variable

Después declaré el objeto de acceso a datos dentro del bloque que abre la conexión y lo usé fuera. No
compila, y tiene sentido: **una variable declarada dentro de un bloque solo existe dentro de ese
bloque**. Y aunque sobreviviera, estaría agarrada a una conexión que ya se cerró.

Ese error lo encontró el compilador de inmediato. Aprendí también que no necesito compilar a mano para
verlo: el editor tiene un panel de problemas que va marcando los errores mientras escribo, y yo llevaba
días corriendo la compilación completa para enterarme de cosas que ya estaban ahí en rojo.

### Un pedido que no existe no es una falla mía

Puse un error de servidor cuando el pedido no aparecía, razonando que si la web acababa de crearlo y no
estaba, algo se había roto. Pero las dos familias de códigos significan cosas distintas: una dice que
quien llama pidió algo que no corresponde, y la otra que yo me caí. Ahí no se cayó nada — el servicio
funcionó perfecto y la respuesta correcta es que eso que piden no está.

Y tiene una consecuencia práctica: un error de servidor le dice al que llama que reintente más tarde. Con
un pedido inexistente eso no se va a arreglar nunca, así que lo estaría mandando a reintentar para
siempre. Que es exactamente lo que hace mi worker cuando recibe un error recuperable.

## Elegir el verbo con un argumento

Este endpoint me obligó a decidir entre dos verbos y a tener la razón lista.

Mi primer impulso fue el de crear, porque pensé que estaba creando algo al asignar la instancia. Pero la
instancia ya existía: la creó el motor en el paso anterior. Mi endpoint solo anota una referencia a algo
que ya está, y en mi base no nace ninguna fila.

Lo que sí es cierto es que escribir el mismo texto dos veces en la misma columna deja el mismo
resultado. Es una operación idempotente por naturaleza, y hay un verbo que significa exactamente eso.

Lo que entendí es que **el verbo no vuelve idempotente a nada**: la propiedad es de lo que hace el
código, y el verbo solo la declara. Pero declararla no es adorno. Si la web llama y la respuesta se
corta por tiempo de espera sin saber si alcanzó a guardarse, con ese verbo puede reintentar sin dudar
porque el estándar lo garantiza; con el otro tendría que ir a leer mi documentación.

Lo probé llamándolo dos veces y quedó igual, así que el razonamiento no era solo teoría.

Y de paso me fijé en que mi endpoint del desenlace, de ayer, tiene la misma forma —rellena columnas de
algo que ya existe y es idempotente— y usa el otro verbo. Según este mismo argumento debería cambiar. No
lo cambié porque funciona y está probado, pero lo anoto: es la primera vez que puedo evaluar una
decisión que tomé antes y ver que fue floja.

## Estado de la Entrega 2

| Criterio | Estado |
|---|---|
| Modelo BPMN ejecutable | ✅ |
| Uso de tareas BPMN y external workers | ✅ |
| Proceso ejecutándose en Flowable | ✅ las seis salidas recorridas |
| Funcionamiento y prueba de web services | ✅ |
| Repositorio GitHub | ✅ |
| Gestión y planificación | ✅ |
| Web services que cubren el proceso | ✅ ocho endpoints; los que faltan esperan a la pantalla que los use |
| Interfaces de usuario | ☐ **lo siguiente** |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |

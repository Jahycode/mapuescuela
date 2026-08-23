# Acta 08 — Los endpoints que el worker necesitaba

- **Fecha:** domingo 23 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## La conexión que compartían todas las peticiones

Antes de escribir endpoints nuevos arreglé algo que tenía anotado: el web service guardaba una sola
conexión a la base y todas las peticiones la usaban.

Yo pensaba que una conexión era como una dirección guardada, un dato inerte. No lo es: es una
conversación en curso, con estado propio — la transacción abierta, la última sentencia, los cursores
que uno está recorriendo. Y el servidor atiende cada petición en un hilo distinto, así que dos
peticiones que llegan juntas se ejecutan de verdad al mismo tiempo sobre esa misma conversación.

Lo que pasaba, o mejor dicho lo que iba a pasar, es que al ejecutar una consulta nueva sobre la misma
conexión el cursor anterior se cierra. Una petición que estaba leyendo resultados los perdería sin
haber hecho nada mal. Y con transacciones es peor: una podría confirmar el trabajo a medio hacer de la
otra.

Nunca me falló porque nunca hubo dos cosas al mismo tiempo — probé siempre a mano, una petición por
vez. Es un fallo de carrera, y esos aparecen justo cuando hay público.

El arreglo fue una clase nueva que entrega conexiones, y cada método abre la suya y la cierra al
terminar. Lo que me quedó dando vueltas es cuál **no** fue la solución: no puse turnos ni candados
para que los hilos se coordinaran al usar la conexión compartida, **dejé de compartirla**. Es la misma
forma de pensar del descuento atómico de stock, donde el arreglo tampoco fue consultar más rápido sino
hacer que consultar y actuar fueran una sola operación. Las dos veces se eliminó la carrera en vez de
administrarla.

Y hay un detalle que ahora sostiene todo: el parámetro que impide que H2 destruya la base en memoria
cuando se cierra la última conexión. Antes era casi decorativo, porque siempre había una conexión
abierta. Ahora es lo único que mantiene la base viva entre peticiones.

## El desenlace: columnas, no tabla

El primer endpoint registra cómo terminó un pedido, y lo llaman tres de los cinco topics con distinto
valor. Uno solo, no tres, porque es la misma operación cambiando un texto.

Empecé pensando en una tabla y al preguntarme para qué servía me di cuenta de que no. Cada instancia
del proceso termina exactamente una vez, así que la relación es uno a uno, y una tabla en ese caso solo
agrega un `JOIN` sin dar nada. Quedaron tres columnas en la tabla de pedidos.

Eso me hizo revisar una decisión anterior, la de no guardar el estado del pedido porque el motor es la
fuente de la verdad. Pensé que esto la rompía, y no: el estado es dónde va el pedido ahora y cambia
todo el tiempo, el desenlace es cómo terminó y no cambia nunca. El estado es una película, el desenlace
es la última foto. Duplicar la película sería el error; guardar la foto no. Y hay una razón práctica:
si Mapuescuela quiere saber cuánto vendió el mes pasado, ese dato tiene que estar en mi base, no en la
del motor de procesos.

De paso salió un beneficio que no buscaba. Al ser columnas, el endpoint hace un `UPDATE` en vez de un
`INSERT`, y eso lo vuelve inofensivo si se llama dos veces — que es exactamente lo que pasa cuando el
worker reintenta.

## El CHECK que rompí sin darme cuenta

Puse una restricción en la columna del desenlace para que solo aceptara los seis valores del modelo, y
el endpoint empezó a devolver error 500 en cuanto intentaba escribir de verdad.

Me costó encontrarlo y la forma en que lo acoté me sirvió: con un valor inválido respondía bien, con un
pedido inexistente respondía bien, y solo fallaba cuando de verdad tenía que modificar una fila. O sea
que el problema no estaba en leer el cuerpo ni en armar la consulta, sino en el momento de escribir.

El error decía que la base estaba cerrada. Resulta que para comparar textos H2 necesita preguntarle
algo a la sesión que creó la restricción, y esa sesión **era la que yo acababa de cerrar esa misma
mañana** al arreglar la conexión compartida. Antes vivía para siempre por accidente.

Saqué la restricción y la validación se quedó solo en Java, donde además da mejor mensaje. Lo dejo
anotado porque la restricción en sí está bien escrita: contra una base de verdad funcionaría. Es una
limitación de H2 en memoria, no un error de diseño.

Lo que más me sirvió de este episodio es que un arreglo correcto destapó algo que estaba escondido
detrás de un accidente.

## Las notificaciones: acá sí una tabla

El segundo endpoint registra los avisos al cliente, y esta vez la tabla se justifica sola: un pedido
puede tener varios avisos, así que la relación es uno a muchos.

La decisión interesante fue cuánto manda el worker. Podría mandar el tipo, el destinatario y el texto,
y decidí que mande **solo el tipo**. Dos razones. La primera es que componer el texto de un aviso es
lógica de negocio y esa vive en el web service; si la armara el worker tendría reglas escritas en
Python y en Java. La segunda es más concreta: el web service ya sabe el correo del cliente, está en su
propia tabla. Si el worker lo mandara, el mismo dato viviría en dos lugares, y hay un caso donde eso se
rompe — si el cliente corrige su correo, una instancia vieja del proceso seguiría cargando el antiguo y
avisaría a la dirección equivocada.

El endpoint recibe el tipo, busca el pedido, saca el correo de ahí y arma el texto desde una tabla de
mensajes. Esa tabla hace dos cosas a la vez: sus claves son los tipos válidos y sus valores el texto.

También me fijé en que este devuelve un código distinto al del desenlace. El del desenlace actualiza
algo que ya existía, así que responde que está bien; este crea una fila nueva, así que responde que
creó un recurso. Mismo proyecto, dos códigos, por una razón y no por capricho.

## La duplicación que sí había que cerrar

Al conectar el handler que avisa por falta de stock quedaron dos llamadas seguidas en la misma función,
y no son iguales: escribir el desenlace es inofensivo si se repite, pero insertar una notificación
crearía una fila duplicada. Con un reintento del worker eso iba a pasar.

Lo cerré con una sola sentencia que inserta únicamente si no existe ya una notificación de ese tipo para
ese pedido, y el número de filas afectadas dice si la creó o si ya estaba. **Es la tercera vez en el
proyecto que uso el mismo recurso**: el descuento de stock, el registro del desenlace y ahora esto. Una
sola ida a la base, y el resultado de la operación es la respuesta. En vez de consultar y después
decidir, hacer la operación de forma que no se pueda colar nada en el medio.

Lo probé llamando tres veces igual: crea la primera y las otras dos responden que ya existía, con una
sola fila en la tabla.

## Dos huecos que cerré de paso

Al crear la tabla de notificaciones puse una clave foránea al pedido, y ahí caí en que **el bug del
sábado existía justamente porque faltaba una**. La columna del producto en la tabla de pedidos no la
tenía, y por eso un pedido podía nacer apuntando a un producto que no existe. Se la agregué: ahora eso
es imposible en la base y no depende de que el código se acuerde de revisar.

El otro salió de una pregunta que me hice mirando la tabla nueva: por qué el destinatario admitía
nulos. La respuesta era que la fuente los admitía, o sea que el correo del cliente podía faltar. Y eso
no tiene sentido: en Mapuescuela el correo es lo único con lo que se le puede hablar al cliente. Agregué
la validación al crear el pedido y las dos columnas ya no admiten nulos.

## Los cinco topics haciendo trabajo real

Al terminar quedaron los cinco atendidos de verdad. Ya no hay ningún handler que imprima una marca de
pendiente y cierre el trabajo sin hacer nada.

Probé el rechazo completo con el worker corriendo: registró el desenlace con el motivo que escribí al
rechazar, el proceso avanzó, el segundo handler anotó la notificación, y la instancia terminó. Todo en
seis segundos y sin intervención.

## Un error que vale registrar

Tuve el endpoint devolviendo 404 sin entender por qué, y era que la ruta estaba en singular en un
archivo y en plural en otro. Dos archivos, dos lenguajes, y lo único que los une es que una cadena de
texto coincida exactamente. No hay compilador que revise eso.

Es justo la diferencia que estudié la semana pasada entre los dos estilos de servicios web: en el que
tiene un contrato obligatorio, ambos lados están forzados a hablar igual. Acá la coincidencia depende de
que yo escriba bien.

## Estado de la Entrega 2

| Criterio | Estado |
|---|---|
| Modelo BPMN ejecutable | ✅ |
| Uso de tareas BPMN y external workers | ✅ |
| Proceso ejecutándose en Flowable | ✅ las seis salidas recorridas |
| Funcionamiento y prueba de web services | ✅ los cinco topics integrados |
| Repositorio GitHub | ✅ |
| Gestión y planificación | ✅ |
| Web services que cubren el proceso | ◐ el lado del worker completo; falta el de la web |
| Interfaces de usuario | ☐ |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |

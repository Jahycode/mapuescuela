# Acta 07 — El worker atendiendo los cinco topics

- **Fecha:** sábado 22 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## Los cuatro topics que faltaban

El jueves el worker atendía uno solo, y había quedado un pedido estacionado esperando la
notificación de falta de stock. Hoy le agregué los otros cuatro.

La forma obvia era una cadena de condiciones: si el topic es este, llama a esta función. Funciona,
pero cada topic nuevo obliga a tocar el bucle. En Python hay algo mejor, y es lo que se siente raro
viniendo de Java: una función es un valor, así que se puede guardar como valor de un diccionario. El
bucle recorre el diccionario y deja de saber qué topics existen. Agregar uno pasa a ser agregar una
línea.

Es el mismo patrón que ya había visto en el web service sin darme cuenta: nunca instancio la clase de
los endpoints, solo digo en qué paquete buscar y la librería se encarga.

Los cuatro handlers nuevos son provisorios. Dejan constancia en pantalla y cierran el trabajo, pero
no llaman a nada, porque los endpoints que necesitarían todavía no existen en el web service. Los
marqué con `[pendiente]` en el log a propósito: esa marca es lo que distingue que el worker hizo su
pega de que el worker fingió, y no la voy a sacar hasta que el handler llame a algo de verdad.

Escribiéndolos me quedó clara una diferencia que no había notado. De los cinco topics, **solo el de
inventario devuelve una variable al proceso**. Los otros cuatro caen directo en el paso siguiente o
en un final, sin gateway en el medio. Eso los hace estructuralmente distintos: el de inventario le
informa algo al proceso, y los otros cuatro solo hacen algo y el proceso sigue igual.

## La prueba: se comió ocho trabajos

Había seis esperando, de tres topics distintos. Arranqué el worker y los procesó en tres vueltas.

Pero fueron ocho, no seis. Dos aparecieron durante la corrida: al completar los de rechazo, el
proceso avanzó al paso siguiente y publicó las notificaciones al cliente, y el worker se las encontró
en la pasada siguiente. O sea que no está vaciando una lista fija, está empujando procesos que le
generan más trabajo. Eso es lo que lo hace un worker y no un script de limpieza.

Ahí también comprobé la bandera que le agregué al bucle. Con cinco topics son cinco preguntas por
vuelta, y si durmiera cada vez que una viene vacía dormiría de más aunque haya trabajo pendiente en
el resto. Con la bandera duerme solo cuando las cinco vinieron vacías, y en esa corrida no durmió
ninguna vez.

## Las seis salidas del proceso

Con la cola vacía revisé el historial completo y me encontré con que faltaban dos de las seis
salidas del modelo: las dos de despacho. No era casualidad. Todos mis pedidos de prueba se habían
creado con modalidad de retiro, así que el gateway de modalidad nunca había tomado la otra rama.

Armé dos pedidos con modalidad de despacho y los llevé por el camino largo, que es el que más
recorre: tres gateways, cinco tareas humanas y el worker en el medio. Uno lo mandé por courier y el
otro por voluntario.

| Salida del modelo | Ejecuciones |
|---|---:|
| Pedido cancelado por vencimiento | 7 |
| Pedido cancelado (pago rechazado) | 3 |
| Pedido retirado | 3 |
| Cancelado por falta de stock | 2 |
| Despachado por courier | 1 |
| Despachado por voluntario | 1 |

Seis de seis, con ejecuciones reales. Es la evidencia que más me interesaba conseguir, porque el
criterio de ejecución pide de inicio a fin incluyendo decisiones, tareas humanas y automatizadas, y
ahora no es algo que yo afirme sino un recuento que se puede revisar.

Me dejo anotada una advertencia. Ese historial vive en la base del contenedor de Flowable, y ese
contenedor no tiene volumen montado: sobrevive a detenerlo y arrancarlo, pero si alguna vez lo
elimino se pierde completo. Antes de usarlo como evidencia hay que capturarlo.

## El orden de la carpeta

Con todo funcionando, la carpeta del worker tenía nueve archivos y no todos servían.

Primero saqué las tres piezas que no son lógica de negocio: las constantes a un archivo de
configuración, las llamadas al motor a un cliente y las llamadas al web service a otro. Los dos
clientes separados a propósito, porque son dos integraciones que van a cambiar por motivos
distintos: si mañana actualizo el motor toco un archivo, y si agrego un endpoint toco el otro.

El resultado que más me gustó es el handler del inventario. Pasó de seis líneas con la petición HTTP
adentro a cuatro, y ninguna menciona una dirección. Antes hablaba HTTP; ahora dice "descuéntame el
stock de este pedido" y se desentiende de cómo se pide eso.

Después borré los cuatro scripts que había escrito para subir la escalera del worker. Ya no los
usaba nada y cada uno tenía su propia copia de la dirección y las credenciales: cinco archivos con
credenciales escritas cuando corresponde uno solo. Al de mirar la cola lo salvé, pero reescrito para
que use los módulos, y bajó de veinte líneas a seis haciendo más que antes.

Un detalle chico me confirmó que el refactor había quedado bien: al terminar, el import de la
librería HTTP en ese archivo quedó sin uso. Se volvió innecesario justamente porque el archivo dejó
de hablar HTTP.

## Los dos errores del web service

En la revisión del lunes había anotado dos errores en el web service, en código que ya daba por
terminado. Hoy los arreglé.

El primero es que el descuento de stock respondía lo mismo cuando el producto no existía y cuando no
había unidades. En los dos casos decía que no alcanzó, así que un pedido con datos malos se iba por la
rama de cancelación como si fuera una decisión de negocio, sin dejar rastro en ningún log. Intenté
resolverlo metiendo la comprobación dentro del mismo método y no funciona: **un booleano no puede
decir tres cosas**, y acá los resultados posibles son tres. Terminó siendo una consulta aparte que
solo verifica si el producto existe, y el recurso devolviendo el código de recurso no encontrado.
Quien decide qué significa cada caso es el recurso, que es el que sabe de códigos HTTP.

El segundo era la cantidad. Un pedido con cantidad cero, o sin ese campo, informaba que el descuento
había alcanzado sin descontar nada. Y probándolo encontré algo peor de lo que tenía anotado: **una
cantidad negativa subía el stock**. Restar menos tres es sumar tres, y la condición del `WHERE`
también se cumplía, así que un pedido de menos tres unidades inventaba tres unidades. Lo comprobé
drenando el producto después: había pasado de cuatro a siete.

Lo arreglé en dos capas: una validación al crear el pedido, que rechaza y dice qué llegó, y una
restricción en la propia tabla, para que la garantía no dependa de que un endpoint futuro se acuerde
de validar. Drenar un producto de cinco unidades ahora da exactamente cinco descuentos y después
falla, que es la aritmética que uno esperaría y que antes no se cumplía.

## El worker aguantando los fallos

El arreglo anterior tuvo una consecuencia inmediata: ahora que el endpoint puede responder que no
encuentra el pedido, el worker se caía, porque no tenía manejo de errores. Y no es un caso
hipotético: cada vez que reinicio el web service su base en memoria nace vacía, y las instancias que
siguen vivas en el motor apuntan a pedidos que ya no existen.

Lo probé a propósito con el web service apagado y el worker murió con un error de conexión. Después
envolví el procesamiento de cada trabajo, de modo que un fallo se anote y el bucle siga con el
siguiente. Un detalle que casi me cuesta caro: hay que capturar solo las excepciones normales, porque
la interrupción de teclado no es una de ellas. Si uno captura todo, construye un worker que no se
puede apagar con `Ctrl+C`.

Con eso deja de morirse, pero el motor no se enteraba de nada: para él el trabajo seguía reservado por
alguien que no había vuelto. Así que agregué el aviso de fallo, que le descuenta un reintento al
trabajo y guarda el motivo. Cuando los tres se agotan, el trabajo cae en la bandeja de trabajos
muertos, donde queda visible y deja de reintentarse. Lo probé y funcionó: el mensaje que quedó
guardado dice exactamente qué pedido no se encontró.

Probándolo apareció un problema que no había previsto. Ese aviso devuelve el trabajo a la cola de
inmediato, así que el worker lo tomaba de nuevo tres segundos después y los tres reintentos se
consumían en menos de veinte segundos. Un reinicio del web service demora más que eso, o sea que el
worker estaba convirtiendo fallos pasajeros en permanentes. Se resuelve pidiéndole al motor que espere
antes de volver a ofrecer el trabajo. Con eso los intentos quedaron separados por más de un minuto, y
un problema que se arregla solo alcanza a arreglarse.

Dejo anotada una imprecisión: configuré treinta segundos de espera y el motor esperó más de ochenta.
No averigüé por qué. Mi sospecha es que revisa los trabajos vencidos en ciclos propios y eso agrega
latencia, pero no lo comprobé. Para el efecto que buscaba da lo mismo, así que lo dejo pendiente.

Lo último fue el apagado. Si detenía el worker mientras tenía un trabajo en mano, ese trabajo quedaba
reservado a su nombre hasta que venciera la reserva, o sea varios minutos en los que nadie más podía
tomarlo. Agregué que al detenerse lo devuelva a la cola, con una operación distinta a la del fallo:
esta no descuenta reintentos ni guarda ningún mensaje, porque apagar el worker no es un error. El
trabajo queda como si nunca lo hubieran tomado.

Para probarlo tuve que meter una pausa a propósito en un handler, porque procesar un trabajo toma
milisegundos y no hay forma de alcanzar a interrumpirlo. Me sirve saberlo: para grabar el video voy a
necesitar el mismo truco si quiero mostrar qué pasa cuando el worker se cae a mitad de camino.

## Estado de la Entrega 2

| Criterio | Estado |
|---|---|
| Modelo BPMN ejecutable | ✅ |
| Uso de tareas BPMN y external workers | ✅ |
| Proceso ejecutándose en Flowable | ✅ las seis salidas recorridas |
| Repositorio GitHub | ✅ |
| Gestión y planificación | ✅ |
| Funcionamiento y prueba de web services | ✅ integración automática de los cinco topics |
| Web services que cubren el proceso | ◐ una de cinco operaciones |
| Interfaces de usuario | ☐ |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |

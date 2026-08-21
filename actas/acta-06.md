# Acta 06 — Arranque de la Entrega 2 y el external worker en Python

- **Fecha:** del lunes 17 al jueves 20 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Esta acta cubre cuatro días. Dos los dediqué a estudiar la unidad del curso, y aunque de ahí no salió
código, sí cambiaron decisiones del proyecto.

## Leer la rúbrica antes de programar

Al cerrar la primera entrega, lo primero que hice fue leer la rúbrica de la segunda. Encontré algo que
no esperaba: no evalúa solo cosas nuevas, sino que vuelve a revisar casi todo lo de la Entrega 1 con
criterios más exigentes.

Ahí estaba también la frase que ordenó el trabajo. El criterio de pruebas de web services pide
evidencia de funcionamiento **e integración con el proceso**. Mi integración existía, pero la hacía yo:
el motor se quedaba esperando en cada tarea automática y yo copiaba el identificador del trabajo para
atenderlo. Eso no es integración, es reemplazo manual.

Por eso el worker quedó primero, antes que la aplicación web, aunque la web pese más puntos. Sin
worker no hay nada que mostrar.

## La revisión de lo que ya tenía

Antes de escribir código nuevo revisé lo construido: el modelo, el web service y la API del motor.
Preferí gastar el tiempo ahí que descubrir los problemas más adelante.

Encontré dos errores en el web service, en código que ya daba por terminado. El primero es que el
descuento de stock responde lo mismo cuando el producto no existe y cuando no hay unidades: en los dos
casos dice que no alcanzó, así que el pedido se iría por la rama de cancelación como si fuera una
decisión de negocio. El segundo es que un pedido con cantidad cero pasa como correcto, porque restar
cero unidades igual modifica la fila.

Los dos son la misma falla de fondo: el sistema contesta algo razonable y sigue, cuando debería
detenerse.

También vi que el modelo lee dos variables que nadie declara, el identificador del pedido y el plazo
de pago. Hoy funcionan porque el archivo de pruebas las inyecta al iniciar la instancia, o sea que la
integración completa depende de una línea que vive en un archivo de pruebas.

Y corregí varias suposiciones mías sobre la API de external workers. La que más me sirvió: el trabajo
no declara a qué topic pertenece, así que la cola no se puede filtrar por topic. Hay que pedirlo al
reservar.

## Dos días de estudio

El martes y el miércoles los dediqué a la unidad de servicios web SOAP y REST. Lo anoto porque se
cruza directo con lo que estoy construyendo.

Lo que más me ordenó fue el tema del contrato. SOAP tiene un archivo obligatorio que describe el
servicio completo, y sobre él hay herramientas que generan el código para invocarlo. En REST no existe
ese equivalente, y por eso mis archivos de peticiones los escribí a mano uno por uno. Ahí ubiqué mi
propio web service, que hasta entonces había elegido sin tener claro qué estaba dejando afuera.

De paso entendí la idempotencia, que explica algo que me había pasado antes sin darme cuenta: cuando
completé dos veces la misma tarea, la segunda vez el motor dijo que el recurso no existía. No era una
falla del motor, es que esa operación no se puede repetir.

## El entorno de Python

El lunes por la noche preparé la carpeta del worker: un entorno virtual y un archivo con las dos
dependencias que necesito. Es la misma idea del envoltorio de Gradle que ya uso en el web service —el
proyecto se trae sus propias herramientas en vez de depender de lo que haya en la máquina— y por eso al
repositorio sube la lista de dependencias y no la carpeta con ellas instaladas.

## El worker, por escalones

Decidí no escribir el worker completo de una vez, sino subir cinco escalones con un resultado
verificable en cada uno. La razón es que el worker toca tres sistemas a la vez, y si algo falla con
todo escrito de golpe no hay forma de saber cuál de los tres tiene el problema.

| Escalón | Qué construí | Qué verifica |
|---|---|---|
| 1 | Consultar la cola de trabajos | Que Python llega al motor y la credencial funciona |
| 2 | Reservar un trabajo | Que el mecanismo de reserva funciona |
| 3 | Informar que el trabajo terminó | El ciclo cerrado |
| 4 | Llamar al web service en el medio | La integración entre los dos servicios |
| 5 | Envolverlo en un ciclo permanente | El worker propiamente tal |

El primero es de solo lectura a propósito. Si algo falla ahí es la credencial o la red, y no dejé
ningún trabajo reservado mientras averiguaba.

Subir de a uno resultó mejor de lo que esperaba, porque cada escalón me enseñó algo que no tenía en la
cabeza al empezar. En el segundo, por ejemplo, entendí para qué sirve la duración de la reserva, y lo
entendí de la peor manera: me demoré escribiendo el escalón siguiente, la reserva venció y el
identificador que tenía anotado dejó de servirme. No fue un error, fue el mecanismo funcionando.

El quinto es el que cambió la naturaleza del programa. Los anteriores eran mandados: se ejecutan,
hacen una cosa y terminan. El worker se queda corriendo y pregunta cada tanto si hay algo para él. Eso
obligó a convertir las líneas sueltas en funciones y a manejar el caso de la cola vacía, que es lo que
pasa la mayor parte del tiempo. Ahí también me topé con un límite del motor: la reserva acepta un solo
topic por llamada, así que atender los cinco son cinco preguntas por vuelta.

De los errores del camino me quedaron dos lecciones. Una fue dejar un marcador sin reemplazar dentro
de una dirección: el motor dijo que el recurso no existía, yo supuse que la instancia había terminado,
y en realidad el mensaje de error traía la dirección exacta que se había enviado, con la respuesta a la
vista. La otra fue confiar en el autocompletado, que me generó dos funciones que no había pedido y una
de ellas habría fallado. Adivina por la forma de lo que uno escribe, no sabe qué devuelve el servicio;
si no puedo explicar qué hace una línea, no debería estar en el archivo.

## Las dos demostraciones

Con el worker corriendo y sin tocar nada, probé los dos caminos que dependen del resultado del
descuento.

El primero con un producto que tenía unidades. Creé el pedido, inicié la instancia, cerré la tarea del
comprobante y aprobé el pago. En cinco segundos el worker había tomado el trabajo, consultado al web
service y avisado al motor, y la instancia estaba en la tarea de preparar el pedido. Los primeros dos
segundos el trabajo estuvo publicado y sin dueño, y eso me gustó: no es un retardo del motor ni de la
red, es la espera que yo mismo definí al escribir el ciclo.

El segundo caso con el producto que ya había quedado sin unidades. El web service respondió que no
alcanzaba, el worker devolvió ese resultado y el motor tomó el flujo por defecto del gateway, así que
el pedido se fue por la rama de cancelación por falta de stock. Ese es el control que agregué al modelo
semanas atrás para que no se vendiera dos veces el mismo mueble, y es la primera vez que lo veo
funcionar completo, con datos reales y sin que yo intervenga.

De ese segundo caso hay un detalle que vale más que la demostración misma. El proceso no terminó:
quedó un trabajo de notificación esperando, porque mi worker atiende un solo topic y nadie escucha los
otros cuatro. No apareció ningún error ni se cayó nada. El trabajo está ahí, y cuando escriba ese
handler el pedido va a terminar como si nada hubiera pasado.

Eso es lo que significa en la práctica que el motor sea la fuente de la verdad y que los workers sean
externos. Hasta hoy era un argumento que podía explicar, pero no mostrar.

## Estado de la Entrega 2

| Criterio | Estado |
|---|---|
| Modelo BPMN ejecutable | ✅ |
| Uso de tareas BPMN y external workers | ✅ |
| Proceso ejecutándose en Flowable | ✅ |
| Repositorio GitHub | ✅ |
| Gestión y planificación | ✅ |
| Web services que cubren el proceso | ◐ una de cinco operaciones |
| Funcionamiento y prueba de web services | ◐ integración automática lograda hoy |
| Interfaces de usuario | ☐ |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |

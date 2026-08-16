# Acta 05 — El web service en Java funcionando

- **Fecha:** sábado 16 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## La clase que levanta el servidor

Escribí la última de las cuatro clases del servicio, la que arranca el servidor y publica los
endpoints. Son diez líneas y hacen tres cosas: definir en qué dirección escuchar, decirle a la
librería dónde buscar mis recursos, y levantar el servidor embebido en el puerto 9090.

Lo que más me llamó la atención es que **la clase con los endpoints no aparece por ninguna parte
ahí**. Nunca la instancio ni la registro. Solo le indico el paquete donde buscar, y la librería
escanea, encuentra las clases anotadas y las registra sola. Ahí entendí para qué sirven realmente
las anotaciones: no son decoración, son marcas para que el framework te encuentre. Si mañana agrego
otro recurso, funciona sin tocar esta clase.

También decidí usar el servidor embebido en vez de instalar uno aparte. El ejemplo del profesor
ofrece tres formas de desplegar, y elegí la que no depende de que haya un servidor instalado en la
máquina de destino: el servicio queda como un programa ejecutable normal que solo necesita Java.

## La prueba de punta a punta

Levanté el servicio y probé los tres endpoints desde un archivo de peticiones, igual que hice con el
motor. Cinco pruebas, todas correctas:

1. Crear un pedido devuelve **201** con el pedido y el id que le asignó la base.
2. Listarlos ya no devuelve la lista vacía.
3. Descontar stock devuelve que sí alcanzó.
4. **Descontar otra vez el mismo producto devuelve que no alcanzó** — el sofá de prueba tiene una
   sola unidad, así que la segunda vez la consulta no encuentra ninguna fila que cumpla la condición
   y el descuento no ocurre.
5. Pedir el descuento de un pedido inexistente devuelve **404** con el mensaje de error.

La cuarta es la que más me interesaba: es la demostración de que el control de sobreventa funciona
de verdad, y es exactamente el caso que modelé en BPMN cuando agregué la rama de quiebre de stock.
El proceso y el servicio ya dicen lo mismo.

## Una advertencia que investigué

Al arrancar, el servidor avisa que no puede generar un archivo de descripción de la API porque
faltan unas librerías de XML. Lo revisé y no afecta nada: ese formato quedó obsoleto y hoy se usa
otro estándar para documentar servicios REST. Lo dejo anotado para que no parezca un error sin
resolver.

## Estudio de la unidad

Aproveché de estudiar la Unidad 2 completa del ramo, que trata justamente de los dos tipos de
servicios web. Me sirvió para poder justificar mejor la decisión que había tomado al principio de
usar solo REST: ahora puedo explicar qué gana y qué pierde cada opción, y por qué la formalidad del
otro enfoque no aporta nada en un proyecto de una sola persona donde el cliente y el servidor los
escribo yo.

## Los formularios

Antes de empezar verifiqué algo que me habría hecho perder la tarde: **el motor open source no
tiene módulo de formularios**. Revisé qué expone su documentación y aparecen procesos, reglas,
casos, eventos y external workers, pero no formularios. Así que diseñarlos esperando que el motor
los dibujara no iba a funcionar.

También revisé cómo lo resolvió el profesor en su ejemplo, y descubrí que él **no hace los
formularios en Flowable**: los tiene en su aplicación web, en HTML, y desde ahí llama al motor para
completar la tarea con las variables. Su modelo BPMN no tiene ni una referencia a formularios.

Con esos dos datos definí el enfoque: crear los formularios en el diseñador y **vincularlos a las
tareas**, de modo que el motor publique cuál corresponde a cada una. El motor no los dibuja —eso lo
hará mi aplicación— pero sí informa cuál toca. Es exactamente el patrón del ejemplo del curso, y
además es lo que hace posible que la interfaz sea independiente del motor.

Antes de arriesgarme exporté a un archivo aparte para revisar cómo quedaba escrita la referencia en
el XML, sin tocar la versión que ya me funcionaba. Salió como un atributo de texto simple, que es el
caso inofensivo: el motor lo guarda sin intentar interpretarlo. Recién ahí reemplacé el archivo bueno
y desplegué.

### Cuáles hice y por qué solo esos

Hice **dos**, y no por falta de tiempo sino por criterio: son los únicos cuya información **decide
por dónde sigue el proceso**.

| Formulario | Variable que produce | Gateway al que alimenta |
|---|---|---|
| Revisión del pago | aprobación y motivo del rechazo | ¿Pago aprobado? |
| Gestión del despacho | tipo de despacho | ¿Voluntario o courier? |

Las demás tareas humanas o son confirmaciones sin datos que capturar, o registran información que no
cambia el rumbo del proceso. Y el formulario para adjuntar el comprobante corresponde a la web
pública del cliente, no al panel interno.

En los dos aproveché de dejar el **valor por defecto en la opción segura** —el pago sin aprobar y el
despacho por voluntario—, que son los mismos caminos que marqué como flujo default en los gateways.
Así el formulario y el proceso coinciden incluso si la persona no toca nada.

### La comprobación

Desplegué, inicié una instancia nueva y avancé hasta la tarea de revisión. La consulta de tareas
activas, que antes devolvía el campo del formulario vacío, ahora devuelve el identificador del
formulario que corresponde. Esa diferencia es la evidencia de que el vínculo funciona en ejecución y
no solo en el diseñador.

## Estado de la entrega

| Criterio | Estado |
|---|---|
| Modelo AS-IS | ✅ |
| Modelo TO-BE | ✅ |
| Repositorio GitHub | ✅ |
| Actas | ✅ |
| Proceso ejecutable en Flowable | ✅ |
| Coherencia BPMN ↔ Flowable | ✅ |
| Avance en web services | ✅ |
| Formularios en Flowable | ✅ |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |
| Tag `entrega-1` | ☐ |

Solo quedan los dos videos y el tag. Tengo todo el material para grabar: los dos modelos, el proceso
corriendo con sus tres escenarios, el servicio en Java funcionando y los formularios vinculados.

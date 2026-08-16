# Acta 05 — El web service funcionando y los formularios

- **Fecha:** sábado 16 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## La clase que levanta el servidor

Escribí la última de las cuatro clases del servicio, que es la encargada de iniciarlo. Son diez
líneas y cumplen tres funciones: definir la dirección donde escuchará, indicarle a la librería dónde
buscar los recursos y levantar el servidor embebido.

Lo que más me llamó la atención es que la clase con los endpoints no aparece mencionada en ninguna
parte de ese archivo. Nunca la instancio ni la registro manualmente. Solo indico el paquete donde
buscar, y la librería lo recorre, encuentra las clases anotadas y las registra por su cuenta. Ahí
entendí para qué sirven realmente las anotaciones: no son decorativas, sino marcas para que el
framework identifique qué debe publicar. Si más adelante agrego otro recurso, funcionará sin
necesidad de modificar esta clase.

También decidí utilizar el servidor embebido en lugar de instalar uno por separado. El ejemplo del
profesor plantea tres alternativas de despliegue, y elegí la que no depende de que exista un servidor
instalado en la máquina de destino, de modo que el servicio queda como un programa ejecutable normal
que solo requiere Java.

## La prueba de punta a punta

Levanté el servicio y probé los tres endpoints desde un archivo de peticiones, del mismo modo en que
había probado el motor de procesos. Realicé cinco pruebas y todas resultaron correctas:

1. Crear un pedido devuelve el código de recurso creado, junto con el pedido y el identificador que
   le asignó la base de datos.
2. Al listarlos, ya no devuelve una lista vacía.
3. Descontar stock indica que la operación alcanzó.
4. Descontar nuevamente el mismo producto indica que no alcanzó, porque el artículo de prueba tiene
   una sola unidad disponible.
5. Solicitar el descuento de un pedido inexistente devuelve el código de recurso no encontrado, junto
   con el mensaje de error correspondiente.

La cuarta prueba es la que más me interesaba, porque demuestra que el control de sobreventa funciona
efectivamente y corresponde al mismo caso que modelé en BPMN cuando agregué la rama de quiebre de
stock. El proceso y el servicio ya expresan la misma regla.

Al arrancar, el servidor muestra una advertencia indicando que no puede generar un archivo de
descripción de la interfaz por faltarle unas librerías de XML. Lo revisé y no afecta al
funcionamiento: ese formato quedó obsoleto y actualmente se utiliza otro estándar para documentar
servicios REST. Lo dejo registrado para que no parezca un problema sin resolver.

## Los formularios

Antes de comenzar verifiqué algo que me habría hecho perder bastante tiempo: el motor en su versión
open source no incluye el módulo de formularios. Revisé qué expone su documentación y aparecen
procesos, reglas de decisión, casos, eventos y external workers, pero no formularios. Diseñarlos
esperando que el motor los presentara no iba a funcionar.

También revisé cómo lo resolvió el profesor en su ejemplo y descubrí que él no construye los
formularios dentro de Flowable, sino en su aplicación web, y desde ahí llama al motor para completar
la tarea enviando las variables. Su modelo de proceso no contiene ninguna referencia a formularios.

Con esos dos antecedentes definí el enfoque: crear los formularios en el diseñador y vincularlos a
las tareas, de manera que el motor publique cuál corresponde a cada una. El motor no los presenta
—de eso se encargará mi aplicación— pero sí informa cuál toca en cada momento. Es el mismo patrón del
ejemplo del curso y, además, es lo que permite que la interfaz sea independiente del motor.

Antes de arriesgarme exporté el modelo a un archivo aparte para revisar cómo quedaba escrita esa
referencia, sin modificar la versión que ya me estaba funcionando. Resultó ser un atributo de texto
simple, que es el caso inofensivo, ya que el motor lo almacena sin intentar interpretarlo. Recién
entonces reemplacé el archivo definitivo y desplegué.

### Cuáles hice y por qué solo esos

Construí dos formularios, y no por falta de tiempo sino por criterio: son los únicos cuya información
determina por dónde continúa el proceso.

| Formulario | Variable que produce | Gateway al que alimenta |
|---|---|---|
| Revisión del pago | aprobación y motivo del rechazo | ¿Pago aprobado? |
| Gestión del despacho | tipo de despacho | ¿Voluntario o courier? |

Las demás tareas humanas o son confirmaciones que no capturan datos, o registran información que no
modifica el rumbo del proceso. El formulario para adjuntar el comprobante, por su parte, corresponde
a la web pública del cliente y no al panel interno.

En ambos casos dejé el valor por defecto en la opción más conservadora —el pago sin aprobar y el
despacho por voluntario—, que coinciden con los flujos por defecto que había marcado en los gateways.
De esa forma, el formulario y el proceso mantienen el mismo criterio incluso si la persona no
modifica nada.

### La comprobación

Desplegué el modelo, inicié una instancia nueva y avancé hasta la tarea de revisión. La consulta de
tareas activas, que antes devolvía vacío el campo del formulario, ahora devuelve el identificador del
formulario que corresponde. Esa diferencia es la evidencia de que el vínculo funciona durante la
ejecución y no solamente en el diseñador.

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

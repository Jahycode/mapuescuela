# Acta 04 — Arranque del web service en Java

- **Fecha:** jueves 13 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## Primera compilación

Escribí los dos archivos de configuración del proyecto y lo compilé por primera vez. Funcionó a la
primera y sin tener la herramienta de construcción instalada en el computador, ya que los archivos
que copié del repositorio del profesor descargan la versión correcta por su cuenta y compilan con
ella.

Ahí terminé de entender para qué sirven realmente. No se trata solo de comodidad: garantizan que
cualquier persona que clone mi repositorio compile con exactamente la misma versión que yo, sin
instalar nada previamente. Es la misma idea que me resolvió el contenedor con el motor de procesos,
pero aplicada a la compilación.

## Qué datos guarda un pedido y cuáles no

Antes de escribir la primera clase definí qué información debía almacenar un pedido. Los datos que
vienen del checkout eran evidentes, pero dos decisiones me tomaron más tiempo.

La primera fue guardar el identificador de la instancia del proceso. Sin ese dato no tendría forma de
volver a encontrar el pedido dentro del motor, y es lo que hace posible la decisión que había tomado
antes de que el motor sea la fuente de verdad del flujo.

La segunda fue **no** guardar el estado del pedido. Inicialmente pensaba lo contrario: quería tener
una columna con el estado para poder consultarlo rápido y saber cuáles estaban esperando el pago.
Sin embargo, eso entra en conflicto con la decisión anterior, porque si mi base de datos indica una
cosa y el motor indica otra, no tendría manera de determinar cuál es la correcta.

Al revisarlo con más detalle, además, el motor responde esas preguntas mejor que una columna. Para
saber cuáles pedidos están por vencer y en qué momento exacto, existe la consulta de temporizadores
programados. Y para saber cómo terminó un pedido, el motor registra en qué evento de fin cerró, lo
que permite distinguir si se canceló por vencimiento, por rechazo o por falta de stock. Con una
columna de estado eso habría que deducirlo.

Lo que sí incorporé fue la fecha de creación, porque es un dato que no cambia nunca y que voy a
necesitar para obtener información agregada. La regla que me quedó es que el estado del flujo vive en
el motor y los hechos de negocio viven en mi base de datos.

## El descuento de inventario

Es el método más importante del servicio y al que dediqué más tiempo. La versión intuitiva consistiría
en consultar cuánto stock hay y, si alcanza, descontarlo. Pero eso falla en el escenario que ya había
detectado al modelar el proceso: si dos pedidos del mismo producto se aprueban casi al mismo tiempo,
ambos leen el mismo stock, ambos concluyen que alcanza y el inventario termina en negativo.

Lo más importante que aprendí es **por qué** falla, porque mi primera explicación era equivocada.
Pensaba que se trataba de una demora del programa, y no es así. Aunque el código se ejecutara de
forma instantánea, son dos consultas separadas a la base de datos, y entre una y otra la base queda
disponible para atender cualquier otra operación. Ser más rápido no resuelve el problema, solo lo
hace menos frecuente, lo que resulta peor porque entonces falla en producción y no se puede
reproducir.

La solución consiste en dejar que la base de datos decida, mediante una sola sentencia que verifica y
descuenta al mismo tiempo. Si hay stock suficiente afecta una fila y, si no lo hay, no afecta
ninguna. Ese número de filas afectadas es exactamente la variable que el proceso espera recibir del
programa externo.

El método quedó en cuatro líneas y sin ninguna condición escrita en Java, ya que toda la lógica está
en la consulta.

## Sobre los códigos de respuesta

Cuando no hay stock, el servicio responde que la operación se procesó correctamente e incluye el
resultado en el cuerpo de la respuesta. Al principio me pareció extraño y consideré devolver un
error.

Sin embargo, no se trata de un error: la petición se procesó sin problemas y la respuesta es que no
alcanzó. Los códigos de error corresponden a situaciones en que quien llama se equivocó, como
solicitar un pedido que no existe, y en ese caso sí respondo que no se encontró. Que un producto se
haya agotado es un resultado de negocio normal, no una falla.

## Una repetición que convenía eliminar

Al escribir el método para buscar un pedido por su identificador noté que estaba copiando por segunda
vez el bloque que convierte una fila de la base de datos en un objeto. Eso significa que el día que
agregue un campo al pedido tendría que recordar modificarlo en dos lugares distintos.

Lo extraje a un método aparte que utilizan ambos. La búsqueda por identificador pasó de veinticinco
líneas a ocho, y la conversión quedó definida en un solo lugar.

## Estado

Quedaron escritas tres de las cuatro clases del servicio: el modelo de datos, la capa de acceso a la
base y los endpoints. Falta la clase que levanta el servidor y probar el conjunto completo.

| Criterio de la entrega | Estado |
|---|---|
| Modelo AS-IS | ✅ |
| Modelo TO-BE | ✅ |
| Repositorio GitHub | ✅ |
| Actas | ✅ |
| Proceso ejecutable en Flowable | ✅ |
| Coherencia BPMN ↔ Flowable | ✅ |
| Avance en web services | 🔨 3 de 4 clases |
| Formularios en Flowable | ☐ |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |
| Tag `entrega-1` | ☐ |

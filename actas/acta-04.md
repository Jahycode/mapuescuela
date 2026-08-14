# Acta 04 — Arranque del web service en Java

- **Fecha:** jueves 13 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## Primera compilación

Escribí los dos archivos de configuración de Gradle y compilé el proyecto por primera vez. Salió a la
primera, y sin tener Gradle instalado en el computador: el *wrapper* que copié del repositorio del
profesor descarga la versión correcta por su cuenta y compila con ella.

Ahí entendí para qué sirve realmente: no es solo comodidad. Garantiza que cualquiera que clone mi
repositorio compile con exactamente la misma versión que yo, sin instalar nada. Es la misma idea que
me resolvió Docker con el motor, pero aplicada a la herramienta de compilación.

## Qué campos lleva un pedido, y cuáles no

Antes de escribir la primera clase me puse a definir qué datos guarda un pedido. Los que vienen del
checkout eran evidentes, pero dos decisiones me costaron más.

**Guardar el id de la instancia del proceso.** Sin ese campo no tengo cómo volver a encontrar el
pedido en el motor. Es el puente entre mi base de datos y Flowable, y es lo que hace posible lo que
decidí en el ADR-006.

**No guardar el estado.** Esta la pensé al revés primero: mi idea era tener un campo con el estado
del pedido, para poder consultarlo rápido y saber cuáles estaban esperando el pago. Pero eso choca
con mi propia decisión de que el motor es la fuente de la verdad: si mi tabla dice una cosa y el
motor dice otra, no tengo forma de saber cuál está bien.

Y revisando, el motor responde mejor esas preguntas que una columna: para saber cuáles vencen y
cuándo, ya existe la consulta de temporizadores programados, que además me da la hora exacta. Y para
saber cómo terminó un pedido, el motor guarda en qué evento de fin cerró — que distingue si se
canceló por vencimiento, por rechazo o por falta de stock. Con un campo de estado eso habría que
adivinarlo.

Lo que sí dejé es la **fecha de creación**, porque es un hecho que no cambia nunca y que voy a
necesitar para reportería. La regla que me quedó: **el estado del flujo vive en el motor, los hechos
de negocio viven en mi base.**

## El descuento de stock

Es el método más importante del servicio y el que más pensé. La versión intuitiva sería consultar
cuánto stock hay, y si alcanza, descontarlo. Pero eso falla en el caso que ya había detectado al
modelar: si dos pedidos del mismo producto se aprueban casi al mismo tiempo, los dos leen el mismo
stock, los dos creen que alcanza, y el inventario queda negativo.

Lo importante que aprendí es **por qué** falla, porque mi primera explicación estaba equivocada:
pensaba que era un problema de demora del programa. No lo es. Aunque el código fuera instantáneo, son
dos viajes separados a la base, y entre uno y otro la base está libre para atender a cualquier otro.
Ser más rápido no arregla el problema, solo lo hace menos frecuente — que es peor, porque entonces
falla en producción y no se puede reproducir.

La solución es dejar que la base decida, en una sola sentencia que verifica y descuenta al mismo
tiempo. Si hay stock suficiente afecta una fila; si no, no afecta ninguna. Ese número de filas
afectadas es exactamente la variable que mi proceso BPMN espera del worker.

Quedó en cuatro líneas y sin ninguna condición escrita en Java. Toda la lógica está en la consulta.

## Sobre los códigos de respuesta

Cuando no hay stock, el servicio responde que la operación salió bien, con el resultado adentro. Al
principio me pareció raro y pensé en devolver un error.

Pero no es un error: la petición se procesó correctamente y la respuesta es "no alcanzó". Los códigos
de error son para cuando quien llama se equivocó — como pedir un pedido que no existe, que ahí sí
respondo que no se encontró. Que un producto se haya agotado es un resultado de negocio normal, no
una falla.

## Una repetición que había que sacar

Al escribir el método para buscar un pedido por su id me di cuenta de que estaba copiando por segunda
vez el bloque que convierte una fila de la base en un objeto. Eso significa que el día que agregue un
campo al pedido tendría que acordarme de tocarlo en dos lugares.

Lo saqué a un método aparte que usan los dos. La búsqueda por id pasó de veinticinco líneas a ocho, y
la conversión quedó en un solo lugar.

## Estado

Escritas tres de las cuatro clases del servicio: el modelo, la capa de acceso a datos y los
endpoints. Falta la clase que levanta el servidor y probarlo de punta a punta.

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

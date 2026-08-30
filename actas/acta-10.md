# Acta 10 — El AS-IS separado en dos procesos y la definición del lenguaje visual

- **Fecha:** martes 25 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Durante esta sesión trabajé sobre la retroalimentación de la Entrega 1, que llegó con la nota máxima y
siete prioridades de mejora. Una de ellas apuntaba al modelo descriptivo, así que corregí el AS-IS y
después definí el lenguaje visual con el que se van a construir las pantallas.

## Lo que hice

### Separar el AS-IS en dos procesos

El modelo `ventaManualAsIs` mezclaba dos cosas distintas en un solo flujo: la publicación de un objeto
y su venta. En la operación real de Mapuescuela no son un camino continuo. Un objeto se publica una vez
y puede no venderse nunca, o venderse tres meses después. Dibujarlos seguidos daba a entender que
publicar es el primer paso de una venta.

Ahora son dos flujos independientes dentro del mismo archivo `.bpmn`: la publicación va de
`startnoneevent1` a `EndNoneEvent_24`, y la venta arranca en `StartNoneEvent_30` con su propio recorrido.
Dejé el argumento escrito en `bpmn/README.md`, porque el diagrama muestra que están separados pero no
explica por qué.

Antes de dibujarlo evalué usar pools o lanes. **Descarté ambas.** Los pools representan procesos
distintos que se comunican por mensajes, y las lanes son el mismo proceso repartido entre responsables
distintos. Lo mío no encaja en ninguna de las dos, porque son dos procesos que no se hablan entre ellos:
no hay ningún mensaje que vaya de la publicación a la venta. Modelarlo con dos pools habría quedado más
vistoso, pero el criterio de evaluación del modelo descriptivo no lo pide, y preferí la forma más simple
que responde la observación.

### Definir el lenguaje visual

Antes de generar nada revisé guías y videos sobre diseño de páginas de catálogo y sobre construcción de
paletas de color. Podría haber pedido una web con un prompt genérico, pero quería entender primero qué
hace que un catálogo funcione, para poder dirigir la herramienta en vez de quedarme con lo primero que
devolviera.

Con esa base trabajé en paralelo con cuatro herramientas —Claude Design, Grok, ChatGPT y Stitch—,
escribiendo prompts y ajustándolos según lo que devolvía cada una. No fue una pasada: fueron muchas
iteraciones, cambiando la estructura, los valores y los colores. Las cuatro propuestas de estilo que
terminé comparando no son cuatro intentos, sino la conclusión de todo ese trabajo.

Algo que resultó clave fue **entregarle a las herramientas el modelo que ya tenía construido** —el
proceso, los estados del pedido, los endpoints existentes— para que las vistas se ajustaran a lo que ya
está armado en vez de proponer una aplicación distinta que después habría que reconciliar.

La paleta pasó por azul, terracota y una versión en crema con tipografía serif antes de llegar al
violeta `#4B2A82` con mostaza `#E8A81C` como único acento.

Al final me quedé con **un prompt específico**, el que producía resultados consistentes, y con ese
modelé el resto de las vistas.

## Error encontrado

Este no fue un error de código sino de supuestos, y me sirvió como método.

Mientras discutía las pantallas, se dio por sentado que el voluntario iba a trabajar desde el teléfono
y empecé a razonar sobre esa base. No recordaba haberlo escrito en ninguna parte, así que pregunté de
dónde salía:

> ¿En qué documento del proyecto dice que el voluntario usa el celular?

En ninguno. Era una suposición inventada, no un requisito. Estuve a punto de tomar decisiones de diseño
para un usuario que no existe en mi enunciado.

De ahí salió el **ADR-009**, que dejé documentado en `docs/README.md`: las pantallas son para computador
de escritorio, y no es un olvido. Dejo constancia de que el cliente probablemente llegue desde Instagram
en el teléfono y que lo asumo a propósito, porque adaptar a móvil no forma parte de lo que evalúa el
ramo. Lo único que sí hago es no fijar anchos en píxeles, sino usar un ancho máximo con márgenes
flexibles, para que en una pantalla chica se vea apretado pero legible en vez de cortado.

El aprendizaje es que cuando aparece un requisito que no reconozco, conviene preguntar de dónde sale
antes de empezar a diseñar para él.

## Pendientes y decisiones

- El bloque `<documentation>` de `ventaManualAsIs.bpmn` todavía describe el proceso viejo como si fuera
  uno solo. Hay que editarlo en Flowable Design y exportar de nuevo.
- Decidí no usar pools ni lanes en el AS-IS. Si en la Entrega 3 se pide justificar la notación, el
  argumento ya está escrito en `bpmn/README.md`.
- No guardé los prompts con los que llegué al resultado. Son la evidencia del trabajo de exploración y
  conviene registrarlos de aquí en adelante, aunque sea en un archivo suelto.
- Con el lenguaje visual definido, lo siguiente es diseñar las pantallas.

## Cierre

La sesión cerró la observación del profesor sobre el modelo descriptivo y dejó definido el sistema
visual con el que se van a construir todas las pantallas. Lo que queda como criterio para adelante es
que el resultado de una herramienta generativa depende de con cuánto contexto se la dirige: investigar
primero cómo se diseña un catálogo, y entregarle además el proceso y los endpoints que ya existen,
produjo propuestas que encajan con lo construido en vez de vistas que después habría que reconciliar.

## Estado de la Entrega 2

| Criterio | Estado |
|---|---|
| Modelo BPMN ejecutable | ✅ |
| Modelo descriptivo AS-IS | ✅ corregido según la retroalimentación |
| Uso de tareas BPMN y external workers | ✅ |
| Proceso ejecutándose en Flowable | ✅ las seis salidas recorridas |
| Funcionamiento y prueba de web services | ✅ |
| Repositorio GitHub | ✅ |
| Gestión y planificación | ✅ |
| Web services que cubren el proceso | ✅ ocho endpoints |
| Interfaces de usuario | ☐ lenguaje visual definido, pantallas pendientes |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |

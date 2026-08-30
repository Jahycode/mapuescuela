# Acta 11 — Las cinco pantallas del prototipo y el contrato del sistema visual

- **Fecha:** miércoles 26 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Durante esta sesión diseñé las pantallas de la web. Quedaron cinco:

- Catálogo
- Checkout
- Seguimiento del pedido, con sus cinco estados
- Bandeja de tareas de la voluntaria
- Resolver una tarea

Faltan dos: el detalle del objeto y la de publicar. Las trabajé con las mismas herramientas de la
sesión anterior —Claude Design, Grok, ChatGPT y Stitch—, partiendo del prompt específico con el que
había cerrado el día anterior y ajustando después los resultados a mano.

## Lo que hice

### El contrato del sistema visual

`web/prototipo/_sistema.md` es la formalización del prompt específico con el que venía trabajando. Lo
saqué del historial de una conversación y lo dejé como documento aparte, para poder pegarlo en cualquier
herramienta antes de pedir una pantalla nueva, en vez de depender de encontrar el mensaje correcto.

Hacía falta porque cada herramienta impone su propio sistema si no se le entrega uno: en el segundo
archivo ya había dos nombres distintos para el mismo color de estado.

El documento contiene el bloque completo de tokens de color y tipografía, el
orden de las capas `@layer`, los nombres de clase que hay que reutilizar en vez de reinventar
(`.panel`, `.btn`, `.lbl`, `.insignia`), y las reglas de escritura: tuteo, cero jerga técnica visible,
montos con separador de miles chileno, y que toda acción irreversible venga acompañada de una frase que
explique qué va a pasar.

Funcionó en lo que cubría. El bloque `@layer tokens` quedó idéntico en los cinco archivos, cosa que
verifiqué comparando su hash y no a ojo: los cinco dan `cd109728`.

### Dos decisiones de las pantallas del voluntario

En `mapuescuela-resolver-tarea.html`, aprobar un pago pide escribir a mano el monto que aparece en la
foto del comprobante y lo compara con el del pedido. Parece un trámite de más y es al revés: aprobar una
transferencia por un monto distinto significa después perseguir la diferencia con alguien que ya se
llevó los objetos.

En la misma pantalla, cuando hay que rechazar, el mensaje se escribe con una previa a la vista que
muestra cómo lo va a ver el cliente en su página, firmado con el nombre de quien lo escribió. Escribir a
ciegas en un cuadro de texto produce mensajes que no se entienden.

La regla detrás de las dos es que **la fricción va con la consecuencia y no con la frecuencia**:
aprobar es un clic y se puede deshacer, mientras que cancelar pide texto obligatorio, ver la previa y
una marca de confirmación. Poner la misma confirmación en ambas haría que la voluntaria apriete sin
leer.

## Error encontrado

Al revisar las cinco pantallas juntas aparecieron contradicciones en los datos de ejemplo que no se
notan mirándolas de a una.

El objeto **N° 0148 era un velador** en cuatro archivos y **una caja de libros infantiles** en el
catálogo. La cómoda tenía un número en la bandeja y otro distinto en el catálogo. Y el pie del catálogo
cierra la página con esta frase:

> Los números no se repiten nunca. El N° 0148 fue ese velador y no va a ser nada más.

Escrita en el único archivo donde ese número era otra cosa. La frase que enuncia la regla la desmiente
el propio archivo que la contiene.

Esto pasó porque cada pantalla se diseñó por separado y cada una inventó sus datos de prueba. Debajo
apareció algo más grave, que no es de diseño sino de modelo: en las pantallas **el número del pedido y
el número del objeto eran el mismo número** — el pedido MAP-0148 traía el objeto 0148. Un pedido y un
objeto son cosas distintas y cada uno lleva su propia numeración; que coincidieran era una confusión que
estaba a punto de pasar a la base de datos.

El aprendizaje es que el diseño hecho en piezas separadas se contradice solo, y la revisión en conjunto
no es opcional.

## Pendientes y decisiones

- El contrato solo cubrió lo que nombró. Lo que no nombró derivó igual: `.insignia` terminó con cuatro
  definiciones distintas en cuatro archivos, y la caja de avisos con tres nombres. Para la próxima tanda
  hay que nombrar también los componentes, no solo los tokens.
- Quedaron alrededor de doce errores detectados en la revisión y ninguno corregido todavía.
- La numeración de pedidos y objetos hay que resolverla en la base antes de conectar cualquier pantalla.
- Faltan las dos pantallas restantes.

## Cierre

La sesión dejó las cinco pantallas principales diseñadas y un contrato que evitó que el sistema visual
se fragmentara entre herramientas. Lo que queda como criterio es que un contrato de este tipo protege
exactamente lo que enumera y nada más: los tokens que nombré quedaron idénticos, y los componentes que
no nombré derivaron en cuatro versiones.

## Estado de la Entrega 2

| Criterio | Estado |
|---|---|
| Modelo BPMN ejecutable | ✅ |
| Modelo descriptivo AS-IS | ✅ |
| Uso de tareas BPMN y external workers | ✅ |
| Proceso ejecutándose en Flowable | ✅ las seis salidas recorridas |
| Funcionamiento y prueba de web services | ✅ |
| Repositorio GitHub | ✅ |
| Gestión y planificación | ✅ |
| Web services que cubren el proceso | ✅ ocho endpoints |
| Interfaces de usuario | ◐ cinco pantallas diseñadas, ninguna conectada |
| Video para la emprendedora | ☐ |
| Video técnico | ☐ |

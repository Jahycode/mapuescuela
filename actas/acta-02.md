# Acta 02 — Modelado completo y preparación de la Entrega 1

- **Fechas:** domingo 10 y lunes 11 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## El modelo del proceso actual

Comencé dibujando el modelo del proceso manual, que era uno de los elementos que me faltaban según la
rúbrica. Antes de hacerlo me pregunté qué sentido tenía modelar algo que igual iba a reemplazar, y
llegué a la conclusión de que sin ese modelo las mejoras del proceso nuevo quedarían como propuestas
sueltas, sin nada con qué compararlas. Lo dibujé tal como me lo describieron: publican el artículo en
Instagram, el cliente comenta o escribe, coordinan todo por WhatsApp y anotan la venta en un cuaderno.

## Las validaciones del proceso automatizado

Después trabajé las condiciones de los gateways del modelo nuevo, utilizando la sintaxis que muestra
el material del curso, y marqué los flujos por defecto de cada uno.

Aquí tomé una decisión que considero importante: todos los flujos por defecto apuntan al camino más
conservador, es decir, rechazar el pago, asumir que no hay stock y despachar en lugar de entregar en
retiro. De esta forma, si alguna variable de decisión llegara vacía, el proceso nunca aprobaría un
pago ni entregaría un producto por accidente.

También detecté un vacío en la lógica del modelo. Tenía un gateway que preguntaba si el despacho lo
realizaba un voluntario o un courier, pero no había ninguna tarea previa donde esa decisión se
tomara. Agregué entonces la tarea de gestión del despacho, en la que el voluntario define la
modalidad. La ubiqué ahí porque, según el enunciado, esa decisión corresponde a la organización y no
al cliente.

## El caso del artículo que se vende dos veces

El enunciado pide evitar que se vendan unidades que ya no están disponibles, así que me puse en el
escenario concreto: existe un solo sofá, dos personas lo compran y ambas transfieren. El voluntario
aprueba el primer pago y el stock queda en cero, de modo que al aprobar el segundo ya no hay nada que
entregar.

Lo resolví agregando un gateway posterior al descuento de inventario, que consulta si el descuento
pudo realizarse. El worker intenta la operación y devuelve una variable con el resultado; si no
alcanzó, el proceso toma una rama que notifica al cliente y termina en un evento de fin propio.
Decidí modelar este caso dentro del proceso y no resolverlo dentro del código porque cancelar un
pedido que ya fue pagado es una decisión de negocio, y como tal debe quedar visible y trazable.

Además, como los artículos son donados y en su mayoría únicos, no existe la posibilidad de reponer
stock. Por eso la única salida realista es notificar al cliente y coordinar la devolución del dinero.

## Revisión técnica del archivo exportado

Antes de desplegar quise verificar algo que me preocupaba: dibujé el modelo con la paleta de la
versión licenciada de Flowable, pero la entrega final debe ejecutarse sobre la versión open source.
Revisé el archivo exportado y confirmé que las tareas automáticas, el temporizador, los flujos por
defecto y las condiciones están escritos con sintaxis estándar, sin nada exclusivo de la versión
pagada. Por lo tanto, la migración del cierre del ramo no debería presentar dificultades.

En esa misma revisión encontré un detalle que de otra forma habría pasado inadvertido. Trece
elementos tenían su nombre guardado en una extensión propia de la herramienta de diseño en lugar del
atributo estándar, lo que ocurría con todos los nombres que había escrito utilizando saltos de línea.
El modelo se desplegaba igual, pero el motor los habría mostrado sin nombre en el historial de
actividades, que es justamente la evidencia que pienso utilizar para demostrar el recorrido del
proceso. Los reescribí todos en una sola línea, en ambos modelos.

## El proceso corriendo y un error que solo apareció al ejecutarlo

Levanté el motor de Flowable open source en un contenedor y desplegué el modelo mediante la API REST.
Inicié una instancia de prueba configurando el plazo de pago en dos minutos en lugar de veinticuatro
horas, para poder demostrar el vencimiento sin tener que esperar un día completo.

El temporizador se disparó por sí solo, sin ninguna intervención. Sin embargo, al revisar el historial
de actividades me encontré con que el recorrido se cortaba justo en el temporizador y nunca llegaba a
cancelar el pedido. Revisando el archivo del modelo encontré la causa: la flecha hacia la tarea de
cancelación nacía en la tarea de adjuntar el comprobante y no en el temporizador.

Ese error tenía dos consecuencias. La primera es que, al vencerse el plazo, el token no tenía por
dónde continuar y la instancia terminaba en silencio. La segunda es más grave: la tarea quedaba con
dos flechas de salida sin ningún gateway entre medio, lo que en BPMN se interpreta como una
bifurcación paralela. Es decir, al subir el comprobante el pedido habría avanzado a revisión y a
cancelación al mismo tiempo.

Lo corregí redibujando la flecha desde el temporizador, volví a desplegar y repetí la prueba. En esta
ocasión el recorrido llegó completo hasta la tarea de cancelación.

Lo que rescato de esta situación es que la validación de la herramienta de diseño no detectó el
error: el panel de validaciones estaba limpio y el diagrama se veía correcto. Un modelo que valida no
es necesariamente un modelo que funciona, y la única manera de comprobarlo fue ejecutarlo.

Finalmente, el token quedó detenido en la tarea de cancelación, que es una tarea de external worker.
El motor publica el trabajo y espera que un programa externo lo tome, y ese programa corresponde a la
próxima entrega. Ese es entonces el punto exacto donde termina el alcance de esta.

## Cómo quedó el proceso

El modelo quedó con ocho tareas humanas, cinco tareas automáticas resueltas como external workers,
cuatro gateways exclusivos, un temporizador de veinticuatro horas y seis eventos de fin distintos.
Los mantuve separados para poder distinguir en el historial si un pedido terminó correctamente, si se
venció, si fue rechazado o si se quedó sin stock.

## Estado de los pendientes

| # | Pendiente | Estado |
|---|---|---|
| 1 | Modelo AS-IS | ✅ |
| 2 | Modelo TO-BE con validación limpia | ✅ |
| 3 | Motor Flowable levantado en local | ✅ |
| 4 | Proceso desplegado vía API REST | ✅ |
| 5 | Instancia de prueba recorriendo las tareas | ✅ |
| 6 | Formularios de las tareas humanas | ☐ |
| 7 | Avance de web services | ☐ |
| 8 | Video técnico y video para la emprendedora | ☐ |
| 9 | Tag `entrega-1` | ☐ |

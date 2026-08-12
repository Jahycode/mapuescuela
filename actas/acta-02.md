# Acta 02 — Modelado completo y preparación de la Entrega 1

- **Fechas:** domingo 10 y lunes 11 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## Domingo 10: el modelo AS-IS y las validaciones del TO-BE

Partí dibujando el modelo del proceso manual actual, que me faltaba. Antes de hacerlo me pregunté
para qué servía si igual iba a construir el proceso nuevo, y la respuesta es que sin el AS-IS las
mejoras no se pueden justificar: quedan como propuestas sueltas en vez de soluciones a un problema
concreto. Lo dibujé tal como me lo describieron: publican en Instagram, el cliente comenta o escribe,
coordinan todo por WhatsApp y anotan la venta en un cuaderno.

Después me metí con las validaciones del modelo automatizado. Le puse las condiciones a los gateways
con la sintaxis del curso (`${vars:equals(variable, valor)}`) y marqué los flujos default. Acá tomé
una decisión que me parece importante: **todos los default apuntan al camino seguro** — rechazar el
pago, asumir que no hay stock, despachar. Si alguna variable llegara vacía, el proceso nunca va a
aprobar un pago ni entregar un producto por accidente.

También me di cuenta de un hueco lógico: tenía un gateway que preguntaba si el despacho lo hacía un
voluntario o un courier, pero nadie definía eso antes. Agregué la tarea **Gestionar despacho**, donde
el voluntario decide. Va ahí porque según el enunciado la decisión es de la organización, no del
cliente.

## El caso del artículo que se vende dos veces

El enunciado pide evitar vender unidades que ya no están disponibles, así que me puse en el caso: hay
un solo sofá, dos personas lo compran y las dos transfieren. El voluntario aprueba a la primera y el
stock queda en cero; cuando aprueba a la segunda, ya no hay nada que entregar.

Lo resolví agregando un gateway **¿Había stock?** después de descontar inventario. El worker intenta
el descuento y devuelve una variable con el resultado; si no se pudo, el proceso se va por una rama
que avisa al cliente y termina en su propio final. Modelé este caso en el proceso y no lo escondí en
el código a propósito: cancelar un pedido que ya está pagado es una decisión de negocio y tiene que
quedar visible y trazable.

Como los artículos son donados y muchos son únicos, no existe la posibilidad de reponer. Por eso la
única salida realista es avisarle al cliente y coordinar la devolución del dinero.

## Lunes 11: revisión técnica del XML

Antes de desplegar quise verificar algo que me preocupaba: dibujé con la paleta de la versión
licenciada de Flowable, pero la entrega final tiene que correr sobre la versión open source. Revisé
el XML exportado y confirmé que las tareas automáticas, el temporizador, los flujos default y las
condiciones están todos escritos con sintaxis estándar. No hay nada exclusivo de la versión pagada,
así que la migración del final no debería darme problemas.

De paso encontré un detalle que se me habría pasado: **13 elementos tenían el nombre guardado en una
extensión propia de la herramienta de diseño en vez del atributo estándar**. Pasaba con todos los
nombres que escribí apretando Enter para cortar la línea. El modelo se desplegaba igual, pero el
motor los habría mostrado sin nombre en el historial de actividades, que es justamente la evidencia
que voy a usar para demostrar el recorrido. Los reescribí todos en una sola línea, en los dos
modelos.

Cerré dejando ambos modelos con la validación limpia y corrigiendo la documentación del repositorio,
que en algunas partes describía un modelo anterior al que terminé dibujando.

## Cómo quedó el proceso

8 tareas humanas, 5 automáticas como external workers, 4 gateways exclusivos, un temporizador de 24
horas y 6 finales diferenciados, para poder distinguir en el historial si un pedido terminó bien, se
venció, lo rechazaron o se quedó sin stock.

## Pendientes para la entrega de mañana

| # | Pendiente | Estado |
|---|---|---|
| 1 | Modelo AS-IS | ✅ |
| 2 | Modelo TO-BE con validación limpia | ✅ |
| 3 | Motor Flowable levantado en local | ☐ |
| 4 | Proceso desplegado vía API REST | ☐ |
| 5 | Instancia de prueba recorriendo las tareas | ☐ |
| 6 | Formularios de las tareas humanas | ☐ |
| 7 | Endpoint REST como avance de web services | ☐ |
| 8 | Video técnico y video para la emprendedora | ☐ |
| 9 | Tag `entrega-1` | ☐ |

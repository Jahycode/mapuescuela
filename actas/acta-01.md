# Acta 01 — Arranque del proyecto

- **Fecha:** sábado 9 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## Qué hice en esta sesión

Primero revisé nuevamente el enunciado completo del caso Mapuescuela y volví a ver parte de la clase
grabada del profesor para tener claras las reglas del ramo. Entre ellas, que los web services deben
desarrollarse en Java, que las entregas deben ser rebanadas funcionales y ejecutables, que tenemos
que llevar actas y que el motor de procesos será la fuente de verdad del flujo.

Después revisé el repositorio de ejemplo que compartió el profesor (INP-complementario-socios) para
entender mejor cómo está planteada la solución. Ahí vi que la web se comunica con Flowable mediante
REST, que las tareas automáticas se manejan mediante external workers con topics y que estos workers
finalmente llaman a un web service en Java. Para el proyecto decidí mantener esa misma lógica, pero
utilizar Python en algunas partes donde me permite avanzar más rápido.

A partir de eso armé el repositorio y dejé separadas las carpetas según cada componente. También
documenté las principales decisiones de arquitectura en `docs/`, principalmente para dejar registrado
por qué se tomaron ciertas decisiones y no tener que reconstruirlo más adelante.

Finalmente, avancé con el modelo del proceso automatizado en Flowable Design. Dejé planteado el flujo
desde el checkout, incluyendo la tarea para adjuntar el comprobante con un temporizador de 24 horas,
la revisión del pago, el descuento de inventario y las distintas alternativas de entrega.

## Lo que revisé de la rúbrica

Al revisar con más detalle la pauta de la Evaluación 1, me di cuenta de que había algunos elementos
que todavía no tenía considerados. Entre ellos están el modelo AS-IS del proceso actual, los
formularios dentro de Flowable, un avance de los web services y, algo que había pasado por alto, que
se deben entregar dos videos y no uno.

## Compromisos para la Entrega 1

| # | Compromiso | Estado al cierre de la sesión |
|---|---|---|
| 1 | Repositorio en GitHub, público y compartido al profesor | ✅ |
| 2 | Modelo TO-BE dibujado en Flowable Design | ✅ |
| 3 | Modelo AS-IS del proceso manual actual | ☐ |
| 4 | Formularios de las tareas humanas | ☐ |
| 5 | Endpoint REST como avance de web services | ☐ |
| 6 | Proceso desplegado en el motor vía API REST | ☐ |
| 7 | Instancia de prueba recorriendo las tareas | ☐ |
| 8 | Video técnico y video para la emprendedora | ☐ |
| 9 | Tag `entrega-1` en el repositorio | ☐ |

# Acta 01 — Arranque del proyecto

- **Fecha:** sábado 9 de agosto de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

## Qué hice en esta sesión

Partí leyendo el enunciado completo del caso Mapuescuela y volviendo a la clase grabada del profesor
para sacar las reglas del ramo: los web services tienen que ser en Java, las entregas son rebanadas
ejecutables y no unidades sueltas, hay que llevar actas, y el motor pasa a ser la fuente de la verdad
del flujo.

Después revisé el repositorio de ejemplo que compartió el profesor (`INP-complementario-socios`) para
entender el patrón que usa el curso: la web llama a Flowable por REST, las tareas automáticas son
external workers con topic, y el worker termina llamando a un web service Java. Decidí replicar ese
patrón cambiando PHP por Python, que es donde avanzo más rápido.

Con eso armé el repositorio, dejé las carpetas por componente y escribí las decisiones de
arquitectura en `docs/DECISIONES.md` para no tener que acordarme después del porqué de cada cosa.

Terminé la sesión dibujando el modelo del proceso automatizado en Flowable Design: el inicio en el
checkout, la tarea de adjuntar el comprobante con el temporizador de 24 horas, la revisión del pago,
el descuento de inventario y las ramas de entrega.

## Lo que revisé de la rúbrica

Leyendo la pauta de la Evaluación 1 me di cuenta de que faltaban cosas que no tenía contempladas: el
modelo AS-IS del proceso actual, los formularios en Flowable, un avance de web services y **dos**
videos, no uno.

## Compromisos para la Entrega 1 (martes 12/08)

| # | Compromiso | Estado al cierre de la sesión |
|---|---|---|
| 1 | Repositorio en GitHub, público y compartido al profesor | ✅ |
| 2 | Modelo TO-BE dibujado en Flowable Design | ✅ |
| 3 | Modelo AS-IS del proceso manual actual | ☐ |
| 4 | Formularios de las tareas humanas | ☐ |
| 5 | Endpoint REST simple como avance de web services | ☐ |
| 6 | Proceso desplegado en el motor vía API REST | ☐ |
| 7 | Instancia de prueba recorriendo las tareas | ☐ |
| 8 | Video técnico y video para la emprendedora | ☐ |
| 9 | Tag `entrega-1` en el repositorio | ☐ |

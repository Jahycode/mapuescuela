# worker/ — El programa que ejecuta las tareas automáticas

**Pendiente para la Entrega 2.**

El motor de Flowable no ejecuta las tareas automáticas por sí solo: publica un trabajo identificado
con un *topic* y espera. Este worker es el programa que le pregunta al motor si hay algo pendiente,
lo toma, hace la pega llamando a `ws-pedidos`, y le avisa al motor que terminó.

Los cinco topics que tiene que atender están en `bpmn/README.md`.

Lo bueno de este modelo es que el worker puedo escribirlo en el lenguaje que quiera aunque el motor
sea Java, y si se cae, el proceso no se rompe: los trabajos quedan esperando hasta que vuelva.

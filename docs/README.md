# docs/ — Decisiones y referencia técnica

Dos cosas hay acá: el registro de las decisiones importantes que fui tomando (más abajo), y
`flowable-api.http`, un archivo con todas las peticiones a la API de Flowable listas para ejecutar —
desplegar el modelo, iniciar instancias, completar tareas, hacer de worker a mano y revisar el
historial. Se usa con la extensión *REST Client* de VS Code.

---

## Decisiones de arquitectura

### ADR-001 · Arquitectura espejo del patrón del curso

Aplicaré lo visto en el repositorio de GitHub que envió el profesor, con algunas modificaciones:
Python → Flowable REST → worker → ws-pedidos en Java. Así quedo alineado con lo que el curso enseña
y evalúa, y me sirve de referencia directa cada vez que me trabe con algo.

### ADR-002 · Solo REST, sin SOAP

El profesor autorizó en clase usar solo REST, porque este es un servicio disciplinar y SOAP es
bastante más complejo. Entonces todos mis servicios van a ser REST. SOAP lo dejo solo como
comparación en la documentación, para mostrar que entiendo la diferencia.

### ADR-003 · Las tareas automáticas van como external workers

Flowable ofrece varias formas de automatizar un paso, pero el profesor dijo que el mecanismo del
curso es el external worker, así que voy con ese. La gracia es que el motor publica un trabajo y lo
consume un programa aparte: eso me permite escribir el worker en Python aunque el motor sea Java, y
si el worker se cae el proceso no se rompe, los trabajos quedan esperando.

Los topics de cada tarea los tengo documentados en `bpmn/README.md`, para no repetir la misma
información en dos partes y que después no me queden desincronizadas.

### ADR-004 · La web en Python y el web service en Java

El curso deja libre la tecnología de la interfaz y la base de datos, pero exige que los web services
sean en Java. Como en Python y SQL Server avanzo mucho más rápido, hago la web ahí y dejo Java
solamente para el ws-pedidos, que es donde el curso lo pide. Me queda una parte en Java chica y bien
delimitada, y de paso una integración real entre tres plataformas distintas, que es de lo que se
trata el ramo.

### ADR-005 · SQL Server para el negocio

La base de datos quedó a libre elección y SQL Server es la que mejor manejo, así que los datos del
negocio van ahí. Para la base del motor de Flowable voy a intentar lo mismo; si me consume más de un
día configurarlo, me paso a MySQL siguiendo la guía del curso y sigo avanzando. Poder revisar el
motor desde SSMS me sirve harto para depurar y para mostrar evidencia en los videos.

### ADR-006 · El motor es la fuente de la verdad

El profesor fue explícito en esto: la fuente de la verdad pasa a ser el motor. Entonces guardo el id
de la instancia en mi tabla de pedidos y el estado se lo pregunto al motor, en vez de llevar un
estado propio en paralelo. Así no termino con dos versiones de la verdad que se desincronizan.

### ADR-007 · Modelo con la licencia, entrego en open source

Modelo en Flowable Design porque el convenio con Iplacex me da acceso, pero la entrega final tiene
que correr sobre la versión open source: Mapuescuela no puede pagar una licencia. Ya revisé que el
XML que exporto no use nada exclusivo de la versión pagada, así que la migración no debería darme
sorpresas al final.

### ADR-008 · Sin login de clientes

El enunciado no pide cuentas de cliente y el profesor recomendó no gastar tiempo en accesos con
contraseña, porque estos emprendedores son una sola persona operando todo. El cliente compra sin
registrarse y sigue su pedido con un link con token. Me ahorro usuarios, roles y recuperación de
contraseñas, y ese tiempo se me va en el proceso, que es lo que evalúan.

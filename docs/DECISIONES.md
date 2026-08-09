# Decisiones de arquitectura (ADRs)

Registro de las decisiones importantes del proyecto, con su justificación. Formato corto:
contexto → decisión → consecuencias.

---

## ADR-001 · Arquitectura espejo del patrón de referencia del curso

**Contexto.** El curso publica un ejemplo oficial (repo `INP-complementario-socios`) con el patrón:
aplicación web → API REST de Flowable (iniciar instancias, completar user tasks) → tareas
automáticas como *External Worker tasks* → worker que invoca a un web service Java de dominio.

**Decisión.** Replicar ese patrón: `web/` (Python) ↔ Flowable REST ↔ `worker/` ↔ `ws-pedidos/` (Java).

**Consecuencias.** Alineación total con lo que el curso enseña y evalúa; el ejemplo del profesor
sirve de referencia directa ante cualquier duda técnica.

## ADR-002 · Solo REST (sin SOAP)

**Contexto.** El material de la Unidad 2 cubre SOAP y REST. El profesor indicó en clase que, al ser
servicio disciplinar, basta con REST ("es mucho más sencillo") y autorizó no usar SOAP.

**Decisión.** Todos los servicios del proyecto son REST/JSON. SOAP se aborda solo a nivel de
análisis comparativo en la documentación (protocolo vs estilo, XML/WSDL vs JSON, casos de uso).

**Consecuencias.** Menos complejidad; se elimina un componente completo (servicio de notificaciones
SOAP del ejemplo de la Unidad 3).

## ADR-003 · Tareas automáticas como External Worker tasks

**Contexto.** Flowable permite automatizar pasos con JavaDelegates (requieren Java embebido),
ScriptTasks (Groovy/JS) o External Worker tasks (el motor publica *jobs* por topic y un proceso
externo los consume). El profesor indicó en clase que el mecanismo del curso es el external worker.

**Decisión.** Las 4 tareas automáticas del proceso son External Worker tasks con topics
(`cancelarPedidoVencido`, `registrarRechazo`, `descontarInventario`, `cancelarPorStock`).

**Consecuencias.** El modelo queda desacoplado del lenguaje de implementación; el worker corre como
proceso aparte y ante caída no bloquea al motor (los jobs esperan). Requiere levantar el worker para
que las instancias avancen por esos pasos.

## ADR-004 · Web en Python/FastAPI; web service de dominio en Java

**Contexto.** Regla del curso: interfaces de usuario y persistencia pueden hacerse "con la
tecnología que más acomode" (el autor domina Python y SQL Server); los **web services son contenido
core y deben ser Java**.

**Decisión.** `web/` en Python + FastAPI (catálogo, carrito, checkout, seguimiento con token, panel
del voluntario). `ws-pedidos/` en Java + JAX-RS/Jersey + Gradle (mismo stack del ejemplo del curso),
exponiendo las operaciones de negocio que el proceso orquesta (descuento de inventario, cancelación,
registro de decisiones). El worker invoca al WS Java; la web consulta catálogo/pedidos.

**Consecuencias.** Se cumple el requisito de Java exactamente donde el curso lo exige, con una
superficie Java pequeña y bien delimitada; la productividad del resto del sistema queda en el stack
más fuerte del autor. Integración real entre tres plataformas (Python ↔ Flowable ↔ Java).

## ADR-005 · SQL Server para el negocio; motor con plan B

**Contexto.** El profesor dejó la base de datos a libre elección. El autor domina SQL Server.

**Decisión.** `MAPUESCUELA_DB` en SQL Server 2022 (negocio). Para la BD del motor de Flowable se
intenta también SQL Server (dialecto soportado oficialmente); si la configuración consume más de un
día, plan B: MariaDB/MySQL siguiendo la guía paso a paso del curso.

**Consecuencias.** Depuración del motor con SSMS (tablas `ACT_RU_*`: ver el timer programado, dónde
está el token) — evidencia valiosa para las demostraciones.

## ADR-006 · El motor es la fuente de la verdad del flujo

**Contexto.** Indicación explícita del profesor: "acá la fuente de la verdad pasa a ser el motor…
en la BD guardas el id de la instancia y le consultas al motor en qué paso está".

**Decisión.** La tabla `pedido` guarda `process_instance_id`. El estado visible se **deriva** de la
instancia (tareas activas / histórico). En la BD solo se materializan hechos de negocio
irreversibles (stock descontado, cancelado con motivo, datos de despacho).

**Consecuencias.** No hay doble fuente de verdad ni estados desincronizados. La UI sigue el modelo
mental de "bandeja de tareas". Prueba ácida: con el motor apagado, ninguna compra puede avanzar.

## ADR-007 · Modelar en Flowable Design (licencia); entregar sobre open source

**Contexto.** Convenio Iplacex-Flowable da acceso a la versión licenciada. El curso exige que la
solución final sea utilizable por el emprendedor sin costos de licencia.

**Decisión.** Prototipado y modelado en Flowable Design; la solución final corre sobre
`flowable-rest` **open source** (WAR en Tomcat). La migración está planificada como fase (no como
imprevisto) en las últimas semanas.

**Consecuencias.** Aprendizaje rápido con la herramienta guiada + entrega sin costo de licencia.

## ADR-008 · Sin login de clientes; seguimiento por URL con token

**Contexto.** Los emprendedores del programa son microempresarios: una persona opera todo (dicho por
el profesor). El enunciado no pide cuentas de cliente, y el profesor recomendó no gastar tiempo en
accesos con credenciales.

**Decisión.** El cliente compra sin registrarse y sigue su pedido vía `/pedido/{numero}?t={token}`.
El panel del voluntario/emprendedor tiene un único acceso simple.

**Consecuencias.** Se elimina gestión de usuarios, roles y recuperación de contraseñas; el foco
queda en el proceso.

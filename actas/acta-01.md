# Acta 01 — Inicio del proyecto y planificación

- **Fecha:** sábado 09 de agosto de 2026
- **Asistentes:** Valentín González (trabajo individual, autorizado por el profesor)
- **Modalidad:** sesión de trabajo asíncrona

## Temas tratados

1. Análisis del caso Mapuescuela (enunciado completo) y de la clase introductoria del profesor.
2. Estudio del repositorio de ejemplo del curso (`INP-complementario-socios`) para adoptar su patrón
   de integración: web ↔ Flowable REST ↔ external workers ↔ web service Java.
3. Definición de la arquitectura y registro de decisiones en `docs/DECISIONES.md` (ADR-001 a 008).
4. Diseño del proceso de venta en BPMN (elementos, variables, topics, estados) — `bpmn/README.md`.
5. Creación del mono-repo con la estructura de carpetas por componente.

## Compromisos (para la Entrega 1 — martes 12/08)

| # | Compromiso | Responsable | Estado |
|---|---|---|---|
| 1 | Repositorio GitHub público creado y compartido al profesor | Valentín | ☐ |
| 2 | Modelo de venta dibujado en Flowable Design (key `ventaMapuescuela`) | Valentín | ☐ |
| 3 | Modelo desplegado en Flowable vía API REST (evidencia: deployment 201) | Valentín | ☐ |
| 4 | Instancia demo iniciada y user tasks recorridas vía API (torpedo) | Valentín | ☐ |
| 5 | Video técnico de la entrega 1 (modelo + despliegue + instancia) | Valentín | ☐ |
| 6 | Video para el emprendedor (qué hará el sistema, sin tecnicismos) | Valentín | ☐ |
| 7 | Tag `entrega-1` en el repositorio | Valentín | ☐ |

## Avances de la sesión

- Mono-repo estructurado (bpmn/, web/, ws-pedidos/, worker/, docs/, actas/).
- Modelo BPMN de referencia completo (`bpmn/venta-mapuescuela.bpmn`) con: 6 user tasks, 4 external
  worker tasks, boundary timer interruptor de 24 h parametrizado, 4 gateways exclusivos con flujos
  default seguros y 5 eventos de fin diferenciados.
- Diccionario de elementos, variables, topics y mapeo de los 9 estados del pedido.
- 8 decisiones de arquitectura documentadas.
- Torpedo de la API REST de Flowable adaptado al proceso (`docs/flowable-api.http`).

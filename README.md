# Mapuescuela — Sistema de ventas con BPMN + Flowable

Proyecto de servicio disciplinar del ramo *Integración de Plataformas* (Iplacex).

[Mapuescuela](https://www.instagram.com/mapuescuela) es una agrupación de Padre Hurtado que hace
*educa-acción para el buen vivir*: talleres de telar mapuche, yoga, fitopreparados y preparación de la
PAES. Parte de lo que financia esos talleres viene de vender lo que le donan — muebles, libros,
juguetes. Hoy lo venden por Instagram y WhatsApp, y lo anotan en un cuaderno.

Esto es un MVP para publicar ese catálogo y llevar las ventas, con el **proceso de venta modelado en
BPMN y corriendo en Flowable**.

> **Para levantarlo:** [`docs/instalacion.md`](docs/instalacion.md).
> **Para usarlo:** [`docs/manual.md`](docs/manual.md).

---

## Cómo está armado

Cuatro piezas, siguiendo el patrón que enseña el curso: la web llama al motor, el motor publica los
trabajos automáticos, y un worker los toma y llama al web service Java.

```
   web/ (Python)  ──── REST ────▶  FLOWABLE  ────▶  worker/  ────▶  ws-pedidos/ (Java)
        │                         (motor BPMN)                              │
        │                                                                   ▼
        └──────────── catálogo, pedidos y la agrupación ────────────▶    H2 (archivo)
```

Tres ideas ordenan el diseño:

- **El motor es la fuente de la verdad.** Cada pedido guarda el id de su instancia y el estado se lo
  pregunto a Flowable, en vez de llevar un estado propio en paralelo.
- **Las tareas automáticas son external workers.** El motor publica el trabajo y el worker lo toma.
  Eso permite escribir el worker en Python aunque el motor sea Java, y si el worker se cae el proceso
  no se rompe: los trabajos quedan esperando.
- **El navegador conoce una sola dirección.** Todo pasa por la web, incluidas las fotos de los
  objetos: `ws-pedidos` nunca se expone al cliente.

## Qué hay en cada carpeta

| Carpeta | Qué contiene |
|---|---|
| `bpmn/` | Los dos modelos: cómo venden hoy y el proceso automatizado que se despliega |
| `web/` | La aplicación: catálogo, checkout, seguimiento, bandeja de tareas y administración |
| `ws-pedidos/` | El web service REST en Java, que es lo que exige el curso |
| `worker/` | El external worker que consume los trabajos automáticos del motor |
| `docs/` | Instalación, manual de uso, decisiones de arquitectura y pruebas |
| `actas/` | Bitácora de avances, una por sesión de trabajo |

## El proceso

El cliente reserva desde el catálogo, tiene 24 horas para transferir y subir el comprobante, una
voluntaria revisa el pago, el sistema descuenta el inventario y el pedido se entrega por retiro o por
despacho.

El modelo tiene **seis finales distintos**: tres son ventas cerradas —retirado, despachado por
voluntario, despachado por courier— y tres son las formas de perderla —el pago no aprobado, el plazo
vencido y el objeto que ya se llevó otra persona. Que el proceso distinga entre ellos es lo que
permite saber después *por qué* se cayó un pedido.

Los seis se recorrieron desde la interfaz y están documentados en
[`docs/pruebas-de-escenarios.md`](docs/pruebas-de-escenarios.md), con una sola consulta al historial
del motor como evidencia. El detalle del modelo está en [`bpmn/README.md`](bpmn/README.md).

## Qué puede hacer la agrupación

Sin que nadie toque el código ni recompile nada:

- Cargar objetos al catálogo, con foto, y ver cómo va a quedar la ficha mientras la escribe.
- Editar o retirar un objeto. Retirar no borra: los pedidos viejos siguen apuntando a él.
- Resolver las tareas de cada pedido desde la bandeja, con el paso siguiente encadenado.
- Revisar un comprobante y aprobar o rechazar, con la decisión firmada por quien entró.
- Editar sus propios datos, incluida la cuenta bancaria que el cliente lee para transferir.
- Mirar el histórico: cuántas ventas se cerraron, cuánto se recaudó y qué se perdió.

## Documentación

| Archivo | Qué responde |
|---|---|
| [`docs/instalacion.md`](docs/instalacion.md) | Cómo levantar las cuatro piezas desde cero |
| [`docs/manual.md`](docs/manual.md) | Cómo se usa, escrito para la agrupación |
| [`docs/README.md`](docs/README.md) | Las decisiones de arquitectura, una por una |
| [`docs/pruebas-de-escenarios.md`](docs/pruebas-de-escenarios.md) | Los seis caminos y su evidencia |
| [`docs/flowable-api.http`](docs/flowable-api.http) | Peticiones listas contra la API del motor |
| [`bpmn/README.md`](bpmn/README.md) | El modelo, sus tareas y sus topics |

Sobre cómo se usaron herramientas de IA en este proyecto —qué se les pidió, cómo se verificó y qué
decisiones no las siguieron— está el **ADR-010** en [`docs/README.md`](docs/README.md).

## Autor

Valentín González. Trabajo individual, autorizado por el profesor.

# Mapuescuela — Sistema de Ventas con BPMN + Flowable

Proyecto de **servicio disciplinar** de la asignatura *Integración de Plataformas* (Iplacex).

**Caso real:** [Mapuescuela](https://www.instagram.com/mapuescuela) es una agrupación sin fines de
lucro que apoya a niños, niñas y jóvenes en situación de deserción escolar. Se financia, en parte,
vendiendo artículos usados donados por la comunidad (libros, muebles, juguetes). Hoy esa venta es
manual; este proyecto construye un **MVP funcional** para publicar el catálogo y gestionar las
compras, con el **proceso de venta modelado en BPMN y automatizado con Flowable**.

## Arquitectura

Sigue el patrón de referencia del curso (web → Flowable REST → external workers → web service Java):

```
┌────────────────┐  inicia proceso /       ┌─────────────────────┐
│  web/          │  completa user tasks    │  FLOWABLE           │
│  Python        │ ───────── REST ───────▶ │  (motor BPMN)       │
│  FastAPI       │                         │  :8080/flowable-rest│
└──────┬─────────┘                         └──────────┬──────────┘
       │                                              │ external worker jobs
       │ catálogo / pedidos                           │ (por topic)
       ▼                                   ┌──────────▼──────────┐
┌────────────────┐                         │  worker/            │
│  SQL SERVER    │ ◀── CRUD de dominio ─── │  External Worker    │
│  (negocio)     │      vía ws-pedidos     │  → llama ws-pedidos │
└────────────────┘                         └──────────┬──────────┘
       ▲                                              │
       └───────────────┌────────────────┐ ◀──────────┘
                       │  ws-pedidos/   │
                       │  Java (JAX-RS  │   ← Web Service REST en Java
                       │  Jersey) :9090 │     (contenido core del curso)
                       └────────────────┘
```

- **El motor es la fuente de la verdad del flujo:** cada pedido guarda su `processInstanceId` y el
  estado se deriva de la instancia de proceso (en qué actividad está el token).
- Las tareas automáticas del proceso son **External Worker Tasks** (por topic); el worker invoca al
  web service Java, que es quien escribe los hechos de negocio en la base de datos.

## Estructura del repositorio (mono-repo)

| Carpeta | Contenido |
|---|---|
| `bpmn/` | Modelo BPMN del proceso de venta + diccionario de elementos |
| `web/` | Aplicación web (Python + FastAPI): catálogo, carrito, checkout, seguimiento, panel |
| `ws-pedidos/` | Web service REST de dominio (Java + Jersey + Gradle) |
| `worker/` | External Worker (consume topics del proceso e invoca al WS) |
| `docs/` | Decisiones de arquitectura (ADRs) y guía de la API REST de Flowable |
| `actas/` | Actas de reuniones / bitácora semanal de avances |

## Proceso de negocio (resumen)

Venta de un artículo: el cliente compra desde el catálogo → el sistema genera el pedido e informa
los datos bancarios → el cliente tiene **24 horas** para transferir y adjuntar el comprobante (si no,
el pedido **se cancela automáticamente** por un temporizador BPMN) → un voluntario **revisa el
comprobante** y aprueba o rechaza → si aprueba, se **descuenta el inventario** y el pedido pasa a
preparación → se entrega por **retiro** (Padre Hurtado) o **despacho** → el pedido finaliza.

Detalle completo del modelo: [`bpmn/README.md`](bpmn/README.md).

## Roadmap de entregas

| Entrega | Alcance |
|---|---|
| **1** | Modelo BPMN en Flowable Design + despliegue al motor + instancia demo recorriendo user tasks |
| **2** | Camino feliz completo: checkout → comprobante → revisión → worker descuenta stock (WS Java) |
| **3** | Timer 24 h + rechazo + anti-sobreventa + retiro/despacho + catálogo y panel usables |
| **Examen** | Migración a Flowable open source, pulido y demostración de los 3 escenarios |

## Autor

Valentín González — trabajo individual (autorizado por el profesor).
Desarrollado con apoyo de IA, entendiendo y validando cada decisión (según lineamientos del curso).

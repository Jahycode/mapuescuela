# Mapuescuela — Sistema de ventas con BPMN + Flowable

Proyecto de servicio disciplinar del ramo *Integración de Plataformas* (Iplacex).

[Mapuescuela](https://www.instagram.com/mapuescuela) es una agrupación sin fines de lucro que apoya a
niños y jóvenes en situación de deserción escolar. Parte de su financiamiento viene de vender
artículos usados que le donan: libros, muebles, juguetes. Hoy venden por Instagram y WhatsApp, y
anotan todo en un cuaderno. Lo que estoy construyendo es un MVP para publicar el catálogo y manejar
las compras, con el **proceso de venta modelado en BPMN y corriendo en Flowable**.

## Cómo está armado

Sigo el patrón que enseña el curso: la web llama a Flowable, Flowable publica trabajos automáticos, y
un worker los toma y llama al web service Java.

```
   web/ (Python)  ──── REST ────▶  FLOWABLE  ────▶  worker/  ────▶  ws-pedidos/ (Java)
        │                          (motor BPMN)                            │
        │                                                                  ▼
        └──────────────── consulta catálogo y pedidos ────────────▶   SQL Server
```

Dos ideas que ordenan todo el diseño:

- **El motor es la fuente de la verdad.** Cada pedido guarda el id de su instancia y el estado se lo
  pregunto a Flowable, en vez de llevar un estado propio en paralelo.
- **Las tareas automáticas son external workers.** El motor publica el trabajo y el worker lo toma.
  Eso me deja escribir el worker en Python aunque el motor sea Java.

## Qué hay en cada carpeta

| Carpeta | Qué contiene |
|---|---|
| `bpmn/` | Los modelos BPMN del proceso de venta (el actual y el automatizado) |
| `web/` | La aplicación web: catálogo, carrito, checkout, seguimiento y panel del voluntario |
| `ws-pedidos/` | El web service REST en Java, que es lo que exige el curso |
| `worker/` | El external worker que consume los trabajos del motor |
| `docs/` | Mis decisiones de arquitectura y la guía de la API REST de Flowable |
| `actas/` | Bitácora de avances |

## El proceso en una línea

El cliente compra desde el catálogo, tiene 24 horas para transferir y subir el comprobante (si no, el
pedido se cancela solo), un voluntario revisa el pago, se descuenta el inventario y el pedido se
entrega por retiro o por despacho.

El detalle está en [`bpmn/README.md`](bpmn/README.md).

## Plan de entregas

| Entrega | Qué tiene que estar listo |
|---|---|
| **1** | Los dos modelos BPMN, el proceso desplegado en el motor y una instancia recorriendo tareas |
| **2** | Camino feliz completo: checkout → comprobante → revisión → el worker descuenta stock |
| **3** | El timer, el rechazo, el quiebre de stock, retiro/despacho y el catálogo usable |
| **Examen** | Migración a Flowable open source y demostración de los tres escenarios |

## Autor

Valentín González. Trabajo individual, autorizado por el profesor.

# Acta 20 — Narrar el sistema en voz alta encontró lo que ninguna prueba había encontrado

- **Fecha:** domingo 13 de septiembre de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Cerré el examen. Grabé los dos videos y quedaron los últimos arreglos: el histórico se puede filtrar
por período, la voluntaria ve el comprobante antes de aprobar un pago, y el catálogo dejó de tardar
cuatro segundos en cargar. Lo importante de la sesión, sin embargo, no es ninguna de esas tres: es que
preparar la grabación destapó que cinco textos de la interfaz prometían algo que el sistema nunca hizo.

## Lo que hice

### El filtro del histórico

`/bandeja/historico` mostraba todos los pedidos cerrados desde siempre. Con cien ventas esa pantalla no
responde la pregunta que la agrupación tiene, que es cuánto se vendió este mes.

El desplegable se arma desde los datos: solo aparecen los meses que de verdad tienen pedidos cerrados,
agrupados por año. **Descarté un rango de fechas libre** porque permite elegir períodos vacíos y obliga
a escribir. Mes y año viajan en **un solo parámetro** y no en dos selectores encadenados: `2026-09` y
`2026` son los dos prefijos de la misma marca ISO, así que el mismo `startswith` resuelve ambos casos.
El valor se valida contra la lista antes de usarse, porque un `?periodo=hola` llega a `int("a")` y
devuelve un 500.

Las tres cifras de arriba —ventas, recaudado, perdidos— se calculan sobre lo filtrado. Era el punto del
cambio; un filtro que no mueve los totales solo esconde filas.

### El comprobante a la vista

La pantalla de revisión mostraba quién pagó, cuánto y qué llevaba, pero **no el comprobante**. La
voluntaria aprobaba una transferencia sin verla.

El web service ya servía la imagen desde la Entrega 2, en `GET /pedidos/{id}/comprobante`; faltaba solo
el proxy y el panel. La dirección quedó en `/bandeja/pedido/<id>/comprobante` y no en
`/pedido/<id>/comprobante`: **colgándola de `/bandeja` la cubre la guarda por prefijo que ya existía**,
sin escribir ninguna regla nueva. Un comprobante lleva el banco y la cuenta de una persona, y los
números de pedido son correlativos.

### Cuatro segundos que no eran de mi código

El catálogo tardaba en cargar. Lo medí en vez de suponerlo: **4,14 s la pantalla, 0,21 s el web
service**. La diferencia no estaba en el código.

`localhost` resuelve en Windows a dos direcciones y entrega primero `::1`, la de IPv6. `ws-pedidos`
escucha solo en IPv4. Así que `requests` intentaba por IPv6, esperaba dos segundos, se rendía y recién
entonces probaba por IPv4. Dos llamadas por pantalla, cuatro segundos. La misma petición medida de las
dos formas: **2,061 s contra 0,004 s**.

Podía arreglarlo del lado del servidor, haciendo que Java escuchara también en IPv6, pero eso pedía
recompilar. **Cambié el cliente**: el valor por defecto de `WS_PEDIDOS` pasó de `localhost` a
`127.0.0.1` en la web, el worker y el `.env.example`, y la pantalla quedó en 0,02 s. Flowable no sufría
el problema porque Docker publica el puerto en las dos familias, y `curl` tampoco, porque prueba las dos
direcciones en paralelo mientras que `requests` las prueba en fila.

### Los dos videos

Escribí los dos guiones y grabé. El de la agrupación es un demo-tutorial, que es lo que la rúbrica pide
ahora en vez de un pitch. El técnico va como un recorrido —catálogo, llave, bandeja, administración y al
final el web service— y no como una sección por criterio: **descarté el orden de la rúbrica** porque
obligaba a saltar entre pantallas. Lo que ya sustenté en la Entrega 3 va nombrado y mostrado, no
explicado de nuevo.

## Error encontrado

Probando el catálogo reservé un velador y me quedé mirando la pantalla:

> ¿Por qué el objeto que acabo de reservar sigue apareciendo en el catálogo?

Porque reservar no lo saca. El `UPDATE producto SET stock = stock - 1` lo ejecuta el worker cuando la
voluntaria **aprueba el pago**, no cuando alguien reserva. Eso está a propósito, y es la razón de que
exista el final `SIN_STOCK`: dos personas pueden pedir lo mismo y se lo lleva quien pague primero.

El problema era que la interfaz decía lo contrario. La página del pedido prometía *«nadie más los puede
comprar mientras corra el plazo»*, y la misma promesa estaba repetida en la celda de reserva del
catálogo y en tres textos del checkout. Cinco lugares afirmando algo que el sistema nunca hizo.

Evalué cambiar el modelo para que reservar sí apartara el objeto, y lo descarté: **dejaría `SIN_STOCK`
inalcanzable**, un camino del diagrama al que ya nadie llegaría. Corregí los textos.

Lo que queda: **leer el sistema en voz alta es una forma de probarlo.** Encontré los cinco textos
porque tuve que narrarlos frente a la cámara, y ahí escuché que estaba afirmando algo que sabía que era
falso. Ninguna prueba automática iba a detectarlo, porque el código hacía exactamente lo que debía; la
que mentía era la frase.

## Cierre

El examen queda entregado. Lo que cambió esta etapa no fue el motor ni la integración, que estaban desde
la entrega pasada: fue que la agrupación puede operar el sistema sin mí. Y me llevo que las tres formas
en que encontré problemas estas semanas —consultar la base, medir y tener que explicarlo— son las tres
que ninguna prueba escrita por mí hacía.

## Estado del Examen

| Criterio | Estado |
|---|---|
| MVP y valor de negocio (25) | ✅ funcional, administrable y con guía de instalación |
| Ejecución integral del proceso en Flowable (15) | ✅ seis finales recorridos y documentados |
| Integración de web services y base de datos (15) | ✅ veintidós endpoints sobre ocho tablas |
| Interfaces de usuario y experiencia (15) | ✅ nueve pantallas con identidad propia |
| Uso de IA y tecnologías complementarias (5) | ✅ ADR-010, apuntado desde el README y sustentado en el video |
| Documentación, repositorio y entregables (10) | ✅ instalación, manual de uso y 57 commits |
| Video demo para la emprendedora (8) | ✅ demo-tutorial grabado |
| Sustentación técnica para el profesor (7) | ✅ grabado, con uso de IA y desafíos técnicos |

# Acta 19 — Escribir cómo se instala fue lo que destapó que estaba mal configurado

- **Fecha:** sábado 12 de septiembre de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

Cerré las dos cosas que faltaban fuera del proceso: la bandeja dejó de estar abierta a quien tuviera
el link, y el proyecto tiene por fin un manual de instalación y uno de uso. Lo interesante es que
sentarme a escribir cómo se levanta el sistema sacó a la luz cuatro errores de configuración que
llevaban semanas ahí sin que nada fallara.

## Lo que hice

### La llave

`/bandeja` y `/admin` piden clave. Tres voluntarias con la suya, escritas en `app.py`, y la sesión de
Flask guardando quién entró.

**No es un sistema de autenticación y lo dejé anotado en el código**: sin hash, sin roles, sin
recuperación. Es una llave para que la pantalla que aprueba transferencias no quede abierta. El
profesor dijo que no gastáramos tiempo en un login, y saber qué estoy dejando fuera vale más que no
haberlo pensado — cambiarlo por una tabla de usuarios sería reemplazar ese diccionario y la línea que
compara.

**La guarda va por prefijo, en un solo `before_request`.** Son catorce rutas internas; con un
decorador por función habría que acordarse en cada una, y la que agregue mañana quedaría abierta sin
que nadie se entere. Probé que los `POST` también rebotan: esconder los botones no sirve de nada si
el formulario se puede enviar a mano.

El parámetro que recuerda a dónde ibas se valida antes de redirigir. Lo escribe quien quiera, y con
un `https://` llevaría a otro sitio después de identificarte, con la confianza de venir de mi página.
Lo comprobé con tres destinos: los dos externos caen a la bandeja y solo la ruta local pasa.

Lo que gana el sistema no es la protección, es la firma: antes cualquiera elegía un nombre de un
desplegable y aprobaba un pago con él. Ahora `revision.revisor` guarda a quien tiene la clave.

### Los dos manuales

`docs/instalacion.md` levanta las cuatro piezas desde cero, con versiones, comandos y qué línea hay
que esperar en cada una. Incluye el comando con que se creó el contenedor de Flowable, **que no
estaba escrito en ninguna parte**: lo recuperé con `docker inspect` en vez de reconstruirlo de
memoria.

De ahí salió un aviso que vale la pena: el contenedor se creó sin volumen, así que el historial del
motor vive adentro suyo. Sobrevive a `docker stop`, pero `docker rm` se lleva la evidencia de las
pruebas y no hay de dónde recuperarla.

`docs/manual.md` es para la agrupación y no menciona una sola vez la palabra «instancia». Explica la
bandeja, cómo revisar un pago, qué pasa solo —el plazo, el descuento de inventario— y qué hacer
cuando algo se ve raro.

### El README dejó de mentir

Decía que la base era SQL Server, hablaba de un carrito que descarté hace meses y su plan de entregas
daba por pendiente la migración a open source, que ya estaba hecha. Ese plan lo reemplacé por lo que
la agrupación puede hacer hoy, que es lo que el criterio del MVP pregunta.

El ADR-005 **no lo reescribí**: quedó marcado como superado por H2, con el motivo. Un ADR registra lo
que decidí entonces; cambiarle el texto borraría que la decisión cambió, que es justamente lo que
vale la pena mostrar.

## Error encontrado

Escribiendo la tabla de variables de entorno del manual fui a verificar los valores por defecto, y
encontré esto en `flowable_client.py`:

```python
PLAZO_PAGO = os.environ.get("PLAZO_PAGO", "PT2M")
```

**El plazo por defecto eran dos minutos.** Quedó de las pruebas del temporizador de la Entrega 3.
Sin exportar nada, cualquier pedido se cancelaba solo a los dos minutos — grabando un video, eso
habría pasado en medio de la demostración.

Tirando de ahí salieron tres más. `python-dotenv` estaba en los dos `requirements.txt`, el
`.env.example` decía «copiar a `.env`», y **ningún archivo llamaba a `load_dotenv()`**: ese archivo
no lo leía nadie y las variables solo funcionaban exportadas a mano en la terminal, que es como
veníamos haciéndolo sin darnos cuenta. Las credenciales del motor seguían escritas en dos archivos. Y
el `.env.example` nombraba `WS_PEDIDOS_URL` cuando el código lee `WS_PEDIDOS`, más cuatro variables
de SQL Server y cinco de datos bancarios que ya no existen.

Ninguna de las cuatro hacía fallar nada. Los valores por defecto tapaban el problema, y el archivo de
configuración describía un sistema que no era el mío.

Lo que queda: **escribir la documentación es una forma de probar el proyecto.** Ninguna prueba mía
iba a encontrar esto, porque todas corrían con el sistema ya configurado por mí. Lo encontró tener
que explicarle a otro cómo configurarlo.

## Pendientes y decisiones

- **Las claves quedan en `app.py`**, que es exactamente lo que venía señalando como problema en
  `worker/config.py`. La diferencia es que son de demostración y está anotado; igual conviene
  nombrarlo en el video antes de que lo pregunten.
- Quedan dos objetos de prueba retirados en el catálogo y la cuenta bancaria vacía. Hay que limpiarlos
  antes de grabar.
- **Conviene recorrer los seis caminos otra vez.** La evidencia documentada es del acta 15 y desde
  entonces cambiaron la interfaz, la persistencia de los desenlaces y el orden de los pasos.

## Cierre

Lo que queda del examen ya no es construir. El sistema hace lo que tiene que hacer, la agrupación
puede operarlo sin mí, y ahora hay dos documentos que explican cómo levantarlo y cómo usarlo. Faltan
los dos videos, y uno de ellos tiene que contar algo que hasta hoy estaba escrito pero escondido: cómo
se usaron las herramientas de IA en todo esto.

## Estado del Examen

| Criterio | Estado |
|---|---|
| MVP y valor de negocio (25) | ✅ funcional, administrable y con guía de instalación |
| Ejecución integral del proceso en Flowable (15) | ✅ |
| Integración de web services y base de datos (15) | ✅ |
| Interfaces de usuario y experiencia (15) | ✅ |
| Uso de IA y tecnologías complementarias (5) | ◐ el ADR-010 ya se apunta desde el README; falta en el video |
| Documentación, repositorio y entregables (10) | ✅ instalación, manual de uso y repositorio al día |
| Video demo para la emprendedora (8) | ☐ |
| Sustentación técnica para el profesor (7) | ☐ |

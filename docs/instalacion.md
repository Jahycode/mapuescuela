# Cómo levantar Mapuescuela

Son cuatro piezas y hay que encenderlas en orden: el motor, el web service, el worker y la web.
Si el motor no está arriba, la web no puede crear pedidos; si el web service no está, el worker
falla al descontar inventario.

La primera vez toma unos veinte minutos, casi todos esperando descargas. Después, levantarlo
completo son cuatro comandos.

---

## Lo que hace falta tener instalado

| | Versión | Para qué |
|---|---|---|
| **Docker Desktop** | cualquiera reciente | Corre el motor de Flowable |
| **Java (JDK)** | 24 o superior | Compila y corre `ws-pedidos` |
| **Python** | 3.12 o superior | Corre la web y el worker |

Gradle **no** hace falta instalarlo: el proyecto trae su propio *wrapper* y lo descarga solo la
primera vez.

---

## 1 · El motor de Flowable

Se usa la imagen oficial de la versión **open source**, sin licencia. Una sola vez:

```
docker run -d --name flowable -p 8080:8080 flowable/flowable-rest
```

De ahí en adelante, cada vez que enciendas el computador:

```
docker start flowable
```

Tarda cerca de un minuto en responder. Para comprobar que está listo:

```
curl -u rest-admin:test http://localhost:8080/flowable-rest/service/repository/deployments
```

El usuario `rest-admin` y la clave `test` vienen por defecto en esa imagen.

No uses docker rm. El contenedor se creó sin volumen, así que todo lo que el motor sabe vive adentro suyo: los procesos que corrieron, el historial, la evidencia de las pruebas. Con docker stop no pasa nada, al prenderlo de nuevo sigue todo ahí. Pero borrarlo se lleva eso y no hay de dónde recuperarlo.

### Desplegar el proceso

Con el motor arriba, hay que subirle el modelo una vez. Está en `bpmn/ventaMapuescuela.bpmn` y se
sube con el bloque 1 de `docs/flowable-api.http`, que se ejecuta con la extensión *REST Client* de
VS Code. Para comprobar que quedó:

```
curl -u rest-admin:test "http://localhost:8080/flowable-rest/service/repository/process-definitions?key=ventaMapuescuela"
```

---

## 2 · El web service de dominio

```
cd ws-pedidos
.\gradlew.bat run
```

La primera vez descarga Gradle y las dependencias. **Esperar a que diga Tablas listas.** antes de
seguir: esa línea confirma que creó las ocho tablas en H2.

Si la base está vacía, además vas a ver:

```
Catálogo inicial cargado: 10 objetos.
Datos de la agrupación cargados. La cuenta va vacía.
```

La base es un archivo en `ws-pedidos/data/pedidos.mv.db`. **H2 acepta un solo proceso a la vez**, así
que no puedes tener dos `ws-pedidos` corriendo ni abrir la consola de H2 mientras el servicio está
levantado.

Queda escuchando en `http://localhost:9090`.

---

## 3 · El worker

En otra terminal:

```
cd worker
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python worker.py
```

Las tres líneas del medio son solo la primera vez. Queda preguntándole al motor cada tres segundos si
hay trabajo automático pendiente. **Si se cae, el proceso no se rompe**: los trabajos quedan en la
cola esperando a que vuelva.

---

## 4 · La web

En una cuarta terminal:

```
cd web
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Queda en `http://localhost:5000`.

---

## Cómo se entra

| Dirección | Quién |
|---|---|
| `http://localhost:5000` | El catálogo, abierto a cualquiera |
| `http://localhost:5000/bandeja` | Las tareas de la agrupación, pide clave |

Las claves de demostración están en `web/app.py`, en el diccionario `VOLUNTARIAS`. Son el nombre en
minúscula: `ana`, `diego`, `rosa`. Es un login simple hardcodeado.

---

## Variables de entorno

Ninguna es obligatoria: todas tienen un valor por defecto que sirve para correr en un computador.
Se copian de `.env.example` a `.env` cuando hace falta cambiarlas.

| Variable | Por defecto | Cuándo se cambia |
|---|---|---|
| `WS_PEDIDOS` | `http://localhost:9090` | Si el web service corre en otra parte |
| `FLOWABLE_BASE_URL` | `http://localhost:8080/flowable-rest` | Lo mismo con el motor |
| `PLAZO_PAGO` | `PT24H` | `PT2M` para ver el vencimiento en una demostración |
| `SECRET_KEY` | valor de desarrollo | Si esto sale a internet |

---

## Si algo no levanta

| Qué ves | Qué pasa |
|---|---|
| La web muestra «no puedo hablar con el sistema» | `ws-pedidos` está abajo |
| Un pedido se queda pegado en una tarea | El worker está abajo, levantarlo hara que siga solo su tarea |
| `ws-pedidos` no parte y habla de *lock* | Hay otro proceso usando `data/pedidos.mv.db` |
| La bandeja está vacía y deberían haber tareas | El motor está abajo, o el modelo no está desplegado |
| Un pedido se cancela solo a los dos minutos | Quedó `PLAZO_PAGO=PT2M` de una prueba anterior |

---

## Empezar de cero

Para dejar todo como recién instalado:

1. Detener `ws-pedidos`.
2. Borrar `ws-pedidos/data/` y `ws-pedidos/comprobantes/` y `ws-pedidos/fotos/`.
3. Levantarlo de nuevo: recrea las tablas, los diez objetos y los datos de la agrupación.

Eso **no** borra el historial de Flowable. Para limpiar también el motor, el bloque 15b de
`docs/flowable-api.http` borra las instancias vivas.

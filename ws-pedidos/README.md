# ws-pedidos/ — El web service de dominio, en Java

Este es el servicio REST que expone las operaciones de negocio del proceso: consultar pedidos,
crearlos y descontar inventario. Lo hago en **Java** porque el curso lo exige para los web services,
y sigo el mismo patrón del ejemplo `ws-socios` del profesor: Jersey + JAX-RS + Gradle, con un
servidor embebido en el puerto 9090.

Es el único componente que el worker va a llamar cuando el proceso ejecute una tarea automática.

## Cómo correrlo

```
.\gradlew.bat run
```

No hace falta tener Gradle instalado: el *wrapper* que está en la carpeta lo descarga solo.

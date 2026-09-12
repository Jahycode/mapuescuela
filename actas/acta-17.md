# Acta 17 — La aplicación dejó de verse mía y empezó a verse de ellos

- **Fecha:** jueves 10 de septiembre de 2026
- **Participa:** Valentín González (trabajo individual, autorizado por el profesor)

La retroalimentación de la Entrega 2 llegó con 100/100 y una recomendación concreta: incorporar la
identidad gráfica de Mapuescuela —sus colores y su logotipo— para que la aplicación se sienta de la
organización para la que la estoy haciendo. Eso es lo que hice hoy, y en el camino encontré que el
problema más grande de esas pantallas no era el color.

## Lo que hice

### La paleta, sacada del logo

En vez de mirar el logo y elegir colores parecidos, lo abrí y le medí los colores exactos: el azul del aro y de la casa, el verde del cerro y el amarillo que usan en todos sus afiches. Son #3C66AE, #84C084 y #F2C230. El violeta del prototipo se fue entero.

Lo que no tenía previsto es que los grises también había que cambiarlos. Los míos tiraban un poco al violeta cosa que uno no nota hasta que pone otro color al lado y con el azul encima la pantalla se veía sucia. Los reemplacé por grises con un dejo de azul, y recién ahí la paleta se vio limpia.

Después revisé que todo se pudiera leer. Hay una forma estándar de medir cuánto destaca un texto sobre su fondo, y el mínimo para que se lea sin esfuerzo es 4,5. El texto sobre las tarjetas da 15,9 y el blanco sobre los botones azules da 7,5, así que van holgados. El verde y el amarillo del logo no llegan ni a 2: sobre blanco casi no se ven. Por eso quedaron como fondo, como borde o como figura, nunca como letra.

### El sello y el guñelve

El logo va en el encabezado de las cinco pantallas internas, y el guñelve la estrella de ocho puntas
del centro quedó como marca de agua de la portada y como viñeta de cada título de sección.

Los dibujé con `mask` y un SVG en un *data URI*, no como imágenes. La diferencia práctica es que
toman el color de un token: la estrella es amarilla porque hereda `--mostaza`, y si mañana cambia ese
valor cambia sola. Con un `<img>` habría que reexportar el archivo.

### La navegación

Las secciones internas eran cuatro botones amarillos en el encabezado. Los pasé a enlaces de texto,
con la actual marcada, y dejé el amarillo solo para los botones que hacen algo.

La regla que lo ordena es que **navegar no es actuar**: con cuatro botones iguales, «Ver el
histórico» pesaba lo mismo que «Aprobar el pago» y el color dejaba de significar algo. La marca de la
sección actual sale de `aria-current="page"`, así que lo visual y lo que anuncia un lector de
pantalla no se pueden separar.

Además la saqué a `_nav.html`, incluido por las cuatro pantallas. Había cinco copias de esos enlaces
y ya se estaban desincronizando: el histórico solo ofrecía volver a las tareas.

## Error encontrado

El rediseño volvió en un archivo de 967 KB y mi primera comparación dijo que había perdido 44 clases de las 44 originales. Estuve a punto de devolverlo. Lo que pasaba es que el HTML venía empaquetado dentro de un string de JavaScript, con las comillas escapadas, así que mi comparación estaba leyendo el envoltorio y no la página. Al desempaquetarlo el resultado era el contrario: cero clases perdidas, los ocho formularios intactos y las capas de CSS en orden.

Lo que queda: una medición puede dar un resultado limpio y estar mirando otra cosa. El «44 de 44» no parecía un error de mi script, parecía un rediseño destruido — y las dos hipótesis explicaban igual de bien el número.

## Pendientes y decisiones

La identidad se aplicó a mano en once de las doce pantallas. Solo el catálogo pasó por la herramienta de rediseño; al resto le propagué la paleta y los acentos yo, y salió barato porque todo el color vive en un bloque de variables al principio de cada hoja de estilo. Cambiar ese bloque reestiliza la pantalla entera.

El logo bajó de 390 KB a 114. Venía a 603 píxeles para mostrarse a dos centímetros. También probé quitarle el fondo blanco para que se viera mejor sobre el azul, pero el recorte dejaba un halo en el borde del círculo, así que volví al original.

Los datos que ve el cliente —la dirección, el correo, la cuenta— siguen escritos dentro de tres plantillas. Mientras vivan ahí, cambiar uno exige abrir el código. Eso es lo próximo.

## Cierre

La recomendación del profesor era estética y terminó siendo otra cosa. Ponerle a la aplicación el
logo de una organización real fue lo que hizo visible que llevaba semanas afirmando cosas sobre ella
que yo mismo había escrito. El color se arregla en una tarde; la costumbre de rellenar con datos
plausibles es lo que hay que no repetir.

## Estado del Examen

| Criterio | Estado |
|---|---|
| MVP y valor de negocio (25) | ◐ falta que la agrupación pueda administrar lo suyo |
| Ejecución integral del proceso en Flowable (15) | ✅ |
| Integración de web services y base de datos (15) | ✅ |
| Interfaces de usuario y experiencia (15) | ◐ con identidad propia; faltan las de administración |
| Uso de IA y tecnologías complementarias (5) | ◐ el ADR-010 sigue sin aparecer en el README |
| Documentación, repositorio y entregables (10) | ◐ falta el manual de instalación |
| Video demo para la emprendedora (8) | ☐ |
| Sustentación técnica para el profesor (7) | ☐ |

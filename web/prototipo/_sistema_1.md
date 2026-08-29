# Sistema visual — pegar esto en cada prompt

Bloque para incluir en el prompt de cualquier herramienta que genere una pantalla nueva,
para que todas nazcan del mismo sistema en vez de inventar uno propio.

> **Cambios de esta versión.** Se resolvieron cuatro huecos que aparecieron al alinear las
> tres primeras pantallas: falta de un ancho para pantallas de trabajo, falta del estado
> «vendido», falta de una escala para el rótulo de portada, y falta de las insignias de
> urgencia que usa la bandeja. Los cuatro están abajo. Las tres pantallas existentes ya
> cumplen este documento entero.

---

```
Esta pantalla es parte de un sistema que ya existe. Usa exactamente estos tokens, con
estos nombres. No inventes variantes ni renombres nada.

@layer tokens {
  :root {
    /* ── Superficies ── */
    --paper:#EEEDF3; --card:#FFFFFF; --bed:#E4E0EC;
    --rule:#CFC9DA;  --rule-soft:#E3DFEA;
    --ink:#1D1930;   --ink-2:#5D5670;
    --violeta:#4B2A82; --violeta-hondo:#3A1F68; --violeta-suave:#F7F5FC;
    --mostaza:#E8A81C;

    /* ── Estados: un solo par de nombres para todo el sistema ── */
    --esp-fg:#8A4B10; --esp-bg:#FBEBD5;   /* esperando el pago · reservado · apura */
    --rev-fg:#4B2A82; --rev-bg:#E6E1F3;   /* revisando */
    --apr-fg:#1D6B4A; --apr-bg:#DCEDE3;   /* aprobado · listo */
    --can-fg:#A32718; --can-bg:#FBE3DF;   /* cancelado · atrasado */
    --ven-fg:#5D5670; --ven-bg:#E7E4EE;   /* vendido · encontró casa */

    /* ── Tipografía ── */
    --display:"Bricolage Grotesque","Helvetica Neue",system-ui,sans-serif;
    --body:"Instrument Sans",system-ui,-apple-system,sans-serif;
    --mono:"DM Mono",ui-monospace,"SF Mono",Consolas,monospace;

    --t-micro:.6875rem; --t-sm:.8125rem; --t-base:.9375rem; --t-md:1.0625rem;
    --t-lg:clamp(1.35rem, 1.1rem + .6vw, 1.75rem);
    --t-xl:clamp(1.75rem, 1.3rem + 1.2vw, 2.5rem);
    --t-portada:clamp(2.6rem, 1.9rem + 2.6vw, 4.6rem);

    /* ── Espacio y medidas ── */
    --sp-1:4px; --sp-2:8px; --sp-3:12px; --sp-4:16px;
    --sp-5:20px; --sp-6:24px; --sp-8:32px; --sp-10:40px; --sp-12:48px;

    --radius:2px;
    --wrap:78rem;        /* pantallas del cliente */
    --wrap-ancho:96rem;  /* pantallas de trabajo interno */
  }
}

OJO con la sintaxis: dentro de clamp() y calc(), el + y el - necesitan espacios a
los lados. Escribir 1.1rem+.6vw invalida la declaración completa y el navegador la
descarta en silencio.

El fondo del body lleva una cuadrícula de 24px:
  background-image:
    linear-gradient(to right,  rgba(35,26,63,.05) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(35,26,63,.05) 1px, transparent 1px);
  background-size: 24px 24px;

Sobre fondo violeta la cuadrícula sigue, en blanco al 5,5%.

Organiza el CSS en capas, en este orden y sin agregar capas nuevas:
  @layer reset, tokens, base, layout, components, states, utilities;

Nombres de clase que ya existen y hay que reutilizar, no reinventar:
  .wrap        el contenedor con ancho máximo
  .panel       caja blanca con borde;  .panel__head y .panel__body adentro
  .lbl         etiqueta chica en mayúsculas
  .sub         subtítulo de sección
  .lead        texto secundario, máximo 62ch
  .btn         botón;  .btn--pri (violeta) .btn--sec (borde) .btn--peligro (rojo)
  .insignia    sello del estado
                 del pedido:  --esperando --revisando --aprobado --cancelado --vendido
                 de la tarea: --atrasado (usa --can-*) --apura (usa --esp-*)
  .mono        para números, códigos, montos y fechas

El mostaza es el único acento y se usa como máximo en tres lugares por pantalla.
Siempre con texto oscuro encima, nunca blanco.

Reglas de escritura:
- Español de Chile, tuteo. Nunca "usted".
- Cero jerga técnica en texto visible: nada de "instancia", "endpoint", "token", "proceso".
- Los montos siempre con el separador de miles chileno: $54.500
- Las horas en palabras cuando son un plazo: "Te quedan poco más de veinte horas", no
  "20:11:59". La hora exacta de vencimiento sí va, en cifras: "Vence hoy a las 21:40".
- Cada acción irreversible va acompañada de una frase que explica qué va a pasar.
- Nunca "producto" ni "artículo en stock": son objetos, y cada uno existe uno solo.

Es para pantalla de computador, 1280px o más. Sin versión móvil, pero anchos flexibles
con máximo, nunca medidas fijas en píxeles.

Entrégalo como un HTML autocontenido, con el CSS adentro y sin librerías externas.
```

---

## Decisiones que no se discuten en cada pantalla

**Un solo color por fila o por tarjeta.** Si algo lleva insignia de estado, no lleva
además marcador mostaza. Dos colores en el mismo elemento y ninguno significa nada.

**«Disponible» no lleva insignia.** En un catálogo de stock 1, el sello más común sería
el más inútil. La ausencia de insignia es la disponibilidad.

**Los vendidos no usan la misma tarjeta en gris.** Una tarjeta idéntica pero apagada se
lee como una tienda rota. Van en formato propio, más chico y en una sección aparte.

**Rechazar tiene dos significados y por lo tanto dos botones.** «Pedir otra foto»
mantiene la reserva; «cancelar» libera los objetos. Juntarlos en un botón provoca
liberaciones por error.

**Los plazos se calculan desde una hora que manda el servidor**, nunca desde el reloj del
navegador.

**La fricción va con la consecuencia, no con la frecuencia.** Aprobar un pago es un clic y se
puede deshacer. Cancelar pide texto obligatorio, ver la previa de lo que leerá el cliente, y
una marca de confirmación. Nunca al revés: poner la misma confirmación en las dos hace que la
voluntaria apriete sin leer.

**Todo texto que vaya a leer un cliente se escribe con la previa a la vista**, mostrando el
mensaje tal como va a aparecer en su pantalla, firmado. Escribir a ciegas en un cuadro de
texto produce mensajes que no se entienden.

## Al revisar lo que devuelva cada herramienta

- ¿Usó los nombres de token de arriba, o inventó los suyos?
- ¿Reutilizó `.panel`, `.btn`, `.lbl`, `.insignia`, o creó clases equivalentes con otro nombre?
- ¿El orden de las capas es el del sistema, o le agregó capas propias?
- ¿El tuteo y el tono son los mismos que en las otras pantallas?
- ¿Cada botón que destruye algo explica qué va a pasar?
- ¿Los plazos están en palabras?

Chequeo rápido: el bloque `@layer tokens` de un archivo nuevo debería ser **idéntico
carácter por carácter** al de los tres que ya existen.

## Pantallas del prototipo

Las cinco están alineadas: el bloque `@layer tokens` de todas da el mismo hash, `cd109728`.

| Pantalla | Archivo | Público | Estado |
|---|---|---|---|
| Catálogo | `mapuescuela-catalogo-violeta.html` | cliente | listo |
| Checkout | `mapuescuela-checkout.html` | cliente | listo |
| Seguimiento del pedido (5 estados) | `mapuescuela-seguimiento-violeta.html` | cliente | listo |
| Bandeja de tareas | `mapuescuela-bandeja-voluntaria.html` | voluntaria | listo |
| Resolver tarea (revisar comprobante) | `mapuescuela-resolver-tarea.html` | voluntaria | listo |
| Detalle del objeto | | cliente | pendiente |
| Publicar un objeto (celular) | | voluntaria | pendiente · única que no es de escritorio |

### Componentes propios de una pantalla, no del sistema

Estos nacieron en una pantalla y todavía no se usan en dos. Si aparecen en una tercera,
conviene subirlos al sistema:

- `.umbrales` / `.umbral` — los tres pasos numerados del checkout
- `.previa` / `.recado` — la vista de lo que va a leer el cliente, en resolver tarea
- `.cotejo` — el campo para comparar el monto leído con el esperado
- `.tarea` — la fila de la cola, en bandeja y en resolver tarea (ya está en dos: candidata a subir)

package cl.mapuescuela.pedidos;

import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.HeaderParam;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.PUT;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.io.InputStream;
import java.sql.Connection;
import java.util.List;
import java.util.Map;
import java.util.Set;


@Path("/productos")
public class ProductoResource {

    private static final Set<String> CATEGORIAS = Set.of("muebles", "libros", "juguetes", "otros");
    private static final Set<String> CONDICIONES = Set.of("nuevo", "bueno", "detalles", "restaurar");

    private static final java.nio.file.Path CARPETA_FOTOS = java.nio.file.Path.of("fotos");
    private static final int MAX_BYTES = 5 * 1024 * 1024;

    private static final Map<String, String> EXTENSIONES = Map.of(
        "image/jpeg", "jpg",
        "image/png",  "png"
    );

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Producto> listar(@QueryParam("incluirRetirados") boolean incluirRetirados) throws Exception {
        try (Connection conn = Db.getConnection()) {
            return new PedidoDAO(conn).listarProductos(incluirRetirados);
        }
    }

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response crear(Producto producto) throws Exception {
        String error = revisar(producto);

        if (error != null) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", error))
                           .build();
        }

        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);
            int id = dao.insertarProducto(producto);

            return Response.status(Response.Status.CREATED)
                           .entity(dao.buscarProducto(id))
                           .build();
        }
    }

    @PUT
    @Path("/{id}")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response editar(@PathParam("id") int id, Producto producto) throws Exception {
        String error = revisar(producto);

        if (error != null) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", error))
                           .build();
        }

        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);
            producto.setId(id);

            if (!dao.actualizarProducto(producto)) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el objeto " + id))
                               .build();
            }

            return Response.ok(dao.buscarProducto(id)).build();
        }
    }

    @POST
    @Path("/{id}/retiro")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response retirar(@PathParam("id") int id, Map<String, Boolean> cuerpo) throws Exception {
        Boolean retirado = (cuerpo == null) ? null : cuerpo.get("retirado");

        if (retirado == null) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", "Falta decir si el objeto se retira o se vuelve a publicar"))
                           .build();
        }

        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

            if (!dao.marcarRetirado(id, retirado)) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el objeto " + id))
                               .build();
            }

            return Response.ok(dao.buscarProducto(id)).build();
        }
    }

    @POST
    @Path("/{id}/foto")
    @Consumes(MediaType.WILDCARD)
    @Produces(MediaType.APPLICATION_JSON)
    public Response subirFoto(@PathParam("id") int id,
                              @HeaderParam("Content-Type") String tipo,
                              InputStream cuerpo) throws Exception {

        String limpio = (tipo == null) ? null : tipo.split(";")[0].trim();
        String extension = (limpio == null) ? null : EXTENSIONES.get(limpio);

        if (extension == null) {
            return Response.status(Response.Status.UNSUPPORTED_MEDIA_TYPE)
                           .entity(Map.of("error", "La foto tiene que ser JPG o PNG. Llego: " + tipo))
                           .build();
        }

        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

            if (dao.buscarProducto(id) == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el objeto " + id))
                               .build();
            }

            byte[] contenido = cuerpo.readNBytes(MAX_BYTES + 1);

            if (contenido.length == 0) {
                return Response.status(Response.Status.BAD_REQUEST)
                               .entity(Map.of("error", "La foto llego vacia"))
                               .build();
            }
            if (contenido.length > MAX_BYTES) {
                return Response.status(413)
                               .entity(Map.of("error", "La foto pesa mas de 5 MB"))
                               .build();
            }

            java.nio.file.Files.createDirectories(CARPETA_FOTOS);
            String archivo = "objeto-" + id + "-" + System.currentTimeMillis() + "." + extension;
            java.nio.file.Files.write(CARPETA_FOTOS.resolve(archivo), contenido);

            dao.guardarFoto(id, archivo);

            return Response.status(Response.Status.CREATED)
                           .entity(Map.of("archivo", archivo, "bytes", contenido.length))
                           .build();
        }
    }

    @GET
    @Path("/{id}/foto")
    public Response verFoto(@PathParam("id") int id) throws Exception {
        Producto producto;

        try (Connection conn = Db.getConnection()) {
            producto = new PedidoDAO(conn).buscarProducto(id);
        }

        if (producto == null || producto.getFoto() == null) {
            return Response.status(Response.Status.NOT_FOUND)
                           .entity(Map.of("error", "El objeto " + id + " no tiene foto"))
                           .type(MediaType.APPLICATION_JSON)
                           .build();
        }

        java.nio.file.Path archivo = CARPETA_FOTOS.resolve(producto.getFoto());

        if (!java.nio.file.Files.exists(archivo)) {
            return Response.status(Response.Status.NOT_FOUND)
                           .entity(Map.of("error", "La foto no esta en el disco: " + producto.getFoto()))
                           .type(MediaType.APPLICATION_JSON)
                           .build();
        }

        String tipo = producto.getFoto().endsWith(".png") ? "image/png" : "image/jpeg";

        return Response.ok(java.nio.file.Files.readAllBytes(archivo), tipo).build();
    }

    private static String revisar(Producto p) {
        if (p == null || p.getNombre() == null || p.getNombre().isBlank()) {
            return "El objeto necesita un nombre";
        }
        if (p.getCategoria() == null || !CATEGORIAS.contains(p.getCategoria())) {
            return "Categoria invalida. Las validas son: " + CATEGORIAS;
        }
        if (p.getCondicion() == null || !CONDICIONES.contains(p.getCondicion())) {
            return "Condicion invalida. Las validas son: " + CONDICIONES;
        }
        if (p.getPrecio() <= 0) {
            return "El precio tiene que ser mayor que cero";
        }
        return null;
    }
}
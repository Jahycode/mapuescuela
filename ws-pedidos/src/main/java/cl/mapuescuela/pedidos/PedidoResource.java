package cl.mapuescuela.pedidos;

import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.HeaderParam;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.PUT;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.io.InputStream;
import java.sql.Connection;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Path("/pedidos")
public class PedidoResource {

    private static final Set<String> DESENLACES = Set.of(
        "RECHAZADO", "CANCELADO_VENCIMIENTO", "SIN_STOCK", "RETIRADO",
        "DESPACHADO_COURIER", "DESPACHADO_VOLUNTARIO"
    );

     private static final Map<String, String> MENSAJES = Map.of(
        "PAGO_RECHAZADO", "Revisamos tu comprobante y no pudimos aprobar el pago." + " Tu pedido quedo cancelado.",
        "SIN_STOCK", "Lo sentimos: el articulo se agoto antes de completar tu pedido." + " No se te cobro nada."
    );

        private static final java.nio.file.Path CARPETA_COMPROBANTES = java.nio.file.Path.of("comprobantes");
    private static final int MAX_BYTES = 5 * 1024 * 1024;

    private static final Map<String, String> EXTENSIONES = Map.of(
        "image/jpeg", "jpg",
        "image/png",  "png",
        "application/pdf", "pdf"
    );

    private static final Set<String> DECISIONES = Set.of("APROBADO", "OTRA_FOTO", "CANCELADO");
    


    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Pedido> listar() throws Exception {
        try (Connection conn = Db.getConnection()) {
            return new PedidoDAO(conn).listar();
        }
    }

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response crear(Pedido pedido) throws Exception {
        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

            if (pedido == null || pedido.getClienteEmail() == null || pedido.getClienteEmail().isBlank()) {
                return Response.status(Response.Status.BAD_REQUEST)
                               .entity(Map.of("error", "El email del cliente es obligatorio"))
                               .build();
            }

            List<PedidoItem> items = pedido.getItems();
            if (items == null || items.isEmpty()) {
                return Response.status(Response.Status.BAD_REQUEST)
                               .entity(Map.of("error", "El pedido tiene que llevar al menos un objeto"))
                               .build();
            }

            Set<Integer> vistos = new HashSet<>();
            int total = 0;

            for (PedidoItem item : items) {
                if (!vistos.add(item.getProductoId())) {
                    return Response.status(Response.Status.BAD_REQUEST)
                                   .entity(Map.of("error", "El objeto " + item.getProductoId()
                                                  + " viene repetido, y cada objeto existe uno solo"))
                                   .build();
                }

                Producto producto = dao.buscarProducto(item.getProductoId());
                if (producto == null) {
                    return Response.status(Response.Status.BAD_REQUEST)
                                   .entity(Map.of("error", "El objeto " + item.getProductoId() + " no existe"))
                                   .build();
                }

                item.setNombre(producto.getNombre());
                item.setPrecio(producto.getPrecio());
                total += producto.getPrecio();
            }

            pedido.setMontoTotal(total);
            pedido.setCreado(LocalDateTime.now());
            pedido.setId(dao.insertar(pedido));

            return Response.status(Response.Status.CREATED).entity(pedido).build();
        }
    }
    

    @POST
    @Path("/{id}/descontar-stock")
    @Produces(MediaType.APPLICATION_JSON)
    public Response descontarStock(@PathParam("id") int id) throws Exception {
        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

            if (dao.buscarPorId(id) == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el pedido " + id))
                               .build();
            }

            List<PedidoItem> items = dao.listarItems(id);
            if (items.isEmpty()) {
                return Response.status(Response.Status.CONFLICT)
                               .entity(Map.of("error", "El pedido " + id + " no tiene objetos"))
                               .build();
            }

            boolean stockOk = dao.reservarObjetos(items);
            return Response.ok(Map.of("stockOk", stockOk)).build();
        }
    }

    @POST
    @Path("/{id}/desenlace")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response registrarDesenlace(@PathParam("id") int id, Map<String, String> cuerpo) throws Exception{
        
        String valor = (cuerpo == null) ? null : cuerpo.get("valor");
        String motivo = (cuerpo == null) ? null : cuerpo.get("motivo");

        if (valor == null || !DESENLACES.contains(valor)) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", "Desenlace invalido o ausente: " + valor + ". Los validos son: " + DESENLACES))
                           .build();
        }

        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

           if (!dao.registrarDesenlace(id,valor,motivo)) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el pedido " + id))
                               .build();
            }
            return Response.ok(dao.buscarPorId(id)).build();
        }
    }

    @POST
    @Path("/{id}/notificaciones")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response registrarNotificacion(@PathParam("id") int id, Map<String, String> cuerpo) throws Exception {

        String tipo = (cuerpo == null) ? null : cuerpo.get("tipo");

        if (tipo == null || !MENSAJES.containsKey(tipo)) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", "Tipo invalido o ausente: " + tipo + ". Los validos son: " + MENSAJES.keySet()))
                           .build();
        }

        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);
            Pedido pedido = dao.buscarPorId(id);

            if (pedido == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el pedido " + id))
                               .build();
            }

            String mensaje = MENSAJES.get(tipo);
            boolean creada = dao.insertarNotificacion(id, tipo,pedido.getClienteEmail(), mensaje);
            return Response.status(creada ? Response.Status.CREATED : Response.Status.OK)
                           .entity(Map.of("tipo", tipo, "destinatario", pedido.getClienteEmail(), "mensaje", mensaje, "creada", creada))
                           .build();
        }
    }

    @GET
    @Path("/{id}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarPedido(@PathParam("id") int id) throws Exception {
        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);
            Pedido pedido = dao.buscarPorId(id);

            if (pedido == null) {
            return Response.status(Response.Status.NOT_FOUND)
                        .entity(Map.of("error", "No existe el pedido " + id))
                        .build();
            }
            pedido.setItems(dao.listarItems(id));
            return Response.ok(pedido).build();
        }
    }

    @PUT
    @Path("/{id}/instancia")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response asignarInstancia(@PathParam("id") int id, Map<String, String> cuerpo) throws Exception {

        String processInstanceId = (cuerpo == null) ? null : cuerpo.get("processInstanceId");

        if (processInstanceId == null || processInstanceId.isBlank()) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", "Falta el processInstanceId"))
                           .build();
        }
        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

            if (!dao.asignarInstancia(id, processInstanceId)) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No se pudo asignar la instancia al pedido " + id))
                               .build();                  
            }
            return Response.ok(dao.buscarPorId(id)).build();
        }
    }

    @POST
    @Path("/{id}/comprobante")
    @Consumes(MediaType.WILDCARD)
    @Produces(MediaType.APPLICATION_JSON)
    public Response subirComprobante(@PathParam("id") int id,
                                     @HeaderParam("Content-Type") String tipo,
                                     InputStream cuerpo) throws Exception {

        if (tipo == null) {
            return Response.status(Response.Status.UNSUPPORTED_MEDIA_TYPE)
                           .entity(Map.of("error", "No dijiste que tipo de archivo estas subiendo"))
                           .build();
        }

        String limpio = tipo.split(";")[0].trim();
        String extension = EXTENSIONES.get(limpio);

        if (extension == null) {
            return Response.status(Response.Status.UNSUPPORTED_MEDIA_TYPE)
                           .entity(Map.of("error", "Solo aceptamos una foto JPG o PNG, o un PDF. Llego: " + tipo))
                           .build();
        }

        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

            if (dao.buscarPorId(id) == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el pedido " + id))
                               .build();
            }

            byte[] contenido = cuerpo.readNBytes(MAX_BYTES + 1);

            if (contenido.length == 0) {
                return Response.status(Response.Status.BAD_REQUEST)
                               .entity(Map.of("error", "El comprobante llego vacio"))
                               .build();
            }
            if (contenido.length > MAX_BYTES) {
                return Response.status(413)
                               .entity(Map.of("error", "El comprobante pesa mas de 5 MB"))
                               .build();
            }

            java.nio.file.Files.createDirectories(CARPETA_COMPROBANTES);
            String archivo = "pedido-" + id + "-" + System.currentTimeMillis() + "." + extension;
            java.nio.file.Files.write(CARPETA_COMPROBANTES.resolve(archivo), contenido);

            int comprobanteId = dao.insertarComprobante(id, archivo, limpio, contenido.length);

            return Response.status(Response.Status.CREATED)
                           .entity(Map.of("id", comprobanteId,
                                          "archivo", archivo,
                                          "bytes", contenido.length))
                           .build();
        }
    }

    @GET
    @Path("/{id}/comprobantes")
    @Produces(MediaType.APPLICATION_JSON)
    public Response listarComprobantes(@PathParam("id") int id) throws Exception {
        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

            if (dao.buscarPorId(id) == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el pedido " + id))
                               .build();
            }

            return Response.ok(dao.listarComprobantes(id)).build();
        }
    }

    @GET
    @Path("/{id}/comprobante")
    @Produces(MediaType.WILDCARD)
    public Response verComprobante(@PathParam("id") int id) throws Exception {
        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);
            List<Comprobante> comprobantes = dao.listarComprobantes(id);

            if (comprobantes.isEmpty()) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "El pedido " + id + " no tiene comprobantes"))
                               .build();
            }

            Comprobante ultimo = comprobantes.get(0);
            java.nio.file.Path ruta = CARPETA_COMPROBANTES.resolve(ultimo.getArchivo());

            if (!java.nio.file.Files.exists(ruta)) {
                return Response.status(Response.Status.GONE)
                               .entity(Map.of("error", "El comprobante esta registrado pero el archivo no esta en disco"))
                               .build();
            }

            return Response.ok(java.nio.file.Files.readAllBytes(ruta))
                           .type(ultimo.getTipo())
                           .header("Content-Disposition", "inline; filename=\"" + ultimo.getArchivo() + "\"")
                           .build();
        }
    }

        @POST
    @Path("/{id}/revision")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response registrarRevision(@PathParam("id") int id, Revision revision) throws Exception {

        if (revision == null || revision.getRevisor() == null || revision.getRevisor().isBlank()) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", "Falta el nombre de quien revisa"))
                           .build();
        }

        String decision = revision.getDecision();

        if (decision == null || !DECISIONES.contains(decision)) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", "La decision tiene que ser APROBADO, OTRA_FOTO o CANCELADO. Llego: " + decision))
                           .build();
        }

        if (!decision.equals("APROBADO")
                && (revision.getMensaje() == null || revision.getMensaje().isBlank())) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", "Si no apruebas, tienes que explicarle al cliente que paso"))
                           .build();
        }

        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

            if (dao.buscarPorId(id) == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el pedido " + id))
                               .build();
            }

            revision.setPedidoId(id);
            revision.setRevisadoEn(LocalDateTime.now());
            revision.setId(dao.insertarRevision(revision));

            return Response.status(Response.Status.CREATED).entity(revision).build();
        }
    }

    @GET
    @Path("/{id}/revisiones")
    @Produces(MediaType.APPLICATION_JSON)
    public Response listarRevisiones(@PathParam("id") int id) throws Exception {
        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);

            if (dao.buscarPorId(id) == null) {
                return Response.status(Response.Status.NOT_FOUND)
                               .entity(Map.of("error", "No existe el pedido " + id))
                               .build();
            }

            return Response.ok(dao.listarRevisiones(id)).build();
        }
    }
}

package cl.mapuescuela.pedidos;

import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.sql.Connection;
import java.time.LocalDateTime;
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

    static {
       try (Connection conn = Db.getConnection()) {
            new PedidoDAO(conn).crearTablas();
       }
         catch (Exception e) {
                e.printStackTrace();
         }
    }

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
        if (!dao.existeProducto(pedido.getProductoId())) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", "El producto " + pedido.getProductoId() + " no existe"))
                           .build();          
        }
        if (pedido.getClienteEmail() == null || pedido.getClienteEmail().isBlank()){
            return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Map.of("error", "El email del cliente es obligatorio"))
                        .build();
        }

        if (pedido.getCantidad() <= 0) {
            return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Map.of("error", "La cantidad debe ser mayor que cero, llego "
                                        + pedido.getCantidad()))
                        .build();
        }
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
            Pedido pedido = dao.buscarPorId(id);

        if (pedido == null) {
            return Response.status(Response.Status.NOT_FOUND)
                           .entity(Map.of("error", "No existe el pedido " + id))
                           .build();
        }
        if (!dao.existeProducto(pedido.getProductoId())) {
            return Response.status(Response.Status.NOT_FOUND)
                        .entity(Map.of("error", "El pedido " + id + " apunta al producto "
                                        + pedido.getProductoId() + ", que no existe"))
                        .build();
        }

        boolean stockOk = dao.descontarStock(pedido.getProductoId(), pedido.getCantidad());
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
}

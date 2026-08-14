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
import java.sql.DriverManager;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Path("/pedidos")
public class PedidoResource {

    private static PedidoDAO dao;

    static {
        try {
            Connection conn = DriverManager.getConnection("jdbc:h2:mem:pedidos;DB_CLOSE_DELAY=-1");
            dao = new PedidoDAO(conn);
            dao.crearTablas();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Pedido> listar() throws Exception {
        return dao.listar();
    }

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response crear(Pedido pedido) throws Exception {
        pedido.setCreado(LocalDateTime.now());
        pedido.setId(dao.insertar(pedido));
        return Response.status(Response.Status.CREATED).entity(pedido).build();
    }

    @POST
    @Path("/{id}/descontar-stock")
    @Produces(MediaType.APPLICATION_JSON)
    public Response descontarStock(@PathParam("id") int id) throws Exception {
        Pedido pedido = dao.buscarPorId(id);

        if (pedido == null) {
            return Response.status(Response.Status.NOT_FOUND)
                           .entity(Map.of("error", "No existe el pedido " + id))
                           .build();
        }

        boolean stockOk = dao.descontarStock(pedido.getProductoId(), pedido.getCantidad());
        return Response.ok(Map.of("stockOk", stockOk)).build();
    }
}
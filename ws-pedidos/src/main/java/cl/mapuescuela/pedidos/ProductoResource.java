package cl.mapuescuela.pedidos;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import java.sql.Connection;
import java.util.List;


@Path("/productos")
public class ProductoResource {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Producto> listar() throws Exception {
        try (Connection conn = Db.getConnection()) {
            return new PedidoDAO(conn).listarProductos();
        }
    }   
}

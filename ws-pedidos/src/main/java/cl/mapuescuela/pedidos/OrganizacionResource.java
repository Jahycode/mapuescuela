package cl.mapuescuela.pedidos;

import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.PUT;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.sql.Connection;
import java.util.Map;


@Path("/organizacion")
public class OrganizacionResource {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Organizacion ver() throws Exception {
        try (Connection conn = Db.getConnection()) {
            return new PedidoDAO(conn).buscarOrganizacion();
        }
    }

    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response guardar(Organizacion org) throws Exception {

        if (org == null || org.getNombre() == null || org.getNombre().isBlank()) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error", "La agrupacion necesita un nombre"))
                           .build();
        }

        // Los datos bancarios son opcionales, pero a medias no sirven: con banco y
        // sin numero, un cliente no puede transferir a ninguna parte.
        boolean algunoDeLaCuenta =
               !esVacio(org.getBanco())
            || !esVacio(org.getNumeroCuenta())
            || !esVacio(org.getTipoCuenta())
            || !esVacio(org.getTitular());

        if (algunoDeLaCuenta && (esVacio(org.getBanco()) || esVacio(org.getNumeroCuenta()))) {
            return Response.status(Response.Status.BAD_REQUEST)
                           .entity(Map.of("error",
                                   "Si cargas la cuenta, el banco y el numero son obligatorios"))
                           .build();
        }

        try (Connection conn = Db.getConnection()) {
            PedidoDAO dao = new PedidoDAO(conn);
            dao.actualizarOrganizacion(org);
            return Response.ok(dao.buscarOrganizacion()).build();
        }
    }

    private static boolean esVacio(String texto) {
        return texto == null || texto.isBlank();
    }
}

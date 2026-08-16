package cl.mapuescuela.pedidos;

import jakarta.ws.rs.core.UriBuilder;
import org.glassfish.jersey.grizzly2.httpserver.GrizzlyHttpServerFactory;
import org.glassfish.jersey.server.ResourceConfig;

import java.net.URI;

public class App {

    public static void main(String[] args) {

        URI baseUri = UriBuilder.fromUri("http://localhost/").port(9090).build();

        ResourceConfig config = new ResourceConfig().packages("cl.mapuescuela.pedidos");

        GrizzlyHttpServerFactory.createHttpServer(baseUri, config);

        System.out.println("ws-pedidos escuchando en " + baseUri);
        System.out.println("Prueba: GET " + baseUri + "pedidos");
        System.out.println("Ctrl+C para detener.");
    }
}
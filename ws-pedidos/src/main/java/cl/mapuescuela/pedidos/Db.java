package cl.mapuescuela.pedidos;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class Db {
    
    private static final String URL = "jdbc:h2:mem:pedidos;DB_CLOSE_DELAY=-1";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL);
    }
}
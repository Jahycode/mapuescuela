package cl.mapuescuela.pedidos;

import java.time.LocalDateTime;

public class Comprobante {

    private int id;
    private int pedidoId;
    private String archivo;
    private String tipo;
    private int bytes;
    private LocalDateTime subidoEn;

    // Getters and Setters
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getPedidoId() {
        return pedidoId;
    }

    public void setPedidoId(int pedidoId) {
        this.pedidoId = pedidoId;
    }

    public String getArchivo() {
        return archivo;
    }

    public void setArchivo(String archivo) {
        this.archivo = archivo;
    }

    public String getTipo() {
        return tipo;
    }

    public void setTipo(String tipo) {
        this.tipo = tipo;
    }

    public int getBytes() {
        return bytes;
    }

    public void setBytes(int bytes) {
        this.bytes = bytes;
    }

    public LocalDateTime getSubidoEn() {
        return subidoEn;
    }

    public void setSubidoEn(LocalDateTime subidoEn) {
        this.subidoEn = subidoEn;
    }
}
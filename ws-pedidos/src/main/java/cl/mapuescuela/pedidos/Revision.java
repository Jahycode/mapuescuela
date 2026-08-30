package cl.mapuescuela.pedidos;

import java.time.LocalDateTime;

public class Revision {

    private int id;
    private int pedidoId;
    private String revisor;
    private String decision;
    private Integer montoLeido;
    private String mensaje;
    private LocalDateTime revisadoEn;

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

    public String getRevisor() {
        return revisor;
    }

    public void setRevisor(String revisor) {
        this.revisor = revisor;
    }

    public String getDecision() {
        return decision;
    }

    public void setDecision(String decision) {
        this.decision = decision;
    }

    public Integer getMontoLeido() {
        return montoLeido;
    }

    public void setMontoLeido(Integer montoLeido) {
        this.montoLeido = montoLeido;
    }

    public String getMensaje() {
        return mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }

    public LocalDateTime getRevisadoEn() {
        return revisadoEn;
    }

    public void setRevisadoEn(LocalDateTime revisadoEn) {
        this.revisadoEn = revisadoEn;
    }
}
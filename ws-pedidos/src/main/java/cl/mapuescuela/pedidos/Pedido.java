package cl.mapuescuela.pedidos;

import java.time.LocalDateTime;
import java.util.List;

public class Pedido {

    private int id;
    private String clienteNombre;
    private String clienteEmail;
    private int montoTotal;
    private String modalidadEntrega;
    private String processInstanceId;
    private LocalDateTime creado;
    private String desenlace;
    private String desenlaceMotivo;
    private LocalDateTime desenlaceEn;
    private List<PedidoItem> items;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getClienteNombre() {
        return clienteNombre;
    }

    public void setClienteNombre(String clienteNombre) {
        this.clienteNombre = clienteNombre;
    }

    public String getClienteEmail() {
        return clienteEmail;
    }

    public void setClienteEmail(String clienteEmail) {
        this.clienteEmail = clienteEmail;
    }

    public int getMontoTotal() {
        return montoTotal;
    }

    public void setMontoTotal(int montoTotal) {
        this.montoTotal = montoTotal;
    }

    public String getModalidadEntrega() {
        return modalidadEntrega;
    }

    public void setModalidadEntrega(String modalidadEntrega) {
        this.modalidadEntrega = modalidadEntrega;
    }

    public String getProcessInstanceId() {
        return processInstanceId;
    }

    public void setProcessInstanceId(String processInstanceId) {
        this.processInstanceId = processInstanceId;
    }

    public LocalDateTime getCreado() {
        return creado;
    }

    public void setCreado(LocalDateTime creado) {
        this.creado = creado;
    }

    public Pedido() {
    }

    public String getDesenlace() {
        return desenlace;
    }

    public void setDesenlace(String desenlace) {
        this.desenlace = desenlace;
    }

    public String getDesenlaceMotivo() {
        return desenlaceMotivo;
    }

    public void setDesenlaceMotivo(String desenlaceMotivo) {
        this.desenlaceMotivo = desenlaceMotivo;
    }

    public LocalDateTime getDesenlaceEn() {
        return desenlaceEn;
    }

    public void setDesenlaceEn(LocalDateTime desenlaceEn) {
        this.desenlaceEn = desenlaceEn;
    }

    public List<PedidoItem> getItems() {
        return items;
    }

    public void setItems(List<PedidoItem> items) {
        this.items = items;
    }



}
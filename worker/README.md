# worker/ — External Worker

**Entrega 2.** Consume los jobs de los topics del proceso (`cancelarPedidoVencido`,
`registrarRechazo`, `descontarInventario`, `cancelarPorStock`) contra la API de external worker de
Flowable, e invoca a `ws-pedidos` para ejecutar cada acción. Base: el `external-worker-java` del
ejemplo del curso (Spring Boot + @FlowableWorker).

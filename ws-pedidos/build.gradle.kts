plugins {
    application
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("jakarta.ws.rs:jakarta.ws.rs-api:4.0.0")
    implementation("org.glassfish.jersey.core:jersey-server:4.0.2")
    implementation("org.glassfish.jersey.containers:jersey-container-grizzly2-http:4.0.2")
    implementation("org.glassfish.jersey.inject:jersey-hk2:4.0.2")
    implementation("org.glassfish.jersey.media:jersey-media-json-binding:4.0.2")
    implementation("com.h2database:h2:2.4.240")
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(24)
    }
}

application {
    mainClass = "cl.mapuescuela.pedidos.App"
}

tasks.withType<JavaCompile> {
    options.encoding = "UTF-8"
}
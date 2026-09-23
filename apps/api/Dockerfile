FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /workspace

# 1. Copiar solo el archivo de dependencias y descargarlas
COPY pom.xml .

# 2. Copiar el código fuente y compilar (Solo este paso se ejecutará si cambias código Java)
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 \
	mvn -q -DskipTests clean package

# Imagen final ligera para ejecución
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /workspace/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
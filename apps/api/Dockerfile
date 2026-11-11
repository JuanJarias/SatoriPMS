# Stage 1: Build backend JAR inside container (no host Java/Maven needed)
FROM maven:3.9.6-eclipse-temurin-21 AS build
WORKDIR /app

# Cache dependencies
COPY pom.xml .
RUN mvn dependency:go-offline -B || true

# Build application
COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: Minimal runtime image
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]

package com.satoripms.api.review;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Servicio encargado de extraer en tiempo real las métricas y reseñas reales
 * desde el perfil oficial de Hotel Torre Satori en Google Reviews.
 *
 * Opera en dos niveles complementarios sin inventar ni simular opiniones:
 * 1. Extracción directa en vivo del resumen oficial de Google Travel
 *    (calificación promedio real, total de opiniones y distribución exacta por estrellas).
 * 2. Consulta a la API oficial Google Places API (New) cuando se configura
 *    GOOGLE_PLACES_API_KEY en el entorno, para traer las tarjetas individuales
 *    de comentarios reales publicados por los huéspedes.
 */
@Service
public class GoogleReviewsService {

    private static final Logger log = LoggerFactory.getLogger(GoogleReviewsService.class);

    private static final String DEFAULT_GOOGLE_REVIEWS_URL =
            "https://www.google.com/travel/hotels/entity/CgsIvsf-mZ_-h-fGARAB/reviews?hl=es-CO&gl=co";
    private static final String DEFAULT_GOOGLE_PLACE_ID = "ChIJQRr4FV2zOY4RvqM_8_EfzsY";
    private static final Duration CACHE_TTL = Duration.ofMinutes(15);

    private static final Pattern DS1_PATTERN = Pattern.compile(
            "AF_initDataCallback\\(\\{key:\\s*'ds:1'.*?data:(.*?),\\s*sideChannel:",
            Pattern.DOTALL
    );

    private final ObjectMapper objectMapper;
    private final HttpClient httpClient;

    private final String googleReviewsUrl;
    private final String googlePlacesApiKey;
    private final String googlePlaceId;

    private volatile Map<String, Object> cachedSummary;
    private volatile Instant cachedAt;

    public GoogleReviewsService(
            ObjectMapper objectMapper,
            @Value("${GOOGLE_REVIEWS_URL:" + DEFAULT_GOOGLE_REVIEWS_URL + "}") String googleReviewsUrl,
            @Value("${GOOGLE_PLACES_API_KEY:}") String googlePlacesApiKey,
            @Value("${GOOGLE_PLACE_ID:" + DEFAULT_GOOGLE_PLACE_ID + "}") String googlePlaceId
    ) {
        this.objectMapper = objectMapper;
        this.googleReviewsUrl = (googleReviewsUrl == null || googleReviewsUrl.isBlank())
                ? DEFAULT_GOOGLE_REVIEWS_URL
                : googleReviewsUrl;
        this.googlePlacesApiKey = googlePlacesApiKey == null ? "" : googlePlacesApiKey.trim();
        this.googlePlaceId = (googlePlaceId == null || googlePlaceId.isBlank())
                ? DEFAULT_GOOGLE_PLACE_ID
                : googlePlaceId.trim();
        this.httpClient = HttpClient.newBuilder()
                .followRedirects(HttpClient.Redirect.NORMAL)
                .connectTimeout(Duration.ofSeconds(10))
                .build();
    }

    public Map<String, Object> getSummary(boolean forceRefresh) {
        if (!forceRefresh && cachedSummary != null && cachedAt != null
                && Duration.between(cachedAt, Instant.now()).compareTo(CACHE_TTL) < 0) {
            return cachedSummary;
        }

        synchronized (this) {
            if (!forceRefresh && cachedSummary != null && cachedAt != null
                    && Duration.between(cachedAt, Instant.now()).compareTo(CACHE_TTL) < 0) {
                return cachedSummary;
            }

            Map<String, Object> fresh = fetchLiveFromGoogle();
            this.cachedSummary = fresh;
            this.cachedAt = Instant.now();
            return fresh;
        }
    }

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getReviews(int limit, boolean forceRefresh) {
        Map<String, Object> summary = getSummary(forceRefresh);
        Object raw = summary.get("reviews");
        if (raw instanceof List<?> list) {
            List<Map<String, Object>> typed = (List<Map<String, Object>>) list;
            return typed.stream().limit(Math.max(1, limit)).toList();
        }
        return List.of();
    }

    private Map<String, Object> fetchLiveFromGoogle() {
        String placeName = "Hotel Satori - Sevilla Valle del Cauca";
        Double average = null;
        Integer total = null;
        Map<Integer, Integer> distribution = new LinkedHashMap<>();
        for (int star = 5; star >= 1; star--) {
            distribution.put(star, 0);
        }
        List<Map<String, Object>> reviews = new ArrayList<>();
        String source = "unavailable";
        String errorMessage = null;

        // 1. Consultar resumen real en vivo desde la URL oficial de Google Travel Reviews
        try {
            String urlWithLocale = googleReviewsUrl.contains("hl=")
                    ? googleReviewsUrl
                    : googleReviewsUrl + (googleReviewsUrl.contains("?") ? "&" : "?") + "hl=es-CO&gl=co";

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(urlWithLocale))
                    .timeout(Duration.ofSeconds(15))
                    .header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
                    .header("Accept-Language", "es-CO,es;q=0.9")
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200 && response.body() != null) {
                Matcher matcher = DS1_PATTERN.matcher(response.body());
                if (matcher.find()) {
                    JsonNode root = objectMapper.readTree(matcher.group(1));
                    String parsedName = root.path(0).path(1).asText("");
                    if (!parsedName.isBlank()) {
                        placeName = parsedName;
                    }

                    JsonNode ratingBlock = root.path(0).path(7);
                    JsonNode summaryPair = ratingBlock.path(0);
                    if (summaryPair.isArray() && summaryPair.size() >= 2) {
                        average = summaryPair.get(0).asDouble();
                        total = summaryPair.get(1).asInt();
                        source = "google_travel_live";
                    }

                    JsonNode distArray = ratingBlock.path(1).path(0);
                    if (distArray.isArray()) {
                        for (JsonNode entry : distArray) {
                            if (entry.isArray() && entry.size() >= 3) {
                                int star = entry.get(0).asInt();
                                int count = entry.get(2).asInt();
                                if (star >= 1 && star <= 5) {
                                    distribution.put(star, count);
                                }
                            }
                        }
                    }
                } else {
                    log.warn("No se encontró el bloque ds:1 en la respuesta de Google Travel Reviews.");
                    errorMessage = "No fue posible analizar el resumen en vivo desde Google Reviews.";
                }
            } else {
                log.warn("Respuesta inesperada de Google Travel Reviews: HTTP {}", response.statusCode());
                errorMessage = "Google Reviews respondió con estado HTTP " + response.statusCode() + ".";
            }
        } catch (Exception ex) {
            log.error("Error consultando Google Travel Reviews en vivo", ex);
            errorMessage = "Error de conexión al consultar Google Reviews en vivo: " + ex.getMessage();
        }

        // 2. Si GOOGLE_PLACES_API_KEY está configurada, obtener también las reseñas individuales oficiales
        boolean placesApiConfigured = !googlePlacesApiKey.isBlank();
        if (placesApiConfigured) {
            try {
                String placesUrl = "https://places.googleapis.com/v1/places/" + googlePlaceId + "?languageCode=es";
                HttpRequest placesRequest = HttpRequest.newBuilder()
                        .uri(URI.create(placesUrl))
                        .timeout(Duration.ofSeconds(15))
                        .header("X-Goog-Api-Key", googlePlacesApiKey)
                        .header("X-Goog-FieldMask", "displayName,rating,userRatingCount,reviews")
                        .GET()
                        .build();

                HttpResponse<String> placesResponse = httpClient.send(placesRequest, HttpResponse.BodyHandlers.ofString());
                if (placesResponse.statusCode() == 200 && placesResponse.body() != null) {
                    JsonNode placeJson = objectMapper.readTree(placesResponse.body());
                    if (placeJson.has("displayName") && placeJson.path("displayName").has("text")) {
                        placeName = placeJson.path("displayName").path("text").asText(placeName);
                    }
                    if (placeJson.has("rating")) {
                        average = placeJson.path("rating").asDouble();
                    }
                    if (placeJson.has("userRatingCount")) {
                        total = placeJson.path("userRatingCount").asInt();
                    }

                    JsonNode reviewsNode = placeJson.path("reviews");
                    if (reviewsNode.isArray()) {
                        int idx = 1;
                        for (JsonNode rev : reviewsNode) {
                            Map<String, Object> item = new LinkedHashMap<>();
                            item.put("id", idx++);
                            item.put("authorName", rev.path("authorAttribution").path("displayName").asText("Huésped de Google"));
                            item.put("authorPhotoUrl", rev.path("authorAttribution").path("photoUri").asText(null));
                            item.put("rating", rev.path("rating").asInt(5));
                            String text = rev.path("text").path("text").asText("");
                            if (text.isBlank()) {
                                text = rev.path("originalText").path("text").asText("");
                            }
                            item.put("comment", text);
                            item.put("relativeTime", rev.path("relativePublishTimeDescription").asText(""));
                            item.put("createdAt", rev.path("publishTime").asText(""));
                            item.put("source", "google");
                            reviews.add(item);
                        }
                    }
                    source = "google_places_api";
                    errorMessage = null;
                } else {
                    log.warn("Google Places API respondió HTTP {}: {}", placesResponse.statusCode(), placesResponse.body());
                    errorMessage = "Google Places API respondió HTTP " + placesResponse.statusCode() + ".";
                }
            } catch (Exception ex) {
                log.error("Error consultando Google Places API", ex);
                errorMessage = "Error al consultar Google Places API: " + ex.getMessage();
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("placeName", placeName);
        result.put("placeId", googlePlaceId);
        result.put("average", average);
        result.put("total", total != null ? total : 0);
        result.put("distribution", distribution);
        result.put("reviews", reviews);
        result.put("source", source);
        result.put("placesApiConfigured", placesApiConfigured);
        result.put("fetchedAt", Instant.now().toString());
        if (errorMessage != null) {
            result.put("error", errorMessage);
        }
        return result;
    }
}

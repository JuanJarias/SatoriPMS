package com.satoripms.api.booking;

import com.satoripms.api.event.SpecialEvent;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/**
 * Cálculo de tarifas de estadía con ajustes de eventos especiales aplicados POR NOCHE.
 *
 * Regla vigente (provisional, PENDIENTE DE CONFIRMAR con el cliente):
 * - Cada noche de la estadía (desde check-in hasta la noche anterior al check-out) usa los
 *   eventos activos cuyo rango [startDate, endDate] incluye esa fecha.
 * - Multiplicador de la noche = 1 - (suma de descuentos %) / 100 + (suma de recargos %) / 100,
 *   con piso en 0.
 * - El recargo por personas adicionales (cobro único por estadía) se ajusta con el
 *   multiplicador promedio de las noches de la estadía.
 *
 * La alternativa descartada por ahora era aplicar el ajuste del primer evento a toda la estadía.
 */
public final class StayPricing {

    private static final BigDecimal HUNDRED = BigDecimal.valueOf(100);

    private StayPricing() {
    }

    /**
     * Multiplicador de cada noche de la estadía, en orden cronológico.
     *
     * @param checkIn  fecha de llegada (primera noche)
     * @param checkOut fecha de salida (no se cobra esa noche)
     * @param events   eventos activos que se cruzan con la estadía (puede ser vacía)
     */
    public static List<BigDecimal> nightlyMultipliers(LocalDate checkIn, LocalDate checkOut, List<SpecialEvent> events) {
        List<BigDecimal> multipliers = new ArrayList<>();
        for (LocalDate night = checkIn; night.isBefore(checkOut); night = night.plusDays(1)) {
            BigDecimal discount = BigDecimal.ZERO;
            BigDecimal surcharge = BigDecimal.ZERO;
            for (SpecialEvent event : events == null ? List.<SpecialEvent>of() : events) {
                if (!Boolean.TRUE.equals(event.getIsActive()) || event.getStartDate() == null || event.getEndDate() == null) {
                    continue;
                }
                if (!night.isBefore(event.getStartDate()) && !night.isAfter(event.getEndDate())) {
                    discount = discount.add(nonNull(event.getDiscountPercentage()));
                    surcharge = surcharge.add(nonNull(event.getSurchargePercentage()));
                }
            }
            BigDecimal multiplier = BigDecimal.ONE
                    .subtract(discount.divide(HUNDRED, 6, RoundingMode.HALF_UP))
                    .add(surcharge.divide(HUNDRED, 6, RoundingMode.HALF_UP));
            multipliers.add(multiplier.max(BigDecimal.ZERO));
        }
        return multipliers;
    }

    /** Valor del alojamiento de una habitación: suma de (precio por noche x multiplicador de la noche). */
    public static BigDecimal roomStayTotal(BigDecimal pricePerNight, List<BigDecimal> multipliers) {
        BigDecimal total = BigDecimal.ZERO;
        for (BigDecimal multiplier : multipliers) {
            total = total.add(pricePerNight.multiply(multiplier));
        }
        return total.setScale(2, RoundingMode.HALF_UP);
    }

    /** Multiplicador promedio de la estadía (1 si no hay noches). */
    public static BigDecimal averageMultiplier(List<BigDecimal> multipliers) {
        if (multipliers.isEmpty()) {
            return BigDecimal.ONE;
        }
        BigDecimal sum = multipliers.stream().reduce(BigDecimal.ZERO, BigDecimal::add);
        return sum.divide(BigDecimal.valueOf(multipliers.size()), 6, RoundingMode.HALF_UP);
    }

    private static BigDecimal nonNull(BigDecimal value) {
        return value == null ? BigDecimal.ZERO : value;
    }
}

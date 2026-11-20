package com.satoripms.api.booking;

import com.satoripms.api.event.SpecialEvent;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class StayPricingTest {

    private static final BigDecimal NIGHTLY = BigDecimal.valueOf(100000);

    @Test
    void withoutEventsEveryNightKeepsBasePrice() {
        List<BigDecimal> m = StayPricing.nightlyMultipliers(LocalDate.of(2026, 12, 1), LocalDate.of(2026, 12, 4), List.of());
        assertThat(m).hasSize(3);
        assertThat(StayPricing.roomStayTotal(NIGHTLY, m)).isEqualByComparingTo("300000.00");
    }

    @Test
    void surchargeOnlyAppliesToNightsInsideTheEvent() {
        // Evento con 20% de recargo desde el 20 de diciembre; estadía del 18 al 22 (4 noches: 18, 19, 20, 21).
        SpecialEvent highSeason = event(LocalDate.of(2026, 12, 20), LocalDate.of(2027, 1, 10), 0, 20);
        List<BigDecimal> m = StayPricing.nightlyMultipliers(LocalDate.of(2026, 12, 18), LocalDate.of(2026, 12, 22), List.of(highSeason));
        // 2 noches a 100.000 + 2 noches a 120.000
        assertThat(StayPricing.roomStayTotal(NIGHTLY, m)).isEqualByComparingTo("440000.00");
    }

    @Test
    void discountAppliesAndEventEndDateIsInclusive() {
        // Descuento del 15% del 15 al 22 de noviembre; estadía del 21 al 24 (noches 21, 22, 23).
        SpecialEvent festival = event(LocalDate.of(2026, 11, 15), LocalDate.of(2026, 11, 22), 15, 0);
        List<BigDecimal> m = StayPricing.nightlyMultipliers(LocalDate.of(2026, 11, 21), LocalDate.of(2026, 11, 24), List.of(festival));
        // 85.000 + 85.000 + 100.000
        assertThat(StayPricing.roomStayTotal(NIGHTLY, m)).isEqualByComparingTo("270000.00");
    }

    @Test
    void overlappingEventsCombineAndInactiveEventsAreIgnored() {
        SpecialEvent discount = event(LocalDate.of(2026, 12, 1), LocalDate.of(2026, 12, 31), 10, 0);
        SpecialEvent surcharge = event(LocalDate.of(2026, 12, 1), LocalDate.of(2026, 12, 31), 0, 25);
        SpecialEvent inactive = event(LocalDate.of(2026, 12, 1), LocalDate.of(2026, 12, 31), 50, 0);
        inactive.setIsActive(false);
        List<BigDecimal> m = StayPricing.nightlyMultipliers(LocalDate.of(2026, 12, 5), LocalDate.of(2026, 12, 6),
                List.of(discount, surcharge, inactive));
        // 1 - 0.10 + 0.25 = 1.15
        assertThat(StayPricing.roomStayTotal(NIGHTLY, m)).isEqualByComparingTo("115000.00");
        assertThat(StayPricing.averageMultiplier(m)).isEqualByComparingTo("1.15");
    }

    @Test
    void multiplierNeverGoesBelowZero() {
        SpecialEvent a = event(LocalDate.of(2026, 12, 1), LocalDate.of(2026, 12, 31), 80, 0);
        SpecialEvent b = event(LocalDate.of(2026, 12, 1), LocalDate.of(2026, 12, 31), 50, 0);
        List<BigDecimal> m = StayPricing.nightlyMultipliers(LocalDate.of(2026, 12, 5), LocalDate.of(2026, 12, 6), List.of(a, b));
        assertThat(StayPricing.roomStayTotal(NIGHTLY, m)).isEqualByComparingTo("0.00");
    }

    private static SpecialEvent event(LocalDate start, LocalDate end, double discount, double surcharge) {
        SpecialEvent e = new SpecialEvent();
        e.setStartDate(start);
        e.setEndDate(end);
        e.setDiscountPercentage(BigDecimal.valueOf(discount));
        e.setSurchargePercentage(BigDecimal.valueOf(surcharge));
        e.setIsActive(true);
        return e;
    }
}

package com.satoripms.api.restaurant;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface RestaurantOrderRepository extends JpaRepository<RestaurantOrder, Long> {
    List<RestaurantOrder> findAllByOrderByCreatedAtDesc();
    List<RestaurantOrder> findByBookingId(Long bookingId);
    List<RestaurantOrder> findByBookingIdAndPaymentStatus(Long bookingId, String paymentStatus);
    Optional<RestaurantOrder> findByOrderCode(String orderCode);
}

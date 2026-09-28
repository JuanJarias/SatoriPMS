package com.satoripms.api.booking;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDate;

public interface BookingRepository extends JpaRepository<Booking, Long> {

    @Query("""
        SELECT COUNT(b) FROM Booking b 
        WHERE b.roomId = :roomId 
          AND b.status IN ('pending_payment', 'confirmed') 
          AND b.checkIn < :checkOut 
          AND b.checkOut > :checkIn
    """)
    long countConflictingBookings(
        @Param("roomId") Long roomId, 
        @Param("checkIn") LocalDate checkIn, 
        @Param("checkOut") LocalDate checkOut
    );
}
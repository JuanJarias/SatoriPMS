package com.satoripms.api.booking;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDate;

public interface BookingRepository extends JpaRepository<Booking, Long> {


    @Query(value = "SELECT count(*) FROM booking b WHERE b.room_id = :roomId " +
           "AND b.stay_range && daterange(:checkIn, :checkOut) " +
           "AND b.status IN ('pending_payment', 'confirmed')", nativeQuery = true)
    int countConflictingBookings(@Param("roomId") Long roomId,
                                  @Param("checkIn") LocalDate checkIn,
                                  @Param("checkOut") LocalDate checkOut);
}
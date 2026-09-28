package com.satoripms.api.room;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface RoomRepository extends JpaRepository<Room, Long> {

    @Query("""
        SELECT r FROM Room r 
        WHERE r.active = true 
          AND r.status = 'available' 
          AND (r.maxAdultsCapacity + r.childrenCapacity) >= (:adults + :children) 
          AND (:pet = false OR r.allowsPets = true)
          AND r.id NOT IN (
              SELECT b.roomId FROM Booking b 
              WHERE b.status IN ('pending_payment', 'confirmed') 
                AND b.checkIn < :checkOut 
                AND b.checkOut > :checkIn
          )
    """)
    List<Room> findAvailableRooms(
        @Param("checkIn") LocalDate checkIn, 
        @Param("checkOut") LocalDate checkOut, 
        @Param("adults") Integer adults, 
        @Param("children") Integer children, 
        @Param("pet") Boolean pet
    );
}
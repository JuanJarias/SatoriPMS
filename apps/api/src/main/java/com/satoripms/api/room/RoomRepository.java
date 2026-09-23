package com.satoripms.api.room;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDate;
import java.util.List;

public interface RoomRepository extends JpaRepository<Room, Long> {

    // BUG CORREGIDO: antes solo filtraba active = true, sin revisar status.
    // Eso podía devolver habitaciones en 'occupied', 'cleaning' o
    // 'maintenance' como si estuvieran disponibles. Ahora exige también
    // status = 'available'.
    //
    // NOTA — pendiente en los datos, no en esta query: el seed real
    // (V2__seed_rooms.sql) todavía tiene datos de ejemplo (9 habitaciones
    // inventadas) mientras te confirman las especificaciones reales.
    @Query("SELECT r FROM Room r WHERE r.active = true AND r.status = 'available' " +
           "AND r.maxAdultsCapacity >= :adults " +
           "AND r.childrenCapacity >= :children " +
           "AND (:pet = false OR r.allowsPets = true) " +
           "AND r.id NOT IN (" +
           "  SELECT b.roomId FROM Booking b " +
           "  WHERE b.status IN ('pending_payment', 'confirmed') " +
           "  AND b.checkIn < :checkOut AND b.checkOut > :checkIn" +
           ")")
    List<Room> findAvailableRooms(@Param("checkIn") LocalDate checkIn,
                                   @Param("checkOut") LocalDate checkOut,
                                   @Param("adults") Integer adults,
                                   @Param("children") Integer children,
                                   @Param("pet") Boolean pet);
}
package com.satoripms.api.event;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface SpecialEventRepository extends JpaRepository<SpecialEvent, Long> {

    List<SpecialEvent> findAllByOrderByStartDateAsc();

    @Query("""
        SELECT e FROM SpecialEvent e 
        WHERE e.isActive = true 
          AND e.startDate <= :checkOut 
          AND e.endDate >= :checkIn
        ORDER BY e.startDate ASC
    """)
    List<SpecialEvent> findActiveEventsInDateRange(
        @Param("checkIn") LocalDate checkIn, 
        @Param("checkOut") LocalDate checkOut
    );
}

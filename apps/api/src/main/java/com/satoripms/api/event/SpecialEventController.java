package com.satoripms.api.event;

import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/events")
@RequiredArgsConstructor
public class SpecialEventController {

    private final SpecialEventRepository specialEventRepository;

    @GetMapping
    public List<SpecialEvent> getAllEvents() {
        return specialEventRepository.findAllByOrderByStartDateAsc();
    }

    @GetMapping("/active")
    public List<SpecialEvent> getActiveEvents(
            @RequestParam("checkIn") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate checkIn,
            @RequestParam("checkOut") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate checkOut) {
        return specialEventRepository.findActiveEventsInDateRange(checkIn, checkOut);
    }

    @PostMapping
    public ResponseEntity<SpecialEvent> createEvent(@RequestBody SpecialEventDto dto) {
        if (dto.getStartDate() == null || dto.getEndDate() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Las fechas de inicio y fin son obligatorias.");
        }
        if (dto.getEndDate().isBefore(dto.getStartDate())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "La fecha de fin no puede ser anterior a la fecha de inicio.");
        }

        SpecialEvent event = new SpecialEvent();
        event.setName(dto.getName() != null ? dto.getName() : "Evento Especial");
        event.setDescription(dto.getDescription());
        event.setStartDate(dto.getStartDate());
        event.setEndDate(dto.getEndDate());
        event.setDiscountPercentage(dto.getDiscountPercentage() != null ? dto.getDiscountPercentage() : BigDecimal.ZERO);
        event.setSurchargePercentage(dto.getSurchargePercentage() != null ? dto.getSurchargePercentage() : BigDecimal.ZERO);
        event.setIsActive(dto.getIsActive() != null ? dto.getIsActive() : true);
        event.setCreatedBy(dto.getCreatedBy() != null ? dto.getCreatedBy() : "admin@torresatori.co");

        SpecialEvent saved = specialEventRepository.save(event);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @PutMapping("/{id}")
    public SpecialEvent updateEvent(@PathVariable Long id, @RequestBody SpecialEventDto dto) {
        SpecialEvent event = specialEventRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Evento no encontrado con ID: " + id));

        if (dto.getName() != null) event.setName(dto.getName());
        if (dto.getDescription() != null) event.setDescription(dto.getDescription());
        if (dto.getStartDate() != null) event.setStartDate(dto.getStartDate());
        if (dto.getEndDate() != null) event.setEndDate(dto.getEndDate());
        if (event.getEndDate().isBefore(event.getStartDate())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "La fecha de fin no puede ser anterior a la fecha de inicio.");
        }
        if (dto.getDiscountPercentage() != null) event.setDiscountPercentage(dto.getDiscountPercentage());
        if (dto.getSurchargePercentage() != null) event.setSurchargePercentage(dto.getSurchargePercentage());
        if (dto.getIsActive() != null) event.setIsActive(dto.getIsActive());

        return specialEventRepository.save(event);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteEvent(@PathVariable Long id) {
        SpecialEvent event = specialEventRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Evento no encontrado con ID: " + id));

        specialEventRepository.delete(event);
        return ResponseEntity.ok(Map.of("message", "Evento " + event.getName() + " eliminado exitosamente."));
    }
}

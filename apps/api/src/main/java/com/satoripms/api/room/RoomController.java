package com.satoripms.api.room;

import com.satoripms.api.booking.BookingRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/rooms")
@RequiredArgsConstructor
public class RoomController {

    private final RoomRepository roomRepository;
    private final BookingRepository bookingRepository;

    @GetMapping
    public List<Room> getAllRooms() {
        return roomRepository.findAll(Sort.by(Sort.Direction.ASC, "number"));
    }

    @GetMapping("/{id}")
    public Room getRoomById(@PathVariable Long id) {
        return roomRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Habitación no encontrada con ID: " + id));
    }

    @PostMapping
    public ResponseEntity<Room> createRoom(@RequestBody RoomDto dto) {
        Room room = new Room();
        room.setNumber(dto.getNumber());
        room.setName(dto.getName());
        room.setDescription(dto.getDescription());
        room.setType(dto.getType() != null ? dto.getType() : "ESTANDAR");
        room.setBaseAdultsCapacity(dto.getBaseAdultsCapacity() != null ? dto.getBaseAdultsCapacity() : 2);
        room.setMaxAdultsCapacity(dto.getMaxAdultsCapacity() != null ? dto.getMaxAdultsCapacity() : 2);
        room.setChildrenCapacity(dto.getChildrenCapacity() != null ? dto.getChildrenCapacity() : 0);
        room.setExtraGuestPrice(dto.getExtraGuestPrice() != null ? dto.getExtraGuestPrice() : BigDecimal.ZERO);
        room.setAllowsPets(dto.getAllowsPets() != null ? dto.getAllowsPets() : false);
        room.setPricePerNight(dto.getPricePerNight() != null ? dto.getPricePerNight() : BigDecimal.valueOf(100000));
        room.setStatus(dto.getStatus() != null ? dto.getStatus() : "available");
        room.setActive(dto.getActive() != null ? dto.getActive() : true);

        Room saved = roomRepository.save(room);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @PutMapping("/{id}")
    public Room updateRoom(@PathVariable Long id, @RequestBody RoomDto dto) {
        Room room = roomRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Habitación no encontrada con ID: " + id));

        if (dto.getNumber() != null) room.setNumber(dto.getNumber());
        if (dto.getName() != null) room.setName(dto.getName());
        if (dto.getDescription() != null) room.setDescription(dto.getDescription());
        if (dto.getType() != null) room.setType(dto.getType());
        if (dto.getBaseAdultsCapacity() != null) room.setBaseAdultsCapacity(dto.getBaseAdultsCapacity());
        if (dto.getMaxAdultsCapacity() != null) room.setMaxAdultsCapacity(dto.getMaxAdultsCapacity());
        if (dto.getChildrenCapacity() != null) room.setChildrenCapacity(dto.getChildrenCapacity());
        if (dto.getExtraGuestPrice() != null) room.setExtraGuestPrice(dto.getExtraGuestPrice());
        if (dto.getAllowsPets() != null) room.setAllowsPets(dto.getAllowsPets());
        if (dto.getPricePerNight() != null) room.setPricePerNight(dto.getPricePerNight());
        if (dto.getStatus() != null) room.setStatus(dto.getStatus());
        if (dto.getActive() != null) room.setActive(dto.getActive());

        return roomRepository.save(room);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteRoom(@PathVariable Long id) {
        Room room = roomRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Habitación no encontrada con ID: " + id));

        long activeBookings = bookingRepository.countActiveBookingsByRoomId(id);
        if (activeBookings > 0) {
            throw new ResponseStatusException(
                    HttpStatus.CONFLICT,
                    "No es posible eliminar la habitación " + room.getNumber() + " porque tiene " + activeBookings + " reserva(s) activa(s) o pendientes registradas."
            );
        }

        roomRepository.delete(room);
        return ResponseEntity.ok(Map.of("message", "Habitación " + room.getNumber() + " eliminada exitosamente."));
    }

    @PatchMapping("/{id}/status")
    public Room updateStatus(@PathVariable Long id, @RequestBody Map<String, String> body) {
        Room room = roomRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Habitación no encontrada con ID: " + id));

        String newStatus = body.get("status");
        if (newStatus == null || !List.of("available", "occupied", "cleaning", "maintenance").contains(newStatus)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Estado inválido. Opciones permitidas: available, occupied, cleaning, maintenance");
        }

        room.setStatus(newStatus);
        return roomRepository.save(room);
    }
}

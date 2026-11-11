package com.satoripms.api.restaurant;

import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/restaurant")
@RequiredArgsConstructor
public class RestaurantController {

    private final MenuItemRepository menuItemRepository;
    private final RestaurantOrderRepository restaurantOrderRepository;

    @GetMapping("/menu")
    public List<MenuItem> getMenu(@RequestParam(value = "category", required = false) String category) {
        if (category != null && !category.isBlank()) {
            return menuItemRepository.findByCategoryAndIsAvailableTrue(category);
        }
        return menuItemRepository.findAllByOrderByCategoryAscNameAsc();
    }

    @PostMapping("/menu")
    public ResponseEntity<MenuItem> createMenuItem(@RequestBody MenuItem item) {
        if (item.getName() == null || item.getPrice() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "El nombre y el precio son obligatorios.");
        }
        MenuItem saved = menuItemRepository.save(item);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @PutMapping("/menu/{id}")
    public MenuItem updateMenuItem(@PathVariable Long id, @RequestBody MenuItem item) {
        MenuItem existing = menuItemRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Ítem no encontrado con ID: " + id));

        if (item.getName() != null) existing.setName(item.getName());
        if (item.getCategory() != null) existing.setCategory(item.getCategory());
        if (item.getDescription() != null) existing.setDescription(item.getDescription());
        if (item.getPrice() != null) existing.setPrice(item.getPrice());
        if (item.getIsAvailable() != null) existing.setIsAvailable(item.getIsAvailable());
        if (item.getImageUrl() != null) existing.setImageUrl(item.getImageUrl());

        return menuItemRepository.save(existing);
    }

    @DeleteMapping("/menu/{id}")
    public ResponseEntity<?> deleteMenuItem(@PathVariable Long id) {
        MenuItem item = menuItemRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Ítem no encontrado con ID: " + id));
        menuItemRepository.delete(item);
        return ResponseEntity.ok(Map.of("message", "Ítem " + item.getName() + " eliminado exitosamente."));
    }

    @GetMapping("/orders")
    public List<RestaurantOrder> getOrders() {
        return restaurantOrderRepository.findAllByOrderByCreatedAtDesc();
    }

    @GetMapping("/orders/by-booking/{bookingId}")
    public List<RestaurantOrder> getOrdersByBooking(@PathVariable Long bookingId) {
        return restaurantOrderRepository.findByBookingId(bookingId);
    }

    @PostMapping("/orders")
    @Transactional
    public ResponseEntity<RestaurantOrder> createOrder(@RequestBody RestaurantOrderDto dto) {
        if (dto.getItems() == null || dto.getItems().isEmpty()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "La orden debe contener al menos un producto.");
        }

        RestaurantOrder order = new RestaurantOrder();
        order.setOrderCode("ORD-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        order.setBookingId(dto.getBookingId());
        order.setRoomId(dto.getRoomId());
        order.setCustomerName(dto.getCustomerName() != null ? dto.getCustomerName() : "Cliente de Mostrador");
        order.setDestination(dto.getDestination() != null ? dto.getDestination() : (dto.getRoomId() != null ? "room" : "counter"));
        order.setPaymentStatus(dto.getPaymentStatus() != null ? dto.getPaymentStatus() : (dto.getBookingId() != null ? "charged_to_room" : "paid"));
        order.setPaymentMethod(dto.getPaymentMethod() != null ? dto.getPaymentMethod() : (dto.getBookingId() != null ? "room_charge" : "cash"));
        order.setNotes(dto.getNotes());

        BigDecimal total = BigDecimal.ZERO;
        for (RestaurantOrderDto.OrderItemDto itemDto : dto.getItems()) {
            RestaurantOrderItem item = new RestaurantOrderItem();
            item.setOrder(order);
            item.setMenuItemId(itemDto.getMenuItemId());
            item.setItemName(itemDto.getItemName() != null ? itemDto.getItemName() : "Producto");
            item.setUnitPrice(itemDto.getUnitPrice() != null ? itemDto.getUnitPrice() : BigDecimal.ZERO);
            item.setQuantity(itemDto.getQuantity() != null && itemDto.getQuantity() > 0 ? itemDto.getQuantity() : 1);
            
            BigDecimal subtotal = item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity()));
            item.setSubtotal(subtotal);
            total = total.add(subtotal);

            order.getItems().add(item);
        }

        order.setTotalAmount(total);
        RestaurantOrder saved = restaurantOrderRepository.save(order);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }
}

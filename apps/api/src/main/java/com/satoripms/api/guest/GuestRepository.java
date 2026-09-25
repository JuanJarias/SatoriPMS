package com.satoripms.api.guest;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface GuestRepository extends JpaRepository<Guest, Long> {
    Optional<Guest> findByWhatsappPhone(String whatsappPhone);
}

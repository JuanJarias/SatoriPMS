package com.satoripms.api.booking;

import com.satoripms.api.guest.Guest;
import com.satoripms.api.guest.GuestRepository;
import com.satoripms.api.room.Room;
import com.satoripms.api.room.RoomRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;

@Testcontainers
@DataJpaTest
@EnabledIfEnvironmentVariable(named = "ENABLE_DOCKER_TESTS", matches = "true")
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(BookingService.class)
class BookingBatchPersistenceIntegrationTest {

    @Container
    static final PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("satori_test")
            .withUsername("satori")
            .withPassword("test-password");

    @DynamicPropertySource
    static void configureDatabase(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private BookingService bookingService;

    @Autowired
    private BookingRepository bookingRepository;

    @Autowired
    private GuestRepository guestRepository;

    @Autowired
    private RoomRepository roomRepository;

    @MockBean
    private RedisLockService redisLockService;

    @Test
    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    void persistsPaidBookingForEverySelectedRoomAndDeletesTestData() {
        String phone = "573001234567";
        UUID reservationGroupId = null;
        List<Long> roomIds = List.of();
        try {
            Room firstRoom = roomRepository.saveAndFlush(createRoom("IT-901", 3, 1, 120000, 25000));
            Room secondRoom = roomRepository.saveAndFlush(createRoom("IT-902", 4, 2, 180000, 30000));
            roomIds = List.of(firstRoom.getId(), secondRoom.getId());

            BookingBatchRequestDto request = new BookingBatchRequestDto();
            request.setWaId(phone);
            request.setGuestName("Huésped de prueba");
            request.setGuestDocument("1234567890");
            request.setCompanions("Acompañante uno, Acompañante dos");
            request.setCheckIn(LocalDate.of(2026, 10, 10));
            request.setCheckOut(LocalDate.of(2026, 10, 12));
            request.setAdults(3);
            request.setChildren(4);
            request.setHasPet(false);
            request.setRooms(List.of(lock(firstRoom.getId(), "test-lock-901"), lock(secondRoom.getId(), "test-lock-902")));

            given(redisLockService.isValid(eq(firstRoom.getId()), eq("test-lock-901"))).willReturn(true);
            given(redisLockService.isValid(eq(secondRoom.getId()), eq("test-lock-902"))).willReturn(true);
            given(redisLockService.release(any(), any())).willReturn(true);

            BookingBatchResponseDto response = bookingService.confirmPaidBookings(request);
            reservationGroupId = response.reservationGroupId();

            List<Booking> saved = bookingRepository.findByReservationGroupId(reservationGroupId);
            Guest savedGuest = guestRepository.findByWhatsappPhone(phone).orElseThrow();

            assertThat(saved).hasSize(2);
            assertThat(saved).extracting(Booking::getRoomId).containsExactlyElementsOf(roomIds);
            assertThat(saved).allSatisfy(booking -> {
                assertThat(booking.getStatus()).isEqualTo("confirmed");
                assertThat(booking.getPaymentStatus()).isEqualTo("paid");
                assertThat(booking.getAdults()).isEqualTo(3);
                assertThat(booking.getChildren()).isEqualTo(4);
                assertThat(booking.getCompanions()).isEqualTo("Acompañante uno, Acompañante dos");
                assertThat(booking.getGuestId()).isEqualTo(savedGuest.getId());
            });
            assertThat(response.totalPrice()).isEqualByComparingTo("682500.00");
            assertThat(savedGuest.getName()).isEqualTo("Huésped de prueba");
            assertThat(savedGuest.getDocumentNumber()).isEqualTo("1234567890");
            assertThat(response.bookingIds()).hasSize(2);
        } finally {
            if (reservationGroupId != null) {
                bookingRepository.deleteAll(bookingRepository.findByReservationGroupId(reservationGroupId));
                bookingRepository.flush();
            }
            guestRepository.findByWhatsappPhone(phone).ifPresent(guestRepository::delete);
            if (!roomIds.isEmpty()) {
                roomRepository.deleteAllById(roomIds);
            }
        }

        if (reservationGroupId != null) {
            assertThat(bookingRepository.findByReservationGroupId(reservationGroupId)).isEmpty();
        }
        assertThat(guestRepository.findByWhatsappPhone(phone)).isEmpty();
        assertThat(roomRepository.findAllById(roomIds)).isEmpty();
    }

    @Test
    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    void persistsPendingBookingWithoutMarkingItAsPaid() {
        String phone = "573001234568";
        UUID reservationGroupId = null;
        List<Long> roomIds = List.of();
        try {
            Room room = roomRepository.saveAndFlush(createRoom("IT-903", 3, 1, 120000, 25000));
            roomIds = List.of(room.getId());

            BookingBatchRequestDto request = new BookingBatchRequestDto();
            request.setWaId(phone);
            request.setGuestName("Huésped pendiente");
            request.setGuestDocument("12345678");
            request.setCheckIn(LocalDate.of(2026, 10, 10));
            request.setCheckOut(LocalDate.of(2026, 10, 12));
            request.setAdults(2);
            request.setChildren(0);
            request.setHasPet(false);
            request.setRooms(List.of(lock(room.getId(), "test-lock-903")));

            given(redisLockService.isValid(eq(room.getId()), eq("test-lock-903"))).willReturn(true);
            given(redisLockService.release(any(), any())).willReturn(true);

            BookingBatchResponseDto response = bookingService.confirmPendingBookings(request);
            reservationGroupId = response.reservationGroupId();

            Booking saved = bookingRepository.findByReservationGroupId(reservationGroupId).get(0);
            assertThat(saved.getStatus()).isEqualTo("pending_payment");
            assertThat(saved.getPaymentStatus()).isEqualTo("pending");
            assertThat(response.status()).isEqualTo("pending_payment");
            assertThat(response.paymentStatus()).isEqualTo("pending");
        } finally {
            if (reservationGroupId != null) {
                bookingRepository.deleteAll(bookingRepository.findByReservationGroupId(reservationGroupId));
                bookingRepository.flush();
            }
            guestRepository.findByWhatsappPhone(phone).ifPresent(guestRepository::delete);
            if (!roomIds.isEmpty()) {
                roomRepository.deleteAllById(roomIds);
            }
        }

        assertThat(guestRepository.findByWhatsappPhone(phone)).isEmpty();
        assertThat(roomRepository.findAllById(roomIds)).isEmpty();
    }

    private static BookingRoomLockDto lock(Long roomId, String token) {
        BookingRoomLockDto roomLock = new BookingRoomLockDto();
        roomLock.setRoomId(roomId);
        roomLock.setLockToken(token);
        return roomLock;
    }

    private static Room createRoom(String number, int maxAdults, int children, long nightlyPrice, long extraGuestPrice) {
        Room room = new Room();
        room.setNumber(number);
        room.setName("Habitación de prueba " + number);
        room.setType("TEST");
        room.setBaseAdultsCapacity(2);
        room.setMaxAdultsCapacity(maxAdults);
        room.setChildrenCapacity(children);
        room.setExtraGuestPrice(BigDecimal.valueOf(extraGuestPrice));
        room.setAllowsPets(true);
        room.setPricePerNight(BigDecimal.valueOf(nightlyPrice));
        room.setStatus("available");
        room.setActive(true);
        return room;
    }
}
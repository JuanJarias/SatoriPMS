ALTER TABLE guest ADD COLUMN document_number VARCHAR(50);
ALTER TABLE booking ADD COLUMN reservation_group_id UUID;
ALTER TABLE booking ADD COLUMN companions TEXT;

CREATE INDEX idx_booking_reservation_group ON booking(reservation_group_id);
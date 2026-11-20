-- V9: Columna dedicada para el código público de reserva (TS-XXXX).
--
-- Hasta ahora el código se guardaba en la columna "companions", reemplazando
-- los nombres reales de los acompañantes. Esta migración:
--   1. Crea booking.booking_code.
--   2. Mueve a booking_code los códigos que estaban guardados en companions
--      y deja companions vacío en esas filas (el nombre original ya se perdió).
--   3. Para las filas restantes, conserva el código que el sistema mostraba
--      (TS- + últimos 4 caracteres del grupo de reserva, o TS- + id).

ALTER TABLE booking ADD COLUMN booking_code VARCHAR(20);

UPDATE booking
SET booking_code = UPPER(TRIM(companions)),
    companions = NULL
WHERE companions ~* '^\s*(TS|BL)-[A-Z0-9]+\s*$';

UPDATE booking
SET booking_code = 'TS-' || UPPER(RIGHT(REPLACE(reservation_group_id::text, '-', ''), 4))
WHERE booking_code IS NULL AND reservation_group_id IS NOT NULL;

UPDATE booking
SET booking_code = 'TS-' || id
WHERE booking_code IS NULL;

ALTER TABLE booking ALTER COLUMN booking_code SET NOT NULL;

CREATE INDEX idx_booking_code ON booking(booking_code);

-- V5: Agregar monto pagado a reservas y soporte de reseñas (Google Reviews / Directas)

-- 1. Columna paid_amount en booking para registrar pagos parciales (50%) o totales (100%)
ALTER TABLE booking ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00;

-- Sincronizar registros existentes
UPDATE booking SET paid_amount = total_price WHERE payment_status = 'paid';
UPDATE booking SET paid_amount = total_price / 2 WHERE payment_status = 'partial';

-- 2. Adaptar la tabla review para permitir reseñas de Google o sin reserva forzosa
ALTER TABLE review ALTER COLUMN room_id DROP NOT NULL;
ALTER TABLE review ALTER COLUMN booking_id DROP NOT NULL;
ALTER TABLE review ALTER COLUMN guest_id DROP NOT NULL;
ALTER TABLE review ADD COLUMN IF NOT EXISTS author_name VARCHAR(150);
ALTER TABLE review ADD COLUMN IF NOT EXISTS source VARCHAR(50) DEFAULT 'google';

-- 3. Semilla de reseñas destacadas de Google para Torre Satori si no existen
INSERT INTO review (author_name, rating, comment, source, created_at)
SELECT 'Carlos Mario Restrepo', 5, 'Excelente ubicación en Sevilla. El mirador y la tranquilidad del hotel familiar son inigualables. Muy recomendado para descansar.', 'google', CURRENT_TIMESTAMP - INTERVAL '5 days'
WHERE NOT EXISTS (SELECT 1 FROM review WHERE author_name = 'Carlos Mario Restrepo');

INSERT INTO review (author_name, rating, comment, source, created_at)
SELECT 'Valentina Gómez', 5, 'La atención por WhatsApp y en recepción fue impecable. Habitaciones muy limpias y acogedoras. Volveremos sin duda.', 'google', CURRENT_TIMESTAMP - INTERVAL '3 days'
WHERE NOT EXISTS (SELECT 1 FROM review WHERE author_name = 'Valentina Gómez');

INSERT INTO review (author_name, rating, comment, source, created_at)
SELECT 'Andrés Felipe Morales', 4, 'Gran experiencia en el Eje Cafetero y Sevilla. El café delicioso y el personal muy atento a cualquier solicitud.', 'google', CURRENT_TIMESTAMP - INTERVAL '1 day'
WHERE NOT EXISTS (SELECT 1 FROM review WHERE author_name = 'Andrés Felipe Morales');


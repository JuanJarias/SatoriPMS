-- db/seed/dev_seed.sql
--
-- Datos iniciales completos para desarrollo local y pruebas integrales de Torre Satori PMS.
-- Se ejecuta automáticamente o manual:
--   docker compose exec postgres psql -U satori -d satoripms -f /seed/dev_seed.sql

-- 1. Usuarios del Sistema (Admin y Recepción)
INSERT INTO system_users (username, password_hash, role, name) VALUES
('admin', '$2a$12$Uy2lw7y1LED32eVFbbxvvO/96LQIj30HMF8LWpauAeqok7nrMaJS.', 'admin', 'Frank Arias Salgado - Administrador'),
('admin@gmail.com', '$2a$12$Uy2lw7y1LED32eVFbbxvvO/96LQIj30HMF8LWpauAeqok7nrMaJS.', 'admin', 'Frank Arias Salgado - Administrador'),
('recepcion', '$2a$12$Uy2lw7y1LED32eVFbbxvvO/96LQIj30HMF8LWpauAeqok7nrMaJS.', 'receptionist', 'Sofía Valencia - Recepcionista')
ON CONFLICT (username) DO UPDATE SET role = EXCLUDED.role, name = EXCLUDED.name;

-- 2. Las 9 Habitaciones de Referencia (Pisos 1, 2 y 3)
INSERT INTO room (number, name, type, base_adults_capacity, max_adults_capacity, children_capacity, extra_guest_price, allows_pets, price_per_night, status, active) VALUES
('101', 'Habitación 101 - Jardín', 'ESTANDAR', 2, 3, 1, 40000, TRUE,  180000, 'occupied', TRUE),
('102', 'Habitación 102 - Familiar', 'ESTANDAR', 2, 4, 2, 40000, FALSE, 290000, 'available', TRUE),
('103', 'Habitación 103 - Patio', 'ESTANDAR', 2, 3, 1, 40000, TRUE,  170000, 'maintenance', TRUE),
('201', 'Habitación 201 - Balcón', 'DOBLE', 2, 4, 2, 40000, FALSE, 210000, 'cleaning', TRUE),
('202', 'Habitación 202 - Suite Satori', 'DOBLE', 2, 4, 2, 40000, TRUE,  380000, 'available', TRUE),
('203', 'Habitación 203 - Cafetal', 'DOBLE', 2, 4, 2, 40000, FALSE, 220000, 'available', TRUE),
('301', 'Habitación 301 - Mirador del Valle', 'SUITE', 4, 6, 2, 50000, FALSE, 350000, 'available', TRUE),
('302', 'Habitación 302 - Atardecer', 'SUITE', 2, 4, 1, 40000, FALSE, 200000, 'available', TRUE),
('303', 'Habitación 303 - Cordillera', 'SUITE', 4, 6, 2, 45000, TRUE,  320000, 'available', TRUE)
ON CONFLICT (number) DO UPDATE SET 
    name = EXCLUDED.name,
    price_per_night = EXCLUDED.price_per_night,
    extra_guest_price = EXCLUDED.extra_guest_price,
    max_adults_capacity = EXCLUDED.max_adults_capacity,
    status = EXCLUDED.status;

-- 3. Productos de Tienda y Minibar (con Salgados Café)
INSERT INTO product (name, price, stock) VALUES
('Agua Cristal 600 ml', 3000.00, 24),
('Gaseosa Postobón 400 ml', 4000.00, 12),
('Cerveza Club Colombia', 7000.00, 8),
('Papas Margarita pollo', 3500.00, 15),
('Chocolatina Jet', 2500.00, 10),
('Salgados Café Origen Especial 250g', 25000.00, 20),
('Salgados Café Drip Bag (Pack x 5)', 16000.00, 18),
('Protector solar FPS 50', 28000.00, 4),
('Cepillo y crema dental', 6000.00, 9)
ON CONFLICT DO NOTHING;

-- 4. Eventos Especiales de Referencia
INSERT INTO special_events (name, description, start_date, end_date, discount_percentage, surcharge_percentage, is_active, created_by)
SELECT 'Temporada Festivales del Café (Sevilla)', 'Semana de la cultura cafetera con alta afluencia regional en Sevilla.', '2026-10-10', '2026-10-18', 0.00, 15.00, TRUE, 'gerencia@torresatori.co'
WHERE NOT EXISTS (SELECT 1 FROM special_events WHERE name = 'Temporada Festivales del Café (Sevilla)');

INSERT INTO special_events (name, description, start_date, end_date, discount_percentage, surcharge_percentage, is_active, created_by)
SELECT 'Promoción Escapada Entre Semana', 'Descuento especial del 10% para reservas de lunes a jueves.', '2026-10-01', '2026-10-31', 10.00, 0.00, TRUE, 'gerencia@torresatori.co'
WHERE NOT EXISTS (SELECT 1 FROM special_events WHERE name = 'Promoción Escapada Entre Semana');

-- 5. Huéspedes de Referencia de Figma
INSERT INTO guest (name, whatsapp_phone, email, document_number) VALUES
('Maria', '+57 300 222 2222', 'maria22@ejemplo.com', '222222'),
('Laura Gómez', '+57 310 555 0142', 'laura.gomez@gmail.com', 'CC 1.113.555.201'),
('Andrés Martínez', '+57 315 555 0187', 'andres.martinez@hotmail.com', 'CC 94.333.712'),
('María Fernanda Rojas', '+57 300 555 0164', 'mafe.rojas@outlook.com', 'CC 66.812.430'),
('Camilo Herrera', '+57 320 555 0119', 'camilo.herrera@yahoo.com', 'CC 16.280.944')
ON CONFLICT (whatsapp_phone) DO UPDATE SET 
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    document_number = EXCLUDED.document_number;

-- 6. Reservas de Referencia de Figma (TS-2391, TS-2041, TS-2047, BL-0318, TS-2052, TS-2036, TS-2033, TS-2029)
-- Se asocian usando identificadores de habitación y huésped
INSERT INTO booking (guest_id, room_id, check_in, check_out, status, payment_status, adults, children, with_pet, total_price, paid_amount, source, reservation_group_id, companions)
SELECT 
    g.id, r.id, '2026-10-03', '2026-10-08', 'confirmed', 'paid', 2, 0, FALSE, 850000.00, 850000.00, 'web', '00002391-0000-0000-0000-000000002391', 'TS-2391'
FROM guest g, room r 
WHERE g.document_number = '222222' AND r.number = '103'
AND NOT EXISTS (SELECT 1 FROM booking WHERE reservation_group_id = '00002391-0000-0000-0000-000000002391');

INSERT INTO booking (guest_id, room_id, check_in, check_out, status, payment_status, adults, children, with_pet, total_price, paid_amount, source, reservation_group_id, companions)
SELECT 
    g.id, r.id, '2026-09-29', '2026-10-02', 'confirmed', 'paid', 2, 0, TRUE, 540000.00, 540000.00, 'chatbot', '00002041-0000-0000-0000-000000002041', 'TS-2041'
FROM guest g, room r 
WHERE g.document_number = 'CC 1.113.555.201' AND r.number = '101'
AND NOT EXISTS (SELECT 1 FROM booking WHERE reservation_group_id = '00002041-0000-0000-0000-000000002041');

INSERT INTO booking (guest_id, room_id, check_in, check_out, status, payment_status, adults, children, with_pet, total_price, paid_amount, source, reservation_group_id, companions)
SELECT 
    g.id, r.id, '2026-10-01', '2026-10-04', 'confirmed', 'partial', 4, 1, FALSE, 870000.00, 435000.00, 'chatbot', '00002047-0000-0000-0000-000000002047', 'TS-2047'
FROM guest g, room r 
WHERE g.document_number = 'CC 94.333.712' AND r.number = '102'
AND NOT EXISTS (SELECT 1 FROM booking WHERE reservation_group_id = '00002047-0000-0000-0000-000000002047');

INSERT INTO booking (guest_id, room_id, check_in, check_out, status, payment_status, adults, children, with_pet, total_price, paid_amount, source, reservation_group_id, companions)
SELECT 
    g.id, r.id, '2026-10-03', '2026-10-05', 'pending_payment', 'partial', 3, 0, FALSE, 420000.00, 100000.00, 'web', '00002052-0000-0000-0000-000000002052', 'TS-2052'
FROM guest g, room r 
WHERE g.document_number = 'CC 16.280.944' AND r.number = '201'
AND NOT EXISTS (SELECT 1 FROM booking WHERE reservation_group_id = '00002052-0000-0000-0000-000000002052');

INSERT INTO booking (guest_id, room_id, check_in, check_out, status, payment_status, adults, children, with_pet, total_price, paid_amount, source, reservation_group_id, companions)
SELECT 
    g.id, r.id, '2026-09-28', '2026-10-01', 'finished', 'paid', 2, 0, FALSE, 630000.00, 630000.00, 'web', '00002036-0000-0000-0000-000000002036', 'TS-2036'
FROM guest g, room r 
WHERE g.document_number = 'CC 66.812.430' AND r.number = '201'
AND NOT EXISTS (SELECT 1 FROM booking WHERE reservation_group_id = '00002036-0000-0000-0000-000000002036');

INSERT INTO booking (guest_id, room_id, check_in, check_out, status, payment_status, adults, children, with_pet, total_price, paid_amount, source, reservation_group_id, companions)
SELECT 
    g.id, r.id, '2026-09-12', '2026-09-14', 'finished', 'paid', 2, 0, FALSE, 760000.00, 760000.00, 'chatbot', '00002033-0000-0000-0000-000000002033', 'TS-2033'
FROM guest g, room r 
WHERE g.document_number = 'CC 1.113.555.201' AND r.number = '202'
AND NOT EXISTS (SELECT 1 FROM booking WHERE reservation_group_id = '00002033-0000-0000-0000-000000002033');

INSERT INTO booking (guest_id, room_id, check_in, check_out, status, payment_status, adults, children, with_pet, total_price, paid_amount, source, reservation_group_id, companions)
SELECT 
    g.id, r.id, '2026-09-20', '2026-09-22', 'cancelled', 'refunded', 2, 0, FALSE, 360000.00, 0.00, 'chatbot', '00002029-0000-0000-0000-000000002029', 'TS-2029'
FROM guest g, room r 
WHERE g.document_number = 'CC 94.333.712' AND r.number = '101'
AND NOT EXISTS (SELECT 1 FROM booking WHERE reservation_group_id = '00002029-0000-0000-0000-000000002029');

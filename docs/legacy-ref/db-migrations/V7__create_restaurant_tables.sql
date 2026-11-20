-- V7: Módulo de Restaurante, Cafetería Salgados Café y Experiencias de Barismo

CREATE TABLE IF NOT EXISTS menu_items (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL
        CHECK (category IN ('desayuno', 'cafeteria', 'experiencia', 'bebida', 'snack', 'postre')),
    description TEXT,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    image_url VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items(category);
CREATE INDEX IF NOT EXISTS idx_menu_items_available ON menu_items(is_available);

CREATE TABLE IF NOT EXISTS restaurant_orders (
    id BIGSERIAL PRIMARY KEY,
    order_code VARCHAR(50) UNIQUE NOT NULL,
    booking_id BIGINT REFERENCES booking(id) ON DELETE SET NULL,
    room_id BIGINT REFERENCES room(id) ON DELETE SET NULL,
    customer_name VARCHAR(150) NOT NULL,
    destination VARCHAR(30) NOT NULL DEFAULT 'room'
        CHECK (destination IN ('room', 'counter', 'mirador', 'table')),
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    payment_status VARCHAR(30) NOT NULL DEFAULT 'charged_to_room'
        CHECK (payment_status IN ('paid', 'charged_to_room', 'pending', 'cancelled')),
    payment_method VARCHAR(30) DEFAULT 'room_charge'
        CHECK (payment_method IN ('cash', 'card', 'transfer', 'room_charge')),
    notes TEXT,
    created_by VARCHAR(100) DEFAULT 'recepcion@torresatori.co',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_restaurant_orders_booking ON restaurant_orders(booking_id);
CREATE INDEX IF NOT EXISTS idx_restaurant_orders_room ON restaurant_orders(room_id);
CREATE INDEX IF NOT EXISTS idx_restaurant_orders_status ON restaurant_orders(payment_status);

CREATE TABLE IF NOT EXISTS restaurant_order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES restaurant_orders(id) ON DELETE CASCADE,
    menu_item_id BIGINT REFERENCES menu_items(id) ON DELETE SET NULL,
    item_name VARCHAR(150) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    subtotal NUMERIC(10, 2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_restaurant_order_items_order ON restaurant_order_items(order_id);

-- Semilla oficial de la Carta de Desayunos, Cafetería Salgados Café y Experiencias
INSERT INTO menu_items (name, category, description, price, is_available)
SELECT 'Desayuno Típico Sevillano', 'desayuno', 'Huevos al gusto, arepa con queso campesino, porción de fruta fresca y café especial de origen Salgados Café.', 18000.00, TRUE
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Desayuno Típico Sevillano');

INSERT INTO menu_items (name, category, description, price, is_available)
SELECT 'Desayuno Americano Torre Satori', 'desayuno', 'Tostadas francesas, tocineta crujiente, huevos revueltos, jugo de naranja natural y café Salgados Café.', 22000.00, TRUE
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Desayuno Americano Torre Satori');

INSERT INTO menu_items (name, category, description, price, is_available)
SELECT 'Espresso Doble Salgados Café', 'cafeteria', 'Extracción intensa con granos de café especial cosechados en Sevilla, tueste medio y notas a panela y cacao.', 7000.00, TRUE
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Espresso Doble Salgados Café');

INSERT INTO menu_items (name, category, description, price, is_available)
SELECT 'Filtrado Artesanal V60 / Chemex', 'cafeteria', 'Método de filtrado manual en mesa resaltando la acidez cítrica y dulzura del café de la cordillera.', 12000.00, TRUE
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Filtrado Artesanal V60 / Chemex');

INSERT INTO menu_items (name, category, description, price, is_available)
SELECT 'Capuchino Especial con Canela', 'cafeteria', 'Leche cremada al vapor con shot de café Salgados Café y toque de canela de la región.', 9500.00, TRUE
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Capuchino Especial con Canela');

INSERT INTO menu_items (name, category, description, price, is_available)
SELECT 'Cata Guiada y Taller de Barismo', 'experiencia', 'Experiencia sensorial de 45 minutos en el mirador con barista experto, catando 3 varietales de café especial.', 45000.00, TRUE
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Cata Guiada y Taller de Barismo');

INSERT INTO menu_items (name, category, description, price, is_available)
SELECT 'Torta Artesanal de Café y Nueces', 'postre', 'Porción horneada en casa con infusión de café Salgados Café y nueces caramelizadas.', 8500.00, TRUE
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Torta Artesanal de Café y Nueces');

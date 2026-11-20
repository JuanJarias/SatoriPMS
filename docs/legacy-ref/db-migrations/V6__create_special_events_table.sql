-- V6: Módulo de Eventos Especiales y Tarifas Dinámicas por Temporada

CREATE TABLE IF NOT EXISTS special_events (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    discount_percentage NUMERIC(5, 2) NOT NULL DEFAULT 0.00
        CHECK (discount_percentage >= 0 AND discount_percentage <= 100),
    surcharge_percentage NUMERIC(5, 2) NOT NULL DEFAULT 0.00
        CHECK (surcharge_percentage >= 0 AND surcharge_percentage <= 100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by VARCHAR(100) DEFAULT 'admin@torresatori.co',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_event_dates CHECK (end_date >= start_date)
);

CREATE INDEX IF NOT EXISTS idx_special_events_dates ON special_events(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_special_events_active ON special_events(is_active);

-- Semilla de evento especial de referencia en Sevilla, Valle del Cauca
INSERT INTO special_events (name, description, start_date, end_date, discount_percentage, surcharge_percentage, is_active, created_by)
SELECT 'Festival del Café de Sevilla', 'Tarifa promocional con 15% de descuento en estadías durante la semana de la cultura y el café en Sevilla.', '2026-11-15', '2026-11-22', 15.00, 0.00, TRUE, 'admin@torresatori.co'
WHERE NOT EXISTS (SELECT 1 FROM special_events WHERE name = 'Festival del Café de Sevilla');

INSERT INTO special_events (name, description, start_date, end_date, discount_percentage, surcharge_percentage, is_active, created_by)
SELECT 'Temporada Alta Fin de Año', 'Recargo de temporada alta del 20% aplicable para reservas entre Navidad y Reyes.', '2026-12-20', '2027-01-10', 0.00, 20.00, TRUE, 'admin@torresatori.co'
WHERE NOT EXISTS (SELECT 1 FROM special_events WHERE name = 'Temporada Alta Fin de Año');

CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE guest (
    id SERIAL PRIMARY KEY,
    whatsapp_phone VARCHAR(20) UNIQUE,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE room (
    id SERIAL PRIMARY KEY,
    number VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    base_adults_capacity INT NOT NULL,
    max_adults_capacity INT NOT NULL,
    children_capacity INT NOT NULL DEFAULT 0,
    extra_guest_price NUMERIC(10, 2) NOT NULL DEFAULT 0,
    allows_pets BOOLEAN NOT NULL DEFAULT FALSE,
    price_per_night NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'available'
        CHECK (status IN ('available', 'occupied', 'cleaning', 'maintenance')),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_room_capacity CHECK (max_adults_capacity >= base_adults_capacity)
);
CREATE INDEX idx_room_type ON room(type);
CREATE INDEX idx_room_status ON room(status);

CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    guest_id INT NOT NULL REFERENCES guest(id),
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'escalated', 'cancelled', 'completed', 'expired')),
    step VARCHAR(30) NOT NULL DEFAULT 'welcome'
        CHECK (step IN ('welcome', 'dates', 'room_selection', 'occupancy', 'pet', 'review')),
    check_in DATE,
    check_out DATE,
    selected_room_id INT REFERENCES room(id),
    adults INT,
    children INT NOT NULL DEFAULT 0,
    with_pet BOOLEAN,
    total_price NUMERIC(10, 2),
    lock_token VARCHAR(100),
    lock_expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_conversation_dates CHECK (
        check_in IS NULL OR check_out IS NULL OR check_in < check_out
    ),
    CONSTRAINT chk_conversation_people CHECK (
        (adults IS NULL OR adults >= 0) AND children >= 0
    )
);
CREATE UNIQUE INDEX uq_active_conversation_guest
    ON conversation(guest_id) WHERE status = 'active';
CREATE INDEX idx_conversation_status ON conversation(status);

CREATE TABLE booking (
    id SERIAL PRIMARY KEY,
    guest_id INT NOT NULL REFERENCES guest(id),
    room_id INT NOT NULL REFERENCES room(id),
    conversation_id INT UNIQUE REFERENCES conversation(id),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    stay_range DATERANGE GENERATED ALWAYS AS (
        daterange(check_in, check_out, '[)')
    ) STORED,
    status VARCHAR(20) NOT NULL
        CHECK (status IN ('pending_payment', 'confirmed', 'finished', 'cancelled')),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (payment_status IN ('pending', 'paid', 'refunded', 'partial')),
    adults INT NOT NULL,
    children INT NOT NULL DEFAULT 0,
    with_pet BOOLEAN NOT NULL DEFAULT FALSE,
    total_price NUMERIC(10, 2) NOT NULL,
    source VARCHAR(20) NOT NULL CHECK (source IN ('chatbot', 'web')),
    lock_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_booking_dates CHECK (check_in < check_out),
    CONSTRAINT chk_booking_people CHECK (adults >= 0 AND children >= 0),
    CONSTRAINT chk_booking_range_not_empty CHECK (NOT isempty(stay_range)),
    CONSTRAINT no_overlapping_bookings EXCLUDE USING gist (
        room_id WITH =,
        stay_range WITH &&
    ) WHERE (status IN ('pending_payment', 'confirmed'))
);
CREATE INDEX idx_booking_stay_range ON booking USING gist (stay_range);
CREATE INDEX idx_booking_room ON booking(room_id);
CREATE INDEX idx_booking_guest ON booking(guest_id);

CREATE TABLE review (
    id SERIAL PRIMARY KEY,
    guest_id INT NOT NULL REFERENCES guest(id),
    room_id INT NOT NULL REFERENCES room(id),
    booking_id INT UNIQUE NOT NULL REFERENCES booking(id),
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE consumption (
    id SERIAL PRIMARY KEY,
    booking_id INT NOT NULL REFERENCES booking(id),
    product_id INT NOT NULL REFERENCES product(id),
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    paid BOOLEAN NOT NULL DEFAULT FALSE,
    occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE system_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'receptionist')),
    name VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
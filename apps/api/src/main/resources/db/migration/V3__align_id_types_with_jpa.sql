-- Align PostgreSQL identifiers with Java Long fields used by JPA.

ALTER TABLE conversation
    DROP CONSTRAINT IF EXISTS conversation_guest_id_fkey,
    DROP CONSTRAINT IF EXISTS conversation_selected_room_id_fkey;

ALTER TABLE booking
    DROP CONSTRAINT IF EXISTS booking_conversation_id_fkey,
    DROP CONSTRAINT IF EXISTS booking_guest_id_fkey,
    DROP CONSTRAINT IF EXISTS booking_room_id_fkey,
    DROP CONSTRAINT IF EXISTS no_overlapping_bookings;

ALTER TABLE review
    DROP CONSTRAINT IF EXISTS review_booking_id_fkey,
    DROP CONSTRAINT IF EXISTS review_guest_id_fkey,
    DROP CONSTRAINT IF EXISTS review_room_id_fkey;

ALTER TABLE consumption
    DROP CONSTRAINT IF EXISTS consumption_booking_id_fkey,
    DROP CONSTRAINT IF EXISTS consumption_product_id_fkey;

ALTER TABLE conversation DROP CONSTRAINT IF EXISTS conversation_pkey;
ALTER TABLE booking DROP CONSTRAINT IF EXISTS booking_pkey;
ALTER TABLE review DROP CONSTRAINT IF EXISTS review_pkey;
ALTER TABLE consumption DROP CONSTRAINT IF EXISTS consumption_pkey;
ALTER TABLE guest DROP CONSTRAINT IF EXISTS guest_pkey;
ALTER TABLE room DROP CONSTRAINT IF EXISTS room_pkey;
ALTER TABLE product DROP CONSTRAINT IF EXISTS product_pkey;
ALTER TABLE system_users DROP CONSTRAINT IF EXISTS system_users_pkey;

ALTER TABLE guest ALTER COLUMN id TYPE BIGINT USING id::BIGINT;
ALTER TABLE room ALTER COLUMN id TYPE BIGINT USING id::BIGINT;
ALTER TABLE conversation
    ALTER COLUMN id TYPE BIGINT USING id::BIGINT,
    ALTER COLUMN guest_id TYPE BIGINT USING guest_id::BIGINT,
    ALTER COLUMN selected_room_id TYPE BIGINT USING selected_room_id::BIGINT;
ALTER TABLE booking
    ALTER COLUMN id TYPE BIGINT USING id::BIGINT,
    ALTER COLUMN guest_id TYPE BIGINT USING guest_id::BIGINT,
    ALTER COLUMN room_id TYPE BIGINT USING room_id::BIGINT,
    ALTER COLUMN conversation_id TYPE BIGINT USING conversation_id::BIGINT;
ALTER TABLE review
    ALTER COLUMN id TYPE BIGINT USING id::BIGINT,
    ALTER COLUMN guest_id TYPE BIGINT USING guest_id::BIGINT,
    ALTER COLUMN room_id TYPE BIGINT USING room_id::BIGINT,
    ALTER COLUMN booking_id TYPE BIGINT USING booking_id::BIGINT;
ALTER TABLE product ALTER COLUMN id TYPE BIGINT USING id::BIGINT;
ALTER TABLE consumption
    ALTER COLUMN id TYPE BIGINT USING id::BIGINT,
    ALTER COLUMN booking_id TYPE BIGINT USING booking_id::BIGINT,
    ALTER COLUMN product_id TYPE BIGINT USING product_id::BIGINT;
ALTER TABLE system_users ALTER COLUMN id TYPE BIGINT USING id::BIGINT;

ALTER TABLE guest ADD CONSTRAINT guest_pkey PRIMARY KEY (id);
ALTER TABLE room ADD CONSTRAINT room_pkey PRIMARY KEY (id);
ALTER TABLE conversation ADD CONSTRAINT conversation_pkey PRIMARY KEY (id);
ALTER TABLE booking ADD CONSTRAINT booking_pkey PRIMARY KEY (id);
ALTER TABLE review ADD CONSTRAINT review_pkey PRIMARY KEY (id);
ALTER TABLE product ADD CONSTRAINT product_pkey PRIMARY KEY (id);
ALTER TABLE consumption ADD CONSTRAINT consumption_pkey PRIMARY KEY (id);
ALTER TABLE system_users ADD CONSTRAINT system_users_pkey PRIMARY KEY (id);

ALTER TABLE conversation
    ADD CONSTRAINT conversation_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES guest(id),
    ADD CONSTRAINT conversation_selected_room_id_fkey FOREIGN KEY (selected_room_id) REFERENCES room(id);
ALTER TABLE booking
    ADD CONSTRAINT booking_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES conversation(id),
    ADD CONSTRAINT booking_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES guest(id),
    ADD CONSTRAINT booking_room_id_fkey FOREIGN KEY (room_id) REFERENCES room(id);
ALTER TABLE review
    ADD CONSTRAINT review_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES booking(id),
    ADD CONSTRAINT review_guest_id_fkey FOREIGN KEY (guest_id) REFERENCES guest(id),
    ADD CONSTRAINT review_room_id_fkey FOREIGN KEY (room_id) REFERENCES room(id);
ALTER TABLE consumption
    ADD CONSTRAINT consumption_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES booking(id),
    ADD CONSTRAINT consumption_product_id_fkey FOREIGN KEY (product_id) REFERENCES product(id);

ALTER TABLE booking ADD CONSTRAINT no_overlapping_bookings EXCLUDE USING gist (
    room_id WITH =,
    stay_range WITH &&
) WHERE (status IN ('pending_payment', 'confirmed'));

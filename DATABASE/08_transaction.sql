USE nearhub;

SELECT
    room_id,
    room_number,
    available_beds,
    status
FROM room
WHERE room_id = 1;

START TRANSACTION;

INSERT INTO room_booking
(
    student_id,
    room_id,
    booking_date,
    start_date,
    end_date,
    status
)
VALUES
(
    1,
    1,
    NOW(),
    '2026-10-01',
    '2027-06-30',
    'Pending'
);

COMMIT;

SELECT
    booking_id,
    student_id,
    room_id,
    status
FROM room_booking
ORDER BY booking_id DESC
LIMIT 1;


SELECT
    room_id,
    available_beds
FROM room
WHERE room_id = 1;

START TRANSACTION;

UPDATE room
SET available_beds = available_beds - 1
WHERE room_id = 2;

SELECT available_beds
FROM room
WHERE room_id = 2;

ROLLBACK;

SELECT available_beds
FROM room
WHERE room_id = 2;

SELECT
    CONSTRAINT_NAME,
    CHECK_CLAUSE
FROM information_schema.CHECK_CONSTRAINTS
WHERE CONSTRAINT_SCHEMA = 'nearhub'
  AND CONSTRAINT_NAME = 'room_chk_3';
 
ALTER TABLE room
DROP CHECK room_chk_3; 
ALTER TABLE room
ADD CONSTRAINT room_chk_3
CHECK (available_beds >= 0); 
 
 rollback;
SELECT room_id, room_number, capacity, available_beds, status
FROM room
WHERE available_beds > 0
  AND status = 'Available';


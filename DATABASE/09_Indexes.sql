USE nearhub;

SHOW INDEX FROM student;
SHOW INDEX FROM hostel;
SHOW INDEX FROM room;
SHOW INDEX FROM mess;
SHOW INDEX FROM room_booking;
SHOW INDEX FROM meal_subscription;
SHOW INDEX FROM feedback;
SHOW INDEX FROM meal_plan;

CREATE INDEX idx_hostel_status_location
ON hostel(status, location);


CREATE INDEX idx_room_hostel_status
ON room(hostel_id, status);

CREATE INDEX idx_room_status_beds
ON room(status, available_beds);

CREATE INDEX idx_mess_status_location
ON mess(status, location);

CREATE INDEX idx_meal_plan_mess
ON meal_plan(mess_id);

CREATE INDEX idx_booking_student_status
ON room_booking(student_id, status);

CREATE INDEX idx_subscription_student_status
ON meal_subscription(student_id, status);

CREATE INDEX idx_feedback_status
ON feedback(status);

USE nearhub;
SHOW INDEX FROM hostel;
SHOW INDEX FROM room;
SHOW INDEX FROM room_booking;


EXPLAIN
SELECT
    r.room_id,
    r.room_number,
    r.room_type,
    r.available_beds,
    r.rent
FROM room r
JOIN hostel h
    ON r.hostel_id = h.hostel_id
WHERE h.status = 'Approved'
  AND r.status = 'Available'
  AND r.available_beds > 0;
  
  
  
EXPLAIN
SELECT
    room_id,
    room_number,
    room_type,
    available_beds,
    rent
FROM room
WHERE status = 'Available'
  AND available_beds > 0;
  
  
  
  
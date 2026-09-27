USE nearhub;

SHOW TABLES;

SELECT * FROM student;
SELECT * FROM hostel_owner;
SELECT * FROM mess_owner;
SELECT * FROM admin;
SELECT * FROM hostel;
SELECT * FROM room;
DESC room;
SELECT * FROM facility;
SELECT * FROM hostel_facility;
SELECT * FROM mess;
DESC mess;
SELECT * FROM menu;

DESCRIBE menu;
SELECT * FROM meal_plan;
desc meal_plan;
SELECT * FROM room_booking;
desc room_booking;

SELECT * FROM meal_subscription;
desc meal_subscription;

SELECT * FROM payment;
SELECT * FROM feedback;
desc feedback;  
SELECT * FROM student_preference;

SELECT
    h.hostel_name,
    ho.name AS owner_name
FROM hostel h
JOIN hostel_owner ho
ON h.hostel_owner_id = ho.hostel_owner_id;

SELECT
    h.hostel_name,
    r.room_number,
    r.room_type,
    r.rent,
    r.available_beds
FROM hostel h
JOIN room r
ON h.hostel_id = r.hostel_id;

SELECT
    m.mess_name,
    mo.name AS mess_owner,
    ho.name AS hostel_owner
FROM mess m
LEFT JOIN mess_owner mo
ON m.mess_owner_id = mo.mess_owner_id
LEFT JOIN hostel_owner ho
ON m.hostel_owner_id = ho.hostel_owner_id;

SELECT
    s.name AS student_name,
    h.hostel_name,
    r.room_number,
    r.room_type,
    rb.start_date,
    rb.end_date,
    rb.status
FROM room_booking rb
JOIN student s
ON rb.student_id = s.student_id
JOIN room r
ON rb.room_id = r.room_id
JOIN hostel h
ON r.hostel_id = h.hostel_id;

use nearhub;
SELECT
    room_id,
    room_number,
    capacity,
    available_beds,
    status
FROM room
WHERE room_id = 1;

SELECT
    s.name AS student_name,
    m.mess_name,
    mp.plan_name,
    mp.price,
    ms.start_date,
    ms.end_date,
    ms.status
FROM meal_subscription ms
JOIN student s
ON ms.student_id = s.student_id
JOIN meal_plan mp
ON ms.plan_id = mp.plan_id
JOIN mess m
ON mp.mess_id = m.mess_id;

SELECT
    s.name AS student_name,
    f.feedback_type,
    f.rating,
    f.feedback_text,
    h.hostel_name,
    m.mess_name,
    f.status
FROM feedback f
JOIN student s
ON f.student_id = s.student_id
LEFT JOIN hostel h
ON f.hostel_id = h.hostel_id
LEFT JOIN mess m




ON f.mess_id = m.mess_id;


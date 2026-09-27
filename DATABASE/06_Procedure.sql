USE nearhub;

DROP PROCEDURE IF EXISTS get_student_booking_details;

DELIMITER $$

CREATE PROCEDURE get_student_booking_details(
    IN p_student_id INT
)
BEGIN

    SELECT
        rb.booking_id,
        rb.student_id,
        s.name AS student_name,
        rb.room_id,
        r.room_number,
        r.room_type,
        r.rent,
        h.hostel_id,
        h.hostel_name,
        h.location,
        h.contact_no AS hostel_contact,
        rb.booking_date,
        rb.start_date,
        rb.end_date,
        rb.status

    FROM room_booking rb

    JOIN student s
        ON rb.student_id = s.student_id

    JOIN room r
        ON rb.room_id = r.room_id

    JOIN hostel h
        ON r.hostel_id = h.hostel_id

    WHERE rb.student_id = p_student_id

    ORDER BY rb.booking_id DESC;

END$$

DELIMITER ;

CALL get_student_booking_details(1);




DROP PROCEDURE IF EXISTS get_available_rooms;

DELIMITER $$

CREATE PROCEDURE get_available_rooms(
    IN p_location VARCHAR(100)
)
BEGIN

    SELECT
        r.room_id,
        r.room_number,
        r.room_type,
        r.capacity,
        r.available_beds,
        r.rent,

        h.hostel_id,
        h.hostel_name,
        h.location,
        h.contact_no AS hostel_contact

    FROM room r

    JOIN hostel h
        ON r.hostel_id = h.hostel_id

    WHERE r.status = 'Available'
      AND r.available_beds > 0
      AND h.status = 'Approved'
      AND (
          p_location IS NULL
          OR p_location = ''
          OR h.location = p_location
      )

    ORDER BY r.rent ASC;

END$$

DELIMITER ;

CALL get_available_rooms(NULL);
CALL get_available_rooms('Wakad');



DROP PROCEDURE IF EXISTS get_student_subscriptions;

DELIMITER $$

CREATE PROCEDURE get_student_subscriptions(
    IN p_student_id INT
)
BEGIN

    SELECT
        ms.subscription_id,
        ms.student_id,

        s.name AS student_name,

        ms.plan_id,
        mp.plan_name,
        mp.price,
        mp.meals_per_day,
        mp.duration,

        m.mess_id,
        m.mess_name,
        m.location,
        m.contact_no AS mess_contact,

        ms.start_date,
        ms.end_date,
        ms.status

    FROM meal_subscription ms

    JOIN student s
        ON ms.student_id = s.student_id

    JOIN meal_plan mp
        ON ms.plan_id = mp.plan_id

    JOIN mess m
        ON mp.mess_id = m.mess_id

    WHERE ms.student_id = p_student_id

    ORDER BY ms.subscription_id DESC;

END$$

DELIMITER ;


CALL get_student_subscriptions(1);



SHOW PROCEDURE STATUS
WHERE Db = 'nearhub';








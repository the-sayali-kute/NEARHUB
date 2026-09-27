CREATE OR REPLACE VIEW approved_hostels_view AS
SELECT
    h.hostel_id,
    h.hostel_name,
    h.address,
    h.location,
    h.description,
    h.gender_type,
    h.contact_no,
    h.hostel_owner_id,
    ho.name AS owner_name,
    ho.email AS owner_email
FROM hostel h
JOIN hostel_owner ho
    ON h.hostel_owner_id = ho.hostel_owner_id
WHERE h.status = 'Approved';

SELECT * FROM approved_hostels_view;

CREATE OR REPLACE VIEW approved_messes_view AS
SELECT
    m.mess_id,
    m.mess_name,
    m.address,
    m.location,
    m.description,
    m.food_type,
    m.contact_no,
    m.hostel_owner_id,
    m.mess_owner_id,
    CASE
        WHEN m.hostel_owner_id IS NOT NULL
            THEN ho.name
        WHEN m.mess_owner_id IS NOT NULL
            THEN mo.name
    END AS owner_name
FROM mess m
LEFT JOIN hostel_owner ho
    ON m.hostel_owner_id = ho.hostel_owner_id
LEFT JOIN mess_owner mo
    ON m.mess_owner_id = mo.mess_owner_id
WHERE m.status = 'Approved';

SELECT * FROM approved_messes_view;

CREATE OR REPLACE VIEW available_rooms_view AS
SELECT
    r.room_id,
    r.hostel_id,
    h.hostel_name,
    h.location,
    h.contact_no AS hostel_contact,
    r.room_number,
    r.room_type,
    r.capacity,
    r.available_beds,
    r.rent,
    r.status
FROM room r
JOIN hostel h
    ON r.hostel_id = h.hostel_id
WHERE r.status = 'Available'
  AND r.available_beds > 0
  AND h.status = 'Approved';

select * from available_rooms_view;

CREATE OR REPLACE VIEW student_booking_details_view AS
SELECT
    rb.booking_id,
    rb.student_id,
    s.name AS student_name,
    s.email AS student_email,
    s.phone AS student_phone,

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
    ON r.hostel_id = h.hostel_id;


SELECT * FROM student_booking_details_view;

CREATE OR REPLACE VIEW active_meal_subscriptions_view AS
SELECT
    ms.subscription_id,

    ms.student_id,
    s.name AS student_name,
    s.email AS student_email,

    ms.plan_id,
    mp.plan_name,
    mp.price,
    mp.meals_per_day,
    mp.duration,

    m.mess_id,
    m.mess_name,
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

WHERE ms.status = 'Active'
  AND m.status = 'Approved';

select * from active_meal_subscriptions_view;

CREATE OR REPLACE VIEW student_preferences_view AS
SELECT
    sp.preference_id,
    sp.student_id,
    s.name AS student_name,
    s.email AS student_email,

    sp.preferred_location,
    sp.max_budget,
    sp.room_type,
    sp.food_type,
    sp.meal_preference,
    sp.required_facility

FROM student_preference sp

JOIN student s
    ON sp.student_id = s.student_id;

SELECT * FROM student_preferences_view;

CREATE OR REPLACE VIEW approved_meal_plans_view AS
SELECT
    mp.plan_id,
    mp.mess_id,
    m.mess_name,
    m.location,
    m.contact_no AS mess_contact,

    mp.plan_name,
    mp.price,
    mp.meals_per_day,
    mp.duration

FROM meal_plan mp

JOIN mess m
    ON mp.mess_id = m.mess_id

WHERE m.status = 'Approved';

SELECT * FROM approved_meal_plans_view;

SHOW FULL TABLES WHERE Table_type = 'VIEW';



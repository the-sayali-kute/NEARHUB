USE nearhub;

INSERT INTO student
(name, email, phone, password_hash, gender, college, course, year, budget, preferred_location)
VALUES
('Aarav Patil', 'aarav@gmail.com', '9876543210', 'HASHED_PASSWORD_1', 'Male', 'VIT Pune', 'AI & Data Science', 2, 8000, 'Viman Nagar'),
('Sneha Kulkarni', 'sneha@gmail.com', '9876543211', 'HASHED_PASSWORD_2', 'Female', 'MIT WPU', 'Computer Engineering', 2, 10000, 'Kothrud'),
('Riya Sharma', 'riya@gmail.com', '9876543212', 'HASHED_PASSWORD_3', 'Female', 'PCCOE', 'AI & Data Science', 3, 9000, 'Wakad'),
('Aditya Joshi', 'aditya@gmail.com', '9876543213', 'HASHED_PASSWORD_4', 'Male', 'VIT Pune', 'Computer Engineering', 2, 7500, 'Viman Nagar'),
('Om Deshmukh', 'om@gmail.com', '9876543214', 'HASHED_PASSWORD_5', 'Male', 'COEP', 'IT', 3, 12000, 'Shivajinagar');

INSERT INTO hostel_owner
(name, email, phone, password_hash, address)
VALUES
('Rajesh Sharma', 'rajesh@nearhub.com', '9000000001', 'HASHED_OWNER_1', 'Pune'),
('Amit Patil', 'amit@nearhub.com', '9000000002', 'HASHED_OWNER_2', 'Pune'),
('Neha Joshi', 'neha@nearhub.com', '9000000003', 'HASHED_OWNER_3', 'Pune');


INSERT INTO mess_owner
(name, email, phone, password_hash, address)
VALUES
('Suresh More', 'suresh@nearhub.com', '9100000001', 'HASHED_MESS_1', 'Pune'),
('Priya Shah', 'priya@nearhub.com', '9100000002', 'HASHED_MESS_2', 'Pune'),
('Kiran Jadhav', 'kiran@nearhub.com', '9100000003', 'HASHED_MESS_3', 'Pune');

INSERT INTO admin
(name, email, password_hash)
VALUES
('NearHub Admin', 'admin@nearhub.com', 'HASHED_ADMIN_1');


INSERT INTO hostel
(hostel_owner_id, hostel_name, address, location, description, gender_type, contact_no, status)
VALUES
(1, 'Sunrise Student Hostel', 'Viman Nagar, Pune', 'Viman Nagar',
 'Comfortable hostel for college students with modern facilities.',
 'Boys', '9200000001', 'Approved'),

(2, 'Green Valley Girls Hostel', 'Kothrud, Pune', 'Kothrud',
 'Safe and student-friendly accommodation.',
 'Girls', '9200000002', 'Approved'),

(3, 'Urban Nest Residency', 'Wakad, Pune', 'Wakad',
 'Affordable student accommodation near colleges.',
 'Co-ed', '9200000003', 'Approved'),

(1, 'Campus Stay', 'Shivajinagar, Pune', 'Shivajinagar',
 'Student hostel with study facilities and Wi-Fi.',
 'Boys', '9200000004', 'Approved');

 INSERT INTO room
(hostel_id, room_number, room_type, capacity, rent, available_beds, status)
VALUES
(1, '101', 'Single', 1, 8000, 1, 'Available'),
(1, '102', 'Double', 2, 6500, 2, 'Available'),
(1, '103', 'Triple', 3, 5500, 2, 'Available'),

(2, '201', 'Single', 1, 9500, 1, 'Available'),
(2, '202', 'Double', 2, 8000, 1, 'Available'),

(3, '301', 'Double', 2, 7000, 2, 'Available'),
(3, '302', 'Triple', 3, 6000, 3, 'Available'),

(4, '401', 'Single', 1, 10000, 1, 'Available'),
(4, '402', 'Double', 2, 8500, 2, 'Available');

INSERT INTO facility
(facility_name, description)
VALUES
('Wi-Fi', 'High-speed internet access'),
('Laundry', 'Laundry service available'),
('Parking', 'Two-wheeler parking'),
('CCTV', '24-hour CCTV surveillance'),
('Security', '24-hour security service'),
('Study Room', 'Dedicated study area'),
('Gym', 'Gym facility available'),
('Power Backup', 'Power backup facility');

INSERT INTO hostel_facility
(hostel_id, facility_id)
VALUES
(1, 1),
(1, 2),
(1, 4),
(1, 5),
(1, 8),

(2, 1),
(2, 4),
(2, 5),
(2, 6),
(2, 8),

(3, 1),
(3, 2),
(3, 3),
(3, 4),

(4, 1),
(4, 5),
(4, 6),
(4, 8);

INSERT INTO mess
(hostel_owner_id, mess_owner_id, mess_name, location, address, description, contact_no, food_type, status)
VALUES
(1, NULL, 'Sunrise Mess', 'Viman Nagar',
 'Sunrise Student Hostel, Viman Nagar, Pune',
 'Mess operated by the hostel owner.',
 '9300000001', 'Both', 'Approved'),

(2, NULL, 'Green Valley Dining', 'Kothrud',
 'Green Valley Girls Hostel, Kothrud, Pune',
 'Dining facility provided by hostel owner.',
 '9300000002', 'Veg', 'Approved');


INSERT INTO mess
(hostel_owner_id, mess_owner_id, mess_name, location, address,
 description, contact_no, food_type, status)
VALUES
(NULL, 1, 'Student Food Hub', 'Wakad', 'Pune',
 'Affordable and healthy meals for students',
 '9300000003', 'Veg', 'Approved'),

(NULL, 2, 'Campus Bites', 'Baner', 'Pune',
 'Student-friendly dining with multiple meal options',
 '9300000004', 'Both', 'Approved');


 INSERT INTO menu
(mess_id, day, meal_type, food_items, description)
VALUES
(1, 'Monday', 'Breakfast', 'Poha, Tea, Banana', 'Healthy breakfast'),
(1, 'Monday', 'Lunch', 'Dal, Rice, Roti, Sabzi', 'Regular lunch'),
(1, 'Monday', 'Dinner', 'Paneer, Roti, Rice, Salad', 'Dinner'),

(2, 'Tuesday', 'Breakfast', 'Upma, Tea, Fruits', 'Breakfast'),
(2, 'Tuesday', 'Lunch', 'Dal, Rice, Roti, Vegetable', 'Lunch'),
(2, 'Tuesday', 'Dinner', 'Pulao, Raita, Roti', 'Dinner'),

(3, 'Wednesday', 'Breakfast', 'Idli, Sambar, Tea', 'Breakfast'),
(3, 'Wednesday', 'Lunch', 'Rajma, Rice, Roti, Salad', 'Lunch'),
(3, 'Wednesday', 'Dinner', 'Veg Biryani, Raita', 'Dinner'),

(4, 'Thursday', 'Breakfast', 'Paratha, Curd, Tea', 'Breakfast'),
(4, 'Thursday', 'Lunch', 'Dal, Rice, Roti, Paneer', 'Lunch'),
(4, 'Thursday', 'Dinner', 'Chapati, Mix Veg, Dal', 'Dinner');

INSERT INTO meal_plan
(mess_id, plan_name, meals_per_day, price, duration, description)
VALUES
(1, 'Monthly Full Plan', 3, 3500, 30, 'Breakfast, lunch and dinner'),
(1, 'Monthly Lunch Dinner', 2, 2800, 30, 'Lunch and dinner'),
(2, 'Monthly Veg Plan', 3, 3200, 30, 'Three vegetarian meals daily'),
(3, 'Weekly Plan', 3, 900, 7, 'Full meal plan for one week'),
(4, 'Monthly Student Plan', 3, 3000, 30, 'Affordable monthly meal plan');

INSERT INTO room_booking
(student_id, room_id, booking_date, start_date, end_date, status)
VALUES
(1, 2, '2026-09-20', '2026-10-01', '2027-03-31', 'Confirmed'),
(2, 4, '2026-09-20', '2026-10-01', '2027-03-31', 'Confirmed'),
(3, 6, '2026-09-20', '2026-10-05', '2027-04-05', 'Pending');

INSERT INTO meal_subscription
(student_id, plan_id, start_date, end_date, status)
VALUES
(1, 1, '2026-10-01', '2026-10-31', 'Active'),
(2, 3, '2026-10-01', '2026-10-31', 'Active'),
(3, 4, '2026-10-05', '2026-10-11', 'Active');

INSERT INTO payment
(student_id, amount, payment_type, booking_id, subscription_id, payment_method, payment_status, transaction_id)
VALUES
(1, 6500, 'Room Booking', 1, NULL, 'UPI', 'Success', 'TXN10001'),
(2, 9500, 'Room Booking', 2, NULL, 'Card', 'Success', 'TXN10002'),
(1, 3500, 'Meal Subscription', NULL, 1, 'UPI', 'Success', 'TXN10003'),
(2, 3200, 'Meal Subscription', NULL, 2, 'UPI', 'Success', 'TXN10004');

INSERT INTO feedback
(student_id, hostel_id, mess_id, rating, feedback_text, feedback_type, status)
VALUES
(1, 1, NULL, 5, 'Good hostel with clean rooms and Wi-Fi.', 'Review', 'Resolved'),

(2, NULL, 2, 4, 'Food quality is good and menu has variety.', 'Review', 'Resolved'),

(3, 3, NULL, NULL, 'Water supply was unavailable for several hours.', 'Complaint', 'Pending'),

(4, NULL, 3, NULL, 'Dinner was served late today.', 'Complaint', 'Pending');

INSERT INTO student_preference
(student_id, preferred_location, max_budget, room_type, food_type, meal_preference, required_facility)
VALUES
(1, 'Viman Nagar', 8000, 'Double', 'Both', 'All', 'Wi-Fi, Security'),
(2, 'Kothrud', 10000, 'Single', 'Veg', 'All', 'Wi-Fi, Study Room'),
(3, 'Wakad', 9000, 'Double', 'Veg', 'Dinner', 'Wi-Fi, Laundry'),
(4, 'Viman Nagar', 7500, 'Triple', 'Both', 'Lunch', 'Wi-Fi'),
(5, 'Shivajinagar', 12000, 'Single', 'Veg', 'All', 'Gym, Wi-Fi');




SELECT 'student' AS table_name, COUNT(*) AS records FROM student
UNION ALL
SELECT 'hostel_owner', COUNT(*) FROM hostel_owner
UNION ALL
SELECT 'mess_owner', COUNT(*) FROM mess_owner
UNION ALL
SELECT 'admin', COUNT(*) FROM admin
UNION ALL
SELECT 'hostel', COUNT(*) FROM hostel
UNION ALL
SELECT 'room', COUNT(*) FROM room
UNION ALL
SELECT 'facility', COUNT(*) FROM facility
UNION ALL
SELECT 'hostel_facility', COUNT(*) FROM hostel_facility
UNION ALL
SELECT 'mess', COUNT(*) FROM mess
UNION ALL
SELECT 'menu', COUNT(*) FROM menu
UNION ALL
SELECT 'meal_plan', COUNT(*) FROM meal_plan
UNION ALL
SELECT 'room_booking', COUNT(*) FROM room_booking
UNION ALL
SELECT 'meal_subscription', COUNT(*) FROM meal_subscription
UNION ALL
SELECT 'payment', COUNT(*) FROM payment
UNION ALL
SELECT 'feedback', COUNT(*) FROM feedback
UNION ALL
SELECT 'student_preference', COUNT(*) FROM student_preference;


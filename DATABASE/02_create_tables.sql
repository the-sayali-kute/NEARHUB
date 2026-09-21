USE nearhub;

CREATE TABLE student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    college VARCHAR(150),
    course VARCHAR(100),
    year INT,
    budget DECIMAL(10,2),
    preferred_location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hostel_owner (
    hostel_owner_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mess_owner (
    mess_owner_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hostel (
    hostel_id INT AUTO_INCREMENT PRIMARY KEY,
    hostel_owner_id INT NOT NULL,
    hostel_name VARCHAR(150) NOT NULL,
    address VARCHAR(255) NOT NULL,
    location VARCHAR(100) NOT NULL,
    description TEXT,
    gender_type ENUM('Boys', 'Girls', 'Co-ed') NOT NULL,
    contact_no VARCHAR(15),
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',

    FOREIGN KEY (hostel_owner_id)
        REFERENCES hostel_owner(hostel_owner_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE room (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    hostel_id INT NOT NULL,
    room_number VARCHAR(20) NOT NULL,
    room_type ENUM('Single', 'Double', 'Triple', 'Four Sharing') NOT NULL,
    capacity INT NOT NULL,
    rent DECIMAL(10,2) NOT NULL,
    available_beds INT NOT NULL,
    status ENUM('Available', 'Full', 'Maintenance') DEFAULT 'Available',

    UNIQUE (hostel_id, room_number),

    FOREIGN KEY (hostel_id)
        REFERENCES hostel(hostel_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (capacity > 0),
    CHECK (rent >= 0),
    CHECK (available_beds >= 0),
    CHECK (available_beds <= capacity)
);

CREATE TABLE facility (
    facility_id INT AUTO_INCREMENT PRIMARY KEY,
    facility_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE hostel_facility (
    hostel_id INT NOT NULL,
    facility_id INT NOT NULL,

    PRIMARY KEY (hostel_id, facility_id),

    FOREIGN KEY (hostel_id)
        REFERENCES hostel(hostel_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (facility_id)
        REFERENCES facility(facility_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE mess (
    mess_id INT AUTO_INCREMENT PRIMARY KEY,
    hostel_owner_id INT NULL,
    mess_owner_id INT NULL,
    mess_name VARCHAR(150) NOT NULL,
    location VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    description TEXT,
    contact_no VARCHAR(15),
    food_type ENUM('Veg', 'Non-Veg', 'Both') NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',

    FOREIGN KEY (hostel_owner_id)
        REFERENCES hostel_owner(hostel_owner_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (mess_owner_id)
        REFERENCES mess_owner(mess_owner_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE menu (
    menu_id INT AUTO_INCREMENT PRIMARY KEY,
    mess_id INT NOT NULL,
    day ENUM(
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ) NOT NULL,
    meal_type ENUM('Breakfast', 'Lunch', 'Snacks', 'Dinner') NOT NULL,
    food_items TEXT NOT NULL,
    description VARCHAR(255),

    FOREIGN KEY (mess_id)
        REFERENCES mess(mess_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE meal_plan (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    mess_id INT NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    meals_per_day INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    duration INT NOT NULL,
    description VARCHAR(255),

    FOREIGN KEY (mess_id)
        REFERENCES mess(mess_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (meals_per_day > 0),
    CHECK (price >= 0),
    CHECK (duration > 0)
);

CREATE TABLE room_booking (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    room_id INT NOT NULL,
    booking_date DATE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status ENUM('Pending', 'Confirmed', 'Cancelled', 'Completed') DEFAULT 'Pending',

    FOREIGN KEY (student_id)
        REFERENCES student(student_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (room_id)
        REFERENCES room(room_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK (end_date IS NULL OR end_date > start_date)
);

CREATE TABLE meal_subscription (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    plan_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('Active', 'Expired', 'Cancelled') DEFAULT 'Active',

    FOREIGN KEY (student_id)
        REFERENCES student(student_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (plan_id)
        REFERENCES meal_plan(plan_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK (end_date > start_date)
);

CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_type ENUM('Room Booking', 'Meal Subscription') NOT NULL,

    booking_id INT NULL,
    subscription_id INT NULL,

    payment_method ENUM('UPI', 'Card', 'Net Banking', 'Cash') NOT NULL,
    payment_status ENUM('Pending', 'Success', 'Failed', 'Refunded') DEFAULT 'Pending',
    transaction_id VARCHAR(100) UNIQUE,

    FOREIGN KEY (student_id)
        REFERENCES student(student_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (booking_id)
        REFERENCES room_booking(booking_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (subscription_id)
        REFERENCES meal_subscription(subscription_id)
        ON DELETE RESTRICT,

    CHECK (
        (payment_type = 'Room Booking'
         AND booking_id IS NOT NULL
         AND subscription_id IS NULL)
        OR
        (payment_type = 'Meal Subscription'
         AND subscription_id IS NOT NULL
         AND booking_id IS NULL)
    ),

    CHECK (amount > 0)
);

CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    hostel_id INT NULL,
    mess_id INT NULL,
    rating INT NULL,
    feedback_text TEXT NOT NULL,
    feedback_type ENUM('Review', 'Complaint') NOT NULL,
    feedback_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Resolved', 'Rejected') DEFAULT 'Pending',

    FOREIGN KEY (student_id)
        REFERENCES student(student_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (hostel_id)
        REFERENCES hostel(hostel_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (mess_id)
        REFERENCES mess(mess_id)
        ON DELETE RESTRICT,

    CHECK (
        (hostel_id IS NOT NULL AND mess_id IS NULL)
        OR
        (hostel_id IS NULL AND mess_id IS NOT NULL)
    ),

    CHECK (
        (feedback_type = 'Review' AND rating BETWEEN 1 AND 5)
        OR
        (feedback_type = 'Complaint' AND rating IS NULL)
    )
);

CREATE TABLE student_preference (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    preferred_location VARCHAR(100),
    max_budget DECIMAL(10,2),
    room_type ENUM('Single', 'Double', 'Triple', 'Four Sharing'),
    food_type ENUM('Veg', 'Non-Veg', 'Both'),
    meal_preference ENUM(
        'Breakfast',
        'Lunch',
        'Snacks',
        'Dinner',
        'All'
    ),
    required_facility VARCHAR(255),

    FOREIGN KEY (student_id)
        REFERENCES student(student_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (max_budget IS NULL OR max_budget >= 0)
);



SHOW TABLES;

SELECT COUNT(*) AS total_tables
FROM information_schema.tables
WHERE table_schema = 'nearhub';

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'nearhub'
ORDER BY table_name;


-- student
--       ↓
-- hostel_owner
--       ↓
-- mess_owner
--       ↓
-- admin
--       ↓
-- hostel
--       ↓
-- room
--       ↓
-- facility
--       ↓
-- hostel_facility
--       ↓
-- mess
--       ↓
-- menu
--       ↓
-- meal_plan
--       ↓
-- room_booking
--       ↓
-- meal_subscription
--       ↓
-- payment
--       ↓
-- feedback
--       ↓
-- student_preference
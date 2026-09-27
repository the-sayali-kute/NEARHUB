USE nearhub;

DROP TRIGGER IF EXISTS after_booking_insert;

DELIMITER $$

CREATE TRIGGER after_booking_insert
AFTER INSERT ON room_booking
FOR EACH ROW
BEGIN
    UPDATE room
    SET available_beds = available_beds - 1
    WHERE room_id = NEW.room_id;
END$$

DELIMITER ;


DROP TRIGGER IF EXISTS after_booking_cancel;

DELIMITER $$

CREATE TRIGGER after_booking_cancel
AFTER UPDATE ON room_booking
FOR EACH ROW
BEGIN
    IF OLD.status <> 'Cancelled'
       AND NEW.status = 'Cancelled' THEN

        UPDATE room
        SET available_beds = available_beds + 1
        WHERE room_id = NEW.room_id;

    END IF;
END$$

DELIMITER ;


DROP TRIGGER IF EXISTS before_mess_insert;

DELIMITER $$

CREATE TRIGGER before_mess_insert
BEFORE INSERT ON mess
FOR EACH ROW
BEGIN

    IF (NEW.hostel_owner_id IS NULL AND NEW.mess_owner_id IS NULL)
       OR
       (NEW.hostel_owner_id IS NOT NULL AND NEW.mess_owner_id IS NOT NULL) THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A mess must have exactly one owner';

    END IF;

END$$

DELIMITER ;


DROP TRIGGER IF EXISTS before_mess_update;

DELIMITER $$

CREATE TRIGGER before_mess_update
BEFORE UPDATE ON mess
FOR EACH ROW
BEGIN

    IF (NEW.hostel_owner_id IS NULL AND NEW.mess_owner_id IS NULL)
       OR
       (NEW.hostel_owner_id IS NOT NULL AND NEW.mess_owner_id IS NOT NULL) THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A mess must have exactly one owner';

    END IF;

END$$

DELIMITER ;


SHOW TRIGGERS FROM nearhub;





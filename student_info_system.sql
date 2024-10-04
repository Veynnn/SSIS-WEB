CREATE DATABASE IF NOT EXISTS ssis;
USE ssis;

DROP TRIGGER IF EXISTS trg_delete_college_courses;
DROP TRIGGER IF EXISTS trg_delete_college_students;

--college
CREATE TABLE IF NOT EXISTS colleges (
    college_code VARCHAR(10) PRIMARY KEY,
    college_name VARCHAR(100) NOT NULL
);

--courses
CREATE TABLE IF NOT EXISTS courses (
    course_code VARCHAR(15) PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    college_code VARCHAR(10),
    CONSTRAINT fk_courses_colleges FOREIGN KEY (college_code)
        REFERENCES colleges(college_code)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

--Students
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(9) PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    year_lvl ENUM('1st year', '2nd year', '3rd year', '4th year') NOT NULL,
    course_code VARCHAR(15),
    college_code VARCHAR(10),
    CONSTRAINT chk_student_id CHECK (REGEXP_LIKE(student_id, '^[0-9]{4}-[0-9]{4}$')),
    CONSTRAINT fk_students_courses FOREIGN KEY (course_code)
        REFERENCES courses(course_code)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_students_colleges FOREIGN KEY (college_code)
        REFERENCES colleges(college_code)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);


DELIMITER //
CREATE TRIGGER trg_delete_college_courses
BEFORE DELETE ON colleges
FOR EACH ROW
BEGIN
    UPDATE courses
    SET college_code = NULL
    WHERE college_code = OLD.college_code;
END;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER trg_delete_college_students
BEFORE DELETE ON colleges
FOR EACH ROW
BEGIN
    UPDATE students
    SET college_code = NULL
    WHERE college_code = OLD.college_code;
END;
//
DELIMITER ;


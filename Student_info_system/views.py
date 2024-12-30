from models import execute_query, fetch_query
from cloudinary import uploader
import math



#--------------------- COLLEGEZZZ----------------------


def get_colleges_search(search_keyword, search_by):
    query = f"SELECT * FROM colleges WHERE {search_by} LIKE %s"
    return fetch_query(query, ('%' + search_keyword + '%',))

# Function to check if a college name exists
def check_college_name_existence(college_name):
    query = "SELECT * FROM colleges WHERE college_name = %s"
    result = fetch_query(query, (college_name,))
    return result

# Function to check if a college code exists
def check_college_code_existence(college_code):
    query = "SELECT * FROM colleges WHERE college_code = %s"
    result = fetch_query(query, (college_code,))
    return result

# Function to add a new college
def add_colleges(college_name, college_code):
    query = """
    INSERT INTO colleges (college_name, college_code)
    VALUES (%s, %s)
    """
    execute_query(query, (college_name, college_code))

# Function to update college information
def update_college_query(college_name, new_college_code, old_college_code):
    query = """
    UPDATE colleges 
    SET college_name = %s, college_code = %s
    WHERE college_code = %s
    """
    execute_query(query, (college_name, new_college_code, old_college_code))

# Function to update courses with the new college code
def update_courses_query(new_college_code, old_college_code):
    query = """
    UPDATE courses 
    SET college_code = %s
    WHERE college_code = %s
    """
    execute_query(query, (new_college_code, old_college_code))

# Function to update students with the new college code
def update_students_query(new_college_code, old_college_code):
    query = """
    UPDATE students 
    SET college_code = %s
    WHERE college_code = %s
    """
    execute_query(query, (new_college_code, old_college_code))

def remove_colleges(college_code):
    update_students_query = """
    UPDATE students
    SET course_code = NULL
    WHERE course_code IN (
        SELECT course_code FROM courses WHERE college_code = %s
    )
    """
    execute_query(update_students_query, (college_code,))

    delete_college_query = "DELETE FROM colleges WHERE college_code = %s"
    execute_query(delete_college_query, (college_code,))




#--------------------- COURSEZZZ----------------------

def get_courses(search_by, search_keyword):
    query = f"SELECT * FROM courses WHERE {search_by} LIKE %s"
    return fetch_query(query, ('%' + search_keyword + '%',))

def check_existing_course(course_name, college_code):
    query_name_check = "SELECT * FROM courses WHERE course_name = %s AND college_code = %s"
    return fetch_query(query_name_check, (course_name, college_code))

def check_existing_code(course_code):
    query_code_check_global = "SELECT * FROM courses WHERE course_code = %s"
    return fetch_query(query_code_check_global, (course_code,))

def insert_new_course(course_name, course_code, college_code):
    query = "INSERT INTO courses (course_name, course_code, college_code) VALUES (%s, %s, %s)"
    execute_query(query, (course_name, course_code, college_code))

def get_colleges():
    query = "SELECT college_code, college_name FROM colleges"
    return fetch_query(query)

def get_course(course_code):
    query = "SELECT course_code, course_name, college_code FROM courses WHERE course_code = %s"
    return fetch_query(query, (course_code,))

def update_course(course_name, new_course_code, college_code, course_code):
    query = """
    UPDATE courses 
    SET course_name = %s, course_code = %s, college_code = %s
    WHERE course_code = %s
    """
    execute_query(query, (course_name, new_course_code, college_code, course_code))

def update_students_course(course_code, college_code):
    query = """
    UPDATE students 
    SET college_code = %s
    WHERE course_code = %s
    """
    execute_query(query, (college_code, course_code))

def delete_course(course_code):
    update_query = "UPDATE students SET course_code = NULL WHERE course_code = %s"
    execute_query(update_query, (course_code,))
    
    delete_query = "DELETE FROM courses WHERE course_code = %s"
    execute_query(delete_query, (course_code,))





#--------------------- STUDENTZZZ----------------------

DEFAULT_PROFILE_IMAGE = 'static/default_pic.jpg'

def get_total_students(search_keyword, search_by):
    count_query = f"""
    SELECT COUNT(*) 
    FROM students 
    WHERE {search_by} LIKE %s
    """
    return fetch_query(count_query, ('%' + search_keyword + '%',))[0]['COUNT(*)']

def get_students(search_keyword, search_by, page, per_page):
    offset = (page - 1) * per_page
    query = f"""
    SELECT 
        students.student_id, 
        students.student_name, 
        students.gender, 
        students.year_lvl, 
        COALESCE(students.image_url, %s) AS image_url, 
        courses.course_code, 
        colleges.college_code, 
        courses.course_name, 
        colleges.college_name
    FROM students
    LEFT JOIN courses ON students.course_code = courses.course_code
    LEFT JOIN colleges ON students.college_code = colleges.college_code
    WHERE students.{search_by} LIKE %s
    LIMIT %s OFFSET %s
    """
    return fetch_query(query, (DEFAULT_PROFILE_IMAGE, '%' + search_keyword + '%', per_page, offset))

def check_student_existence(student_id, course_code, college_code):
    query_id_check = "SELECT * FROM students WHERE student_id = %s"
    existing_id = fetch_query(query_id_check, (student_id,))

    query_course_check = "SELECT * FROM courses WHERE course_code = %s AND college_code = %s"
    existing_course = fetch_query(query_course_check, (course_code, college_code))

    return existing_id, existing_course

def add_student_to_db(student_id, student_name, gender, year_lvl, course_code, college_code, image_url):
    query = """
    INSERT INTO students (student_id, student_name, gender, year_lvl, course_code, college_code, image_url) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    execute_query(query, (student_id, student_name, gender, year_lvl, course_code, college_code, image_url))

def update_student_in_db(student_id, student_name, gender, year_lvl, course_code, college_code, image_url):
    query = """
    UPDATE students 
    SET student_name = %s, gender = %s, year_lvl = %s, course_code = %s, college_code = %s, image_url = %s
    WHERE student_id = %s
    """
    execute_query(query, (student_name, gender, year_lvl, course_code, college_code, image_url, student_id))

def remove_student_from_db(student_id):
    delete_query = "DELETE FROM students WHERE student_id = %s"
    execute_query(delete_query, (student_id,))

def get_colleges():
    college_query = "SELECT college_code, college_name FROM colleges"
    return fetch_query(college_query)

def get_courses_by_college(college_code):
    course_query = "SELECT course_code, course_name FROM courses WHERE college_code = %s"
    return fetch_query(course_query, (college_code,))

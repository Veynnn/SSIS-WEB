from flask import Blueprint, render_template, request, redirect, url_for, flash, abort,jsonify
from models import execute_query, fetch_query
import math



from models import execute_query, fetch_query
from cloudinary_config import upload_result,cloudinary
from cloudinary import uploader
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

students_bp = Blueprint(
    'students',
    __name__,
    template_folder='templates',
    static_folder='Student_info_system/static',  
    static_url_path='/static'
)


template_path = os.path.join(project_root, 'templates')
static_path = os.path.join(project_root, 'static')

DEFAULT_PROFILE_IMAGE = 'static/default_pic.jpg'

#--------------------- Student Page ----------------------

@students_bp.route('/students', methods=['GET'])
def students():
    search_keyword = request.args.get('search', '')
    search_by = request.args.get('search_by', 'student_id')
    page = int(request.args.get('page', 1))  
    per_page = 50  
    if 'student_button' in request.args:
        return redirect(url_for('students.students'))

    valid_search_fields = ['student_id', 'student_name', 'gender', 'year_lvl', 'course_code', 'college_code']
    if search_by not in valid_search_fields:
        search_by = 'student_id'

    count_query = f"""
    SELECT COUNT(*) 
    FROM students 
    WHERE {search_by} LIKE %s
    """
    total_students = fetch_query(count_query, ('%' + search_keyword + '%',))[0]['COUNT(*)']

    total_pages = math.ceil(total_students / per_page)
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
    students = fetch_query(query, (DEFAULT_PROFILE_IMAGE, '%' + search_keyword + '%', per_page, offset))

    default_profile_image = url_for('static', filename='default_profile.png')
    
    return render_template('students.html', 
                           students=students, 
                           default_profile_image=default_profile_image,
                           search_keyword=search_keyword,
                           search_by=search_by,
                           page=page,
                           total_pages=total_pages)


#--------------------- Add Student ----------------------
@students_bp.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_id = request.form['student_id'].upper()
        student_name = request.form['student_name'].upper()
        gender = request.form['gender'].upper()
        year_lvl = request.form['year_lvl'].upper()
        course_code = request.form['course_code'].upper()
        college_code = request.form['college_code'].upper()

        image_file = request.files.get('image')
        image_url = DEFAULT_PROFILE_IMAGE
        if image_file:
            upload_result = uploader.upload(image_file, public_id=student_id)
            image_url = upload_result['secure_url']

        query_id_check = "SELECT * FROM students WHERE student_id = %s"
        existing_id = fetch_query(query_id_check, (student_id,))

        query_course_check = "SELECT * FROM courses WHERE course_code = %s AND college_code = %s"
        existing_course = fetch_query(query_course_check, (course_code, college_code))

    
        if existing_id:
            return jsonify({'status': 'duplicate'}), 400
        elif not existing_course:
            flash('Cannot add student. The selected course does not exist for this college.', 'danger')
        else:
            query = """
                INSERT INTO students (student_id, student_name, gender, year_lvl, course_code, college_code, image_url) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            execute_query(query, (student_id, student_name, gender, year_lvl, course_code, college_code, image_url))
            flash('Student added successfully', 'success')
            return redirect(url_for('students.students'))

        return redirect(url_for('students.students'))
    
    college_query = "SELECT college_code, college_name FROM colleges"
    colleges = fetch_query(college_query)
    
    return render_template('add_student.html', colleges=colleges)




#--------------------- AJAX Check Student Existence ----------------------
@students_bp.route('/check_student_existence', methods=['POST'])
def check_student_existence():
    student_id = request.form.get('student_id').upper()
    course_code = request.form.get('course_code').upper()
    college_code = request.form.get('college_code').upper()

    # Check if student ID or course exists
    query_id_check = "SELECT * FROM students WHERE student_id = %s"
    existing_id = fetch_query(query_id_check, (student_id,))

    query_course_check = "SELECT * FROM courses WHERE course_code = %s AND college_code = %s"
    existing_course = fetch_query(query_course_check, (course_code, college_code))

    response = {
        'exists': False,
        'id_exists': bool(existing_id),
        'course_exists': bool(existing_course)
    }

    if existing_id:
        response['exists'] = True

    return jsonify(response)


#--------------------- Edit Student ----------------------

@students_bp.route('/edit_student/<student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if request.method == 'POST':
        student_name = request.form['student_name'].upper()
        gender = request.form['gender'].upper()
        year_lvl = request.form['year_lvl'].upper()
        course_code = request.form['course_code'].upper()
        college_code = request.form['college_code'].upper()

        image_file = request.files.get('image')
        current_image_url = request.form.get('current_image_url', DEFAULT_PROFILE_IMAGE)

        if request.form.get('delete_image') == "true": 
            image_url = DEFAULT_PROFILE_IMAGE  
        elif image_file:
            upload_result = uploader.upload(image_file , overwrite=True, public_id=student_id)
            image_url = upload_result['secure_url']
        else:
            image_url = current_image_url  

        try:
            update_student_query = """
            UPDATE students 
            SET student_name = %s, gender = %s, year_lvl = %s, course_code = %s, college_code = %s, image_url = %s
            WHERE student_id = %s
            """
            execute_query(update_student_query, (student_name, gender, year_lvl, course_code, college_code, image_url, student_id))
            flash('Student updated successfully', 'success')
            return redirect(url_for('students.students'))

        except Exception as e:
            print(f"Error updating student: {e}")
            flash('An error occurred while updating the student. Please try again.', 'danger')
            return redirect(url_for('students.edit_student', student_id=student_id))

    student_query = """
    SELECT students.*, COALESCE(students.image_url, %s) AS image_url
    FROM students
    WHERE students.student_id = %s
    """
    student = fetch_query(student_query, (DEFAULT_PROFILE_IMAGE, student_id))
    
    if not student:
        abort(404)

    college_query = "SELECT college_code, college_name FROM colleges"
    colleges = fetch_query(college_query)

    return render_template('edit_student.html', student=student[0], colleges=colleges)


#--------------------- Fetch Courses by College ----------------------
@students_bp.route('/get_courses/<college_code>', methods=['GET'])
def get_courses(college_code):
    course_query = "SELECT course_code, course_name FROM courses WHERE college_code = %s"
    courses = fetch_query(course_query, (college_code,))
    return jsonify(courses)


#--------------------- Remove Student ----------------------
@students_bp.route('/remove_student/<string:student_id>', methods=['POST'])
def remove_student(student_id):
    delete_query = "DELETE FROM students WHERE student_id = %s"
    execute_query(delete_query, (student_id,))
    uploader.destroy (student_id)
    flash('Student removed successfully', 'success')
    return redirect(url_for('students.students'))

    
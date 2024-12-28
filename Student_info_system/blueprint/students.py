from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from views import (
                    get_total_students,
                    get_students,
                    check_student_existence,
                    add_student_to_db,
                    update_student_in_db,
                    remove_student_from_db,
                    get_colleges,
                    get_courses_by_college
                )
from cloudinary import uploader
import os
import math
from models import fetch_query

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
students_bp = Blueprint(
    'students',
    __name__,
    template_folder='templates',
    static_folder='Student_info_system/static',  
    static_url_path='/static'
)

DEFAULT_PROFILE_IMAGE = 'static/default_pic.jpg'

#--------------------- Student Page ----------------------

@students_bp.route('/students', methods=['GET'])
def students():
    search_keyword = request.args.get('search', '')
    search_by = request.args.get('search_by', 'student_id')
    page = int(request.args.get('page', 1))  
    per_page = 50  

    valid_search_fields = ['student_id', 'student_name', 'gender', 'year_lvl', 'course_code', 'college_code']
    if search_by not in valid_search_fields:
        search_by = 'student_id'

    total_students = get_total_students(search_keyword, search_by)
    total_pages = math.ceil(total_students / per_page)

    students = get_students(search_keyword, search_by, page, per_page)

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

        existing_id, existing_course = check_student_existence(student_id, course_code, college_code)

        if existing_id:
            return jsonify({'status': 'duplicate'}), 400
        elif not existing_course:
            flash('Cannot add student. The selected course does not exist for this college.', 'danger')
        else:
            add_student_to_db(student_id, student_name, gender, year_lvl, course_code, college_code, image_url)
            flash('Student added successfully', 'success')
            return redirect(url_for('students.students'))

        return redirect(url_for('students.students'))
    
    colleges = get_colleges()
    return render_template('add_student.html', colleges=colleges)



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
            update_student_in_db(student_id, student_name, gender, year_lvl, course_code, college_code, image_url)
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

    colleges = get_colleges()

    return render_template('edit_student.html', student=student[0], colleges=colleges)



#--------------------- Fetch Courses by College ----------------------

@students_bp.route('/get_courses/<college_code>', methods=['GET'])
def get_courses(college_code):
    courses = get_courses_by_college(college_code)
    return jsonify(courses)



#--------------------- Remove Student ----------------------

@students_bp.route('/remove_student/<string:student_id>', methods=['POST'])
def remove_student(student_id):
    remove_student_from_db(student_id)
    flash('Student removed successfully', 'success')
    return redirect(url_for('students.students'))

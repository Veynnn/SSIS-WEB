from flask import render_template, request, redirect, url_for, flash, abort,jsonify
from __init__ import app
from models import execute_query, fetch_query
from cloudinary_config import upload_result,cloudinary
from cloudinary import uploader
import os



#------------------ pers page---------------------
@app.route('/')
def index():
    return render_template('index.html')




# COLLEGEZ
#---------------------College Page------------------
@app.route('/colleges', methods=['GET'])
def colleges():

    search_keyword = request.args.get('search', '')
    search_by = request.args.get('search_by', 'college_code') 
    
    
    if 'college_button' in request.args:
        return redirect(url_for('colleges'))

    if search_by not in ['college_code', 'college_name']:
        search_by = 'college_code'  
    
    query = f"SELECT * FROM colleges WHERE {search_by} LIKE %s"
      
    colleges = fetch_query(query, ('%' + search_keyword + '%',))

    return render_template('colleges.html', colleges=colleges, search_keyword=search_keyword)


#---------------------Add College------------------
@app.route('/add_college', methods=['GET', 'POST'])
def add_college():
    if request.method == 'POST':
        college_name = request.form['college_name'].upper()
        college_code = request.form['college_code'].upper()
        
        #-----college code or name exist----------
        query_name_check = "SELECT * FROM colleges WHERE college_name = %s"
        existing_name = fetch_query(query_name_check, (college_name,))
        
        query_code_check = "SELECT * FROM colleges WHERE college_code = %s"
        existing_code = fetch_query(query_code_check, (college_code,))
        
        #-----error handling-------------
        if existing_name and existing_code:
            flash('Cannot add college. Both the college name and code already exist.', 'danger')
        elif existing_name:
            flash('Cannot add college. The college name already exists.', 'danger')
        elif existing_code:
            flash('Cannot add college. The college code already exists.', 'danger')
        else:
            query = "INSERT INTO colleges (college_name, college_code) VALUES (%s, %s)"
            execute_query(query, (college_name, college_code))
            flash('College added successfully', 'success')
            return redirect(url_for('colleges'))
        
        return redirect(url_for('add_college'))
    
    return render_template('add_college.html')


    #-------------ajax thingz-------------
@app.route('/check_college_existence', methods=['POST'])
def check_college_existence():
    
    college_name = request.form.get('college_name').upper()
    college_code = request.form.get('college_code').upper()
    
    query_name_check = "SELECT * FROM colleges WHERE college_name = %s"
    query_code_check = "SELECT * FROM colleges WHERE college_code = %s"

    existing_name = fetch_query(query_name_check, (college_name,))
    existing_code = fetch_query(query_code_check, (college_code,))

    response = {
        'exists': False,
        'name_exists': bool(existing_name),
        'code_exists': bool(existing_code)
    }

    if existing_name or existing_code:
        response['exists'] = True
    
    return jsonify(response)

#---------------------Edit College------------------
@app.route('/edit_college/<college_code>', methods=['GET', 'POST'])
def edit_college(college_code):
    if request.method == 'POST':

        college_name = request.form['college_name'].upper()
        new_college_code = request.form['college_code'].upper()


        #-------------update queriez-------------
        try:
            update_college_query = """
            UPDATE colleges 
            SET college_name = %s, college_code = %s
            WHERE college_code = %s
            """
            execute_query(update_college_query, (college_name, new_college_code, college_code))

            update_courses_query = """
            UPDATE courses 
            SET college_code = %s
            WHERE college_code = %s
            """
            execute_query(update_courses_query, (new_college_code, college_code))

            update_students_query = """
            UPDATE students 
            SET college_code = %s
            WHERE college_code = %s
            """
            execute_query(update_students_query, (new_college_code, college_code))


            #-------------for response and handlingz-------------
            return jsonify({
                'status': 'success',
                'message': 'College updated successfully.'
            }), 200

        except Exception as e:
            print(f"Error updating college: {e}")

            return jsonify({
                'status': 'error',
                'message': 'An error occurred while updating the college. Please try again.'
            }), 500


    college_query = "SELECT college_code, college_name FROM colleges WHERE college_code = %s"                #----note: dis fetch college-----
    college = fetch_query(college_query, (college_code,))

    if not college:
        abort(404)  

    return render_template('edit_college.html', college=college[0])

#---------------------Remove College------------------
@app.route('/remove_college/<string:college_code>', methods=['POST'])
def remove_college(college_code):
    try:
        delete_college_query = "DELETE FROM colleges WHERE college_code = %s"
        execute_query(delete_college_query, (college_code,))
        
        flash('College removed successfully. Courses now have no associated college.', 'success')
    except Exception as e:
        print(f"Error deleting college: {e}")
        flash('Error occurred while deleting the college.', 'danger')
    
    return redirect(url_for('colleges'))





# COURSEZ
#---------------------Course Page------------------
@app.route('/courses', methods=['GET'])
def courses():
    search_keyword = request.args.get('search', '')
    search_by = request.args.get('search_by', 'college_code')

    if 'course_button' in request.args:
        return redirect(url_for('courses'))

    if search_by not in ['college_code', 'course_code', 'course_name']:
        search_by = 'college_code' 
    
    query = f"SELECT * FROM courses WHERE {search_by} LIKE %s"
    courses = fetch_query(query, ('%' + search_keyword + '%',))

    return render_template('courses.html', courses=courses, search_keyword=search_keyword)


#---------------------Add Course----------------------
@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_name = request.form['course_name'].upper()
        course_code = request.form['course_code'].upper()
        college_code = request.form['college_code'].upper()

        try:
            query_name_check = "SELECT * FROM courses WHERE course_name = %s AND college_code = %s"
            existing_name = fetch_query(query_name_check, (course_name, college_code))

            query_code_check_global = "SELECT * FROM courses WHERE course_code = %s"
            existing_code = fetch_query(query_code_check_global, (course_code,))

            if existing_name and existing_code:
                return jsonify({'success': False, 'message': 'Both the course name and code already exist. Please choose different values.'})
            elif existing_name:
                return jsonify({'success': False, 'message': 'The course name already exists for this college. Please choose a different name.'})
            elif existing_code:
                return jsonify({'success': False, 'message': 'The course code already exists across all colleges. Please choose a different code.'})  # Global check message
            else:
                query = "INSERT INTO courses (course_name, course_code, college_code) VALUES (%s, %s, %s)"
                execute_query(query, (course_name, course_code, college_code))
                return jsonify({'success': True, 'message': 'Course added successfully.'})

        except Exception as e:
            return jsonify({'success': False, 'message': 'Error occurred: ' + str(e)})  

    college_query = "SELECT college_code, college_name FROM colleges"
    colleges = fetch_query(college_query)
    return render_template('add_course.html', colleges=colleges)

@app.route('/check_course_existence', methods=['POST'])
def check_course_existence():
    course_name = request.form.get('course_name').upper()
    course_code = request.form.get('course_code').upper()
    college_code = request.form.get('college_code').upper()

    try:
        query_name_check = "SELECT * FROM courses WHERE course_name = %s AND college_code = %s"
        query_code_check_global = "SELECT * FROM courses WHERE course_code = %s"  

        existing_name = fetch_query(query_name_check, (course_name, college_code))
        existing_code = fetch_query(query_code_check_global, (course_code,))

        response = {
            'exists': bool(existing_name or existing_code),
            'name_exists': bool(existing_name),
            'code_exists': bool(existing_code)  
        }

        return jsonify(response)
    except Exception as e:
        print(f"Error checking course existence: {e}")
        return jsonify({'exists': False, 'name_exists': False, 'code_exists': False, 'message': 'Error occurred while checking course existence.'})  # Ensure a clear error message


#---------------------Edit Course----------------------
@app.route('/edit_course/<course_code>', methods=['GET', 'POST'])
def edit_course(course_code):
    if request.method == 'POST':
        course_name = request.form['course_name'].upper()
        new_course_code = request.form['course_code'].upper()
        college_code = request.form['college_code'].upper()

        try:
            update_course_query = """
            UPDATE courses 
            SET course_name = %s, course_code = %s, college_code = %s
            WHERE course_code = %s
            """
            execute_query(update_course_query, (course_name, new_course_code, college_code, course_code))

            update_students_query = """
            UPDATE students 
            SET college_code = %s
            WHERE course_code = %s
            """
            execute_query(update_students_query, (college_code, new_course_code))

            return jsonify({
                'status': 'success',
                'message': 'Course updated successfully.'
            }), 200

        except Exception as e:
            print(f"Error updating course: {e}")

            return jsonify({
                'status': 'error',
                'message': 'An error occurred while updating the course. Please try again.'
            }), 500

    course_query = "SELECT course_code, course_name, college_code FROM courses WHERE course_code = %s"
    result = fetch_query(course_query, (course_code,))
    
    if not result:
        abort(404) 

    course = result[0]  

    college_query = "SELECT college_code, college_name FROM colleges"
    colleges = fetch_query(college_query)

    return render_template('edit_course.html', course=course, colleges=colleges)


#---------------------Remove Course----------------------
@app.route('/remove_course/<string:course_code>', methods=['POST'])
def remove_course(course_code):

    update_query = "UPDATE students SET course_code = NULL WHERE course_code = %s"
    execute_query(update_query, (course_code,))
    
    delete_query = "DELETE FROM courses WHERE course_code = %s"
    execute_query(delete_query, (course_code,))
    
    flash('Course removed successfully', 'success')
    return redirect(url_for('courses'))





# Placeholder image URL if no image is uploaded
DEFAULT_PROFILE_IMAGE = os.path.join('static', 'EYYY.jpg')

#--------------------- Student Page ----------------------
@app.route('/students', methods=['GET'])
def students():
    search_keyword = request.args.get('search', '')
    search_by = request.args.get('search_by', 'student_id')

    # Redirect if the 'student_button' is pressed
    if 'student_button' in request.args:
        return redirect(url_for('students'))

    valid_search_fields = ['student_id', 'student_name', 'gender', 'year_lvl', 'course_code', 'college_code']
    if search_by not in valid_search_fields:
        search_by = 'student_id'

    query = f"""
    SELECT 
        students.student_id, 
        students.student_name, 
        students.gender, 
        students.year_lvl, 
        COALESCE(students.image_url, %s) AS image_url,  -- Default if image URL is NULL
        courses.course_code, 
        colleges.college_code, 
        courses.course_name, 
        colleges.college_name
    FROM students
    LEFT JOIN courses ON students.course_code = courses.course_code
    LEFT JOIN colleges ON students.college_code = colleges.college_code
    WHERE students.{search_by} LIKE %s
    """
    students = fetch_query(query, (DEFAULT_PROFILE_IMAGE, '%' + search_keyword + '%'))

    return render_template('students.html', students=students, search_keyword=search_keyword, default_profile_image=DEFAULT_PROFILE_IMAGE)


#--------------------- Add Student ----------------------
@app.route('/add_student', methods=['GET', 'POST'])
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
            upload_result = uploader.upload(image_file)
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
            return redirect(url_for('students'))

        return redirect(url_for('add_student'))
    
    college_query = "SELECT college_code, college_name FROM colleges"
    colleges = fetch_query(college_query)
    
    return render_template('add_student.html', colleges=colleges)


#--------------------- AJAX Check Student Existence ----------------------
@app.route('/check_student_existence', methods=['POST'])
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

@app.route('/edit_student/<student_id>', methods=['GET', 'POST'])
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
            upload_result = uploader.upload(image_file)
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
            return redirect(url_for('students'))

        except Exception as e:
            print(f"Error updating student: {e}")
            flash('An error occurred while updating the student. Please try again.', 'danger')
            return redirect(url_for('edit_student', student_id=student_id))

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
@app.route('/get_courses/<college_code>', methods=['GET'])
def get_courses(college_code):
    course_query = "SELECT course_code, course_name FROM courses WHERE college_code = %s"
    courses = fetch_query(course_query, (college_code,))
    return jsonify(courses)


#--------------------- Remove Student ----------------------
@app.route('/remove_student/<string:student_id>', methods=['POST'])
def remove_student(student_id):
    delete_query = "DELETE FROM students WHERE student_id = %s"
    execute_query(delete_query, (student_id,))
    
    flash('Student removed successfully', 'success')
    return redirect(url_for('students'))

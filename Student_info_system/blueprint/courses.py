from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from models import execute_query, fetch_query


courses_bp = Blueprint('courses', import_name=__name__, template_folder='templates')



# COURSEZ
#---------------------Course Page------------------
@courses_bp.route('/courses', methods=['GET'])
def courses():
    search_keyword = request.args.get('search', '')
    search_by = request.args.get('search_by', 'college_code')

    if 'course_button' in request.args:
        return redirect(url_for('courses.courses'))

    if search_by not in ['college_code', 'course_code', 'course_name']:
        search_by = 'college_code' 
    
    query = f"SELECT * FROM courses WHERE {search_by} LIKE %s"
    courses = fetch_query(query, ('%' + search_keyword + '%',))

    return render_template('courses.html', courses=courses, search_keyword=search_keyword)


#---------------------Add Course----------------------
@courses_bp.route('/add_course', methods=['GET', 'POST'])
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

@courses_bp.route('/check_course_existence', methods=['POST'])
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
@courses_bp.route('/edit_course/<course_code>', methods=['GET', 'POST'])
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
@courses_bp.route('/remove_course/<string:course_code>', methods=['POST'])
def remove_course(course_code):

    update_query = "UPDATE students SET course_code = NULL WHERE course_code = %s"
    execute_query(update_query, (course_code,))
    
    delete_query = "DELETE FROM courses WHERE course_code = %s"
    execute_query(delete_query, (course_code,))
    
    flash('Course removed successfully', 'success')
    return redirect(url_for('courses.courses'))



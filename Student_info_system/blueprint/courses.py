from flask import Blueprint, render_template, request, redirect, url_for, flash, abort,jsonify
from views import (
    get_courses,
    check_existing_course,
    check_existing_code,
    insert_new_course,
    get_colleges,
    get_course,
    update_course,
    update_students_course,
    delete_course
)

courses_bp = Blueprint('courses', import_name=__name__, template_folder='templates')

#---------------------Course Page------------------
@courses_bp.route('/courses', methods=['GET'])
def courses():

    search_keyword = request.args.get('search', '')
    search_by = request.args.get('search_by', 'college_code')

    if 'course_button' in request.args:
        return redirect(url_for('courses.courses'))

    if search_by not in ['college_code', 'course_code', 'course_name']:
        search_by = 'college_code'

    courses = get_courses(search_by, search_keyword)

    return render_template('courses.html', courses=courses, search_keyword=search_keyword)


#---------------------Add Course----------------------
@courses_bp.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_name = request.form['course_name'].upper()
        course_code = request.form['course_code'].upper()
        college_code = request.form['college_code'].upper()

        try:
            existing_name = check_existing_course(course_name, college_code)
            existing_code = check_existing_code(course_code)

            if existing_name and existing_code:
                flash('Both the course name and code already exist. Please choose different values.', 'danger')
                return redirect(url_for('courses.add_course'))
            elif existing_name:
                flash('The course name already exists for this college. Please choose a different name.', 'danger')
                return redirect(url_for('courses.add_course'))
            elif existing_code:
                flash('The course code already exists across all colleges. Please choose a different code.', 'danger')
                return redirect(url_for('courses.add_course'))
            else:
                insert_new_course(course_name, course_code, college_code)
                flash('Course added successfully.', 'success')
                return redirect(url_for('courses.courses'))

        except Exception as e:
            flash(f"Course added successfully.", 'danger')
            return redirect(url_for('courses.courses'))

    colleges = get_colleges()
    return render_template('add_course.html', colleges=colleges)


@courses_bp.route('/check_course_existence', methods=['POST'])
def check_course_existence():
    course_name = request.form.get('course_name').upper()
    course_code = request.form.get('course_code').upper()
    college_code = request.form.get('college_code').upper()

    try:
        existing_name = check_existing_course(course_name, college_code)
        existing_code = check_existing_code(course_code)

        response = {
            'exists': bool(existing_name or existing_code),
            'name_exists': bool(existing_name),
            'code_exists': bool(existing_code)
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'exists': False, 'name_exists': False, 'code_exists': False, 'message': 'Error occurred while checking course existence.'})


#---------------------Edit Course----------------------
@courses_bp.route('/edit_course/<course_code>', methods=['GET', 'POST'])
def edit_course(course_code):
    if request.method == 'POST':
        course_name = request.form['course_name'].upper()
        new_course_code = request.form['course_code'].upper()
        college_code = request.form['college_code'].upper()

        try:
            update_course(course_name, new_course_code, college_code, course_code)
            update_students_course(course_code, college_code)

            flash('Course updated successfully.', 'success')
            return redirect(url_for('courses.courses'))  
        except Exception as e:
            flash('Course updated successfully.', 'danger')
            return redirect(url_for('courses.courses', course_code=course_code))  

    course = get_course(course_code)
    
    if not course:
        abort(404)

    colleges = get_colleges()  
    return render_template('edit_course.html', course=course[0], colleges=colleges)


#---------------------Remove Course----------------------
@courses_bp.route('/remove_course/<string:course_code>', methods=['POST'])
def remove_course(course_code):
    try:
        delete_course(course_code)
        flash('Course removed successfully', 'success')
    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')

    return redirect(url_for('courses.courses'))

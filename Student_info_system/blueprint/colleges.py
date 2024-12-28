from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from views import (get_colleges_search, 
                   check_college_name_existence, 
                   check_college_code_existence, 
                   add_colleges, get_college_by_code, 
                   update_college, 
                   remove_colleges
            )
from models import fetch_query,execute_query
import MySQLdb 


colleges_bp = Blueprint('colleges', import_name=__name__, template_folder='templates')


#---------------------College Page------------------
@colleges_bp.route('/colleges', methods=['GET'])
def colleges():

    search_keyword = request.args.get('search', '')
    search_by = request.args.get('search_by', 'college_code') 
    
    if 'college_button' in request.args:
        return redirect(url_for('colleges.colleges'))

    if search_by not in ['college_code', 'college_name']:
        search_by = 'college_code'  
    
    colleges = get_colleges_search (search_keyword, search_by)

    return render_template('colleges.html', colleges=colleges, search_keyword=search_keyword)

#---------------------Add College------------------
@colleges_bp.route('/add_college', methods=['GET', 'POST'])
def add_college():
    if request.method == 'POST':
        college_name = request.form['college_name'].upper()
        college_code = request.form['college_code'].upper()
        
        existing_name = check_college_name_existence(college_name)
        existing_code = check_college_code_existence(college_code)
        
        if existing_name and existing_code:
            flash('Cannot add college. Both the college name and code already exist.', 'danger')
        elif existing_name:
            flash('Cannot add college. The college name already exists.', 'danger')
        elif existing_code:
            flash('Cannot add college. The college code already exists.', 'danger')
        else:
            try:
                add_colleges(college_name, college_code=college_code)
                flash('College added successfully', 'success')
                return redirect(url_for('colleges.colleges'))
            except Exception as e:
                flash(f'Error adding college: {str(e)}', 'danger')
        
        return redirect(url_for('colleges.add_college'))
    
    return render_template('add_college.html')



#-------------AJAX College Existence Check-------------
@colleges_bp.route('/check_college_existence', methods=['POST'])
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
@colleges_bp.route('/edit_college/<college_code>', methods=['GET', 'POST'])
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
@colleges_bp.route('/remove_college/<string:college_code>', methods=['POST'])
def remove_college(college_code):
    try:
        remove_colleges(college_code)
        flash('College removed successfully. Associated courses and course references for students have been cleared.', 'success')
    except Exception as e:
        print(f"Error deleting college: {e}")
        flash('Error occurred while deleting the college.', 'danger')

    return redirect(url_for(endpoint='colleges.colleges'))

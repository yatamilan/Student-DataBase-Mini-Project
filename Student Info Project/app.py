from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector

# Create a new Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # This is needed to show flash messages on the website

# This is the setup for connecting to the database
db_config = {
    'host': 'host',  # The address where the database is located
    'user': 'user',       # The username to log in to the database
    'password': 'password', # The password to log in to the database
    'database': 'database'  # The name of the database we are using
}

# This function connects to the database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)  # Connect to the database
    return conn  # Return the connection to use it later

# This function finds the next student ID to use
def get_next_id():
    conn = get_db_connection()  # Get the database connection
    cursor = conn.cursor()  # Create a cursor to run commands on the database
    cursor.execute('SELECT id FROM students ORDER BY id')  # Get all student IDs
    ids = [row[0] for row in cursor.fetchall()]  # Make a list of all IDs
    next_id = 1  # Start with ID 1
    for id in ids:  # Check each ID
        if id != next_id:  # If the ID is not the next one we need
            break  # Stop the loop
        next_id += 1  # Go to the next ID
    conn.close()  # Close the connection to the database
    return next_id  # Return the next ID to use

# This route shows the main page
@app.route('/')
def home():
    return render_template('sample.html')  # Show the 'sample.html' page

# This route adds a new student to the database
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']  # Get the student's name from the form
    age = request.form['age']  # Get the student's age from the form
    grade = request.form['grade']  # Get the student's grade from the form
    student_id = get_next_id()  # Find the next ID to use
    conn = get_db_connection()  # Connect to the database
    cursor = conn.cursor()  # Create a cursor to run commands
    try:
        # Add the new student to the database
        cursor.execute('INSERT INTO students (id, name, age, grade) VALUES (%s, %s, %s, %s)', (student_id, name, age, grade))
        conn.commit()  # Save the changes to the database
        flash('Student added successfully!', 'success')  # Show a success message
    except Exception as e:
        flash(f'Error adding student: {e}', 'error')  # Show an error message if something goes wrong
    finally:
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection to the database
    return redirect(url_for('home'))  # Go back to the main page

# This route updates a student's information
@app.route('/update_student', methods=['POST'])
def update_student():
    student_id = request.form['updateId']  # Get the student's ID from the form
    name = request.form.get('updateName')  # Get the new name (if any) from the form
    age = request.form.get('updateAge')  # Get the new age (if any) from the form
    grade = request.form.get('updateGrade')  # Get the new grade (if any) from the form
    conn = get_db_connection()  # Connect to the database
    cursor = conn.cursor()  # Create a cursor to run commands
    try:
        # Prepare the update command
        update_query = 'UPDATE students SET '
        updates = []
        if name:
            updates.append('name = %s')  # Add name to the update list if provided
        if age:
            updates.append('age = %s')  # Add age to the update list if provided
        if grade:
            updates.append('grade = %s')  # Add grade to the update list if provided
        update_query += ', '.join(updates)  # Join all updates together
        update_query += ' WHERE id = %s'  # Specify which student to update
        values = [val for val in [name, age, grade] if val is not None]  # Collect all values that are not None
        values.append(student_id)  # Add the student ID to the end of the values list
        cursor.execute(update_query, values)  # Run the update command
        conn.commit()  # Save the changes to the database
        flash('Student updated successfully!', 'success')  # Show a success message
    except Exception as e:
        flash(f'Error updating student: {e}', 'error')  # Show an error message if something goes wrong
    finally:
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection to the database
    return redirect(url_for('home'))  # Go back to the main page

# This route deletes a student from the database
@app.route('/delete_student', methods=['POST'])
def delete_student():
    student_id = request.form['deleteId']  # Get the student's ID from the form
    conn = get_db_connection()  # Connect to the database
    cursor = conn.cursor()  # Create a cursor to run commands
    try:
        cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))  # Delete the student with the given ID
        conn.commit()  # Save the changes to the database
        flash('Student deleted successfully!', 'success')  # Show a success message
    except Exception as e:
        flash(f'Error deleting student: {e}', 'error')  # Show an error message if something goes wrong
    finally:
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection to the database
    return redirect(url_for('home'))  # Go back to the main page

# This route shows all students
@app.route('/view_all_students')
def view_all_students():
    conn = get_db_connection()  # Connect to the database
    cursor = conn.cursor(dictionary=True)  # Create a cursor to run commands and get results as dictionaries
    cursor.execute('SELECT * FROM students')  # Get all students from the database
    students = cursor.fetchall()  # Fetch all the students
    cursor.close()  # Close the cursor
    conn.close()  # Close the connection to the database
    return render_template('view_all_students.html', students=students)  # Show the 'view_all_students.html' page with the student data

# Run the app in debug mode (show errors in the browser)
if __name__ == '__main__':
    app.run(debug=True)

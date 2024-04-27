import time
from datetime import datetime, timedelta
import re
import bcrypt
from _sqlite3 import Error
from flask import Flask, render_template, request, flash, url_for, session, redirect, logging, jsonify
import random
import string
import database

app = Flask(__name__)
db_file = "CAPSTONE-PROJECT.db"
app.secret_key = 'super secret key'  # secret key for captcha
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

# Define session timeout duration in seconds
SESSION_TIMEOUT = 60

# Set the session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)


@app.before_request
def before_request():
    # Check if user is logged in and session is active
    if 'user_id' in session:
        # Check if the last activity time is stored in session
        last_activity_time = session.get('last_activity_time')
        if last_activity_time is not None:
            # Calculate time elapsed since last activity
            time_elapsed = time.time() - last_activity_time
            # If time elapsed exceeds session timeout, log the user out
            if time_elapsed > SESSION_TIMEOUT:
                # Clear session and log out user
                session.clear()
                flash("Session timed out due to inactivity.")
                return redirect(url_for('login'))
        # Update last activity time in session
        session['last_activity_time'] = time.time()


@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out due to inactivity.')
    return redirect(url_for('login'))


@app.route('/new_folder')
def new_folder():
    return render_template('new_folder.html')


@app.route('/add_folder', methods=['POST'])
def add_folder():
    folder_name = request.form.get("folder_name")

    messages = []  # List to store messages
    message_type = "error"  # Default message type

    try:
        # Establish database connection
        conn = database.connect(db_file)
        cursor = conn.cursor()

        # Check if folder name is provided
        if not folder_name:
            messages.append("Please provide a folder name.")
        else:
            # Retrieve user ID from session
            user_id = session.get('user_id')
            if user_id:
                # Add folder to the database with the associated user_id
                cursor.execute("INSERT INTO FOLDER (USER_ID, FOLDER_NAME) VALUES (?, ?)", (user_id, folder_name))
                conn.commit()
                messages.append("Folder added successfully.")
                message_type = "success"
            else:
                messages.append("User ID not found.")

    except Exception as e:
        messages.append("Failed to add folder. Try again!")
        print("Error:", e)

    finally:
        # Close the database connection
        if conn:
            conn.close()

    # Redirect back to the vault page after adding the folder
    return redirect(url_for('vault'))


def generate_password(
    length, min_length, min_numbers, min_special_chars, special_chars, avoid_ambiguous
):
    password = ""
    numbers = string.digits
    special_characters = "".join(special_chars)
    ambiguous_characters = "0Oo1Il|"
    if avoid_ambiguous:
        characters = "".join(
            [
                c
                for c in string.ascii_letters + numbers + special_characters
                if c not in ambiguous_characters
            ]
        )
    else:
        characters = string.ascii_letters + numbers + special_characters

    # Add minimum numbers
    for _ in range(min_numbers):
        password += random.choice(numbers)

    # Add minimum special characters
    for _ in range(min_special_chars):
        password += random.choice(special_characters)

    # Generate the rest of the password
    remaining_length = length - min_length
    for _ in range(remaining_length):
        password += random.choice(characters)

    password = "".join(random.sample(password, len(password)))
    return password


@app.route('/generate_password', methods=['POST'])
def handle_generate_password():
    length = int(request.form['total_length'])
    min_length = int(request.form['min_length'])
    min_numbers = int(request.form['min_numbers'])
    min_special_chars = int(request.form['min_special_chars'])
    special_chars = request.form.getlist('special_chars')
    avoid_ambiguous = 'avoid_ambiguous' in request.form

    password = generate_password(length, min_length, min_numbers, min_special_chars, special_chars, avoid_ambiguous)
    return password  # Return the generated password as plain text

@app.route('/vault')
def vault():
    if 'user_id' in session:
        user_id = session.get('user_id')
        try:
            # Establish database connection
            conn = database.connect(db_file)
            cursor = conn.cursor()

            # Retrieve folders for the current user
            cursor.execute("SELECT FOLDER_NAME FROM FOLDER WHERE USER_ID = ? AND USER_ID = ? ", (user_id, user_id))
            folders = cursor.fetchall()

        except Exception as e:
            print("Error:", e)
            folders = []

        finally:
            # Close the database connection
            if conn:
                conn.close()

        # Render the template with the list of folders
        return render_template('vault.html', folders=folders)

    flash("You are not logged in.")
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        options = request.form.get('options')
        password_type = request.form.get('password_type')
        total_length = int(request.form.get('total_length'))
        min_length = int(request.form.get('min_length'))
        min_numbers = int(request.form.get('min_numbers'))
        min_special_chars = int(request.form.get('min_special_chars'))
        special_chars = request.form.getlist('special_chars')
        avoid_ambiguous = 'avoid_ambiguous' in request.form

        if options == 'Password':
            password = generate_password(total_length, min_length, min_numbers, min_special_chars, special_chars,
                                         avoid_ambiguous)
            return render_template('index.html', password=password)
        elif options == 'Encrypted':
            # Implement logic for encrypted password generation here
            encrypted_password = "EncryptedPassword"  # Replace this with your encrypted password generation logic
            return render_template('index.html', password=encrypted_password)

    return render_template('index.html', password='')

@app.route('/gen_Password')
def gen_Password():
    return render_template('gen_Password.html')

@app.route('/login')
def login():
    return render_template('index.html')


@app.route('/loginAction', methods=['POST'])
def loginAction():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Connect to the database
        conn = database.connect(db_file)
        if conn is None:
            flash("Failed to connect to the database.")
            return redirect(url_for('login'))

        cursor = conn.cursor()

        # Check if user exists in the database
        cursor.execute("SELECT * FROM REGISTRATION WHERE EMAIL = ?", (email,))
        user = cursor.fetchone()

        if user:
            # Debug: Print user data retrieved from the database
            print("User Data:", user)

            # Check if passwords match
            if bcrypt.checkpw(password.encode('utf-8'), user[4]):  # Compare hashed password
                # Passwords match, set session variables or redirect to dashboard
                session['user_id'] = user[0]  # Assuming user_id is in the first column
                flash("Login successful.")
                return redirect(url_for('profile'))
            else:
                error_message = "Invalid email or password. Please try again."
        else:
            error_message = "Invalid email or password. Please try again."

        # Debug: Print error message
        print("Error Message:", error_message)

        # Render login page with error message
        return render_template('index.html', error_message=error_message)

    return render_template('index.html')


@app.route('/profile')
def profileaction():
    # Check if user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        # Connect to the database
        conn = database.connect(db_file)
        if conn is None:
            flash("Failed to connect to the database.")
            return redirect(url_for('login'))

        cursor = conn.cursor()

        # Fetch user info from the database
        cursor.execute("SELECT * FROM REGISTRATION WHERE ID = ?", (user_id,))
        user_info = cursor.fetchone()

        # Close cursor and connection
        cursor.close()
        conn.close()

        return render_template('profile.html', user_info=user_info)
    else:
        flash("You are not logged in.")
        return redirect(url_for('login'))


@app.route('/registration')
def registration():
    return render_template('registration.html')


@app.route('/registrationAction', methods=['POST'])
def registrationAction():
    email = request.form.get("email_address")
    name = request.form.get("name")
    password = request.form.get("master_password")
    password_hint = request.form.get("hint")
    retype_password = request.form.get("retype_password")  # Fix: Correct field name

    messages = []  # List to store messages
    message_type = "error"  # Default message type

    try:
        # Establish database connection
        conn = database.connect(db_file)
        if conn is None:
            raise Error("Failed to connect to the database.")

        cursor = conn.cursor()

        # Check if username already exists in the database
        cursor.execute("SELECT email FROM REGISTRATION WHERE LOWER(email) = LOWER(?)", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            messages.append("Email already taken. Please choose a different email.")
            return render_template('registration.html', messages=messages, message_type=message_type)  # Return early

        # Check if password and password hint match
        if password == password_hint:
            messages.append("Password hint should not be the same as the password.")
            return render_template('registration.html', messages=messages, message_type=message_type)  # Return early

        # Check password complexity
        if len(password) < 8:
            messages.append("Password must be at least 8 characters long.")
        elif not any(char.isupper() for char in password):
            messages.append("Password must contain at least one capital letter.")
        elif not any(char in "!@#$%^&*?" for char in password):
            messages.append("Password must contain at least one symbol.")
        else:
            messages.append("Password meets complexity requirements.")
            # Continue with registration process

        # Check if passwords match
        if password != retype_password:  # Fix: Correct field name
            messages.append("Passwords do not match.")
            return render_template('registration.html', messages=messages, message_type=message_type)  # Return early

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Execute SQL query
        cursor.execute("INSERT INTO REGISTRATION (EMAIL, NAME, MASTER_PASSWORD, PASSWORD_HINT) VALUES (?, ?, ?, ?)",
                       (email, name, hashed_password, password_hint))
        conn.commit()
        conn.commit()
        messages.append("Account created successfully.")
        message_type = "success"
        return redirect(url_for('profile'))

    except Error as e:
        messages.append("Failed to signup. Try again!")
        print("Database Error:", e)

    except Exception as e:
        messages.append("Failed to create your account. Try again!")
        print("Error:", e)

    finally:
        if conn:
            conn.close()

    # Render the template with the messages and message type
    return render_template('registration.html', messages=messages, message_type=message_type)


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/new_item')
def new_item():
    return render_template('new_item.html')


@app.route('/new_itemAction', methods=['GET', 'POST'])
def new_itemAction():
    if 'user_id' in session:
        user_id = session.get('user_id')
        if request.method == 'POST':
            try:
                # Handle form submission
                item_type_id = request.form['item_type_id']
                name = request.form['name']
                folder_id = request.form['folder_id']

                conn = database.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO items (item_type_id, name, folder_id, user_id) VALUES (?, ?, ?, ?)",
                               (item_type_id, name, folder_id, user_id))
                conn.commit()

                if conn:
                    conn.close()

                return redirect(url_for('success_page'))

            except Error as e:
                print("Database Error:", e)
                # Handle the error appropriately, e.g., render an error page

        # Retrieve folders belonging to the logged-in user
        conn = database.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT FOLDER_NAME FROM FOLDER WHERE USER_ID = ?", (user_id,))
        folders = cursor.fetchall()
        print("Folders:", folders)

        conn.close()

        return render_template('new_item.html', folders=folders)
    else:
        # Redirect to login page or handle unauthorized access
        return redirect(url_for('login_page'))


# Add this route to handle account deletion// not deleting data related to user just user profile
@app.route('/delete_account', methods=['POST'])
def delete_account():
    # Check if the user is authenticated
    if 'user_id' in session:
        user_id = session['user_id']
        try:
            # Connect to the database
            conn = database.connect(db_file)
            cursor = conn.cursor()

            # Delete user's data from related tables
            cursor.execute("DELETE FROM REGISTRATION WHERE USER_ID = ?", (user_id,))
            # You may need additional delete operations for related tables, such as items, folders, etc.

            conn.commit()
            flash("Your account has been successfully deleted.")
            # Clear the session
            session.clear()
            return redirect(url_for('index'))

        except Exception as e:
            # Handle any errors appropriately
            print("Error deleting account:", e)
            flash("Failed to delete your account. Please try again later.")

        finally:
            if conn:
                conn.close()

    else:
        # Redirect to login page or handle unauthorized access
        flash("You are not logged in.")
        return redirect(url_for('login'))

# Update your settings HTML template to include a form or button to trigger the account deletion



@app.route('/vault/<folder_name>')
def view_folder(folder_name):
    try:
        # Establish database connection
        conn = database.connect(db_file)
        cursor = conn.cursor()

        # Retrieve items from the selected folder
        cursor.execute(
            "SELECT * FROM ITEM WHERE FOLDER_ID = (SELECT ID FROM FOLDER WHERE LOWER(FOLDER_NAME) = LOWER(?))",
            (folder_name,))
        items = cursor.fetchall()

    except database.Error as e:
        print("Database Error:", e)
        items = []

    finally:
        # Close the database connection
        if conn:
            conn.close()

    # Render the template with the items in the folder
    return render_template('folder.html', folder_name=folder_name, items=items)


@app.route('/get_folders1')
def get_folders():
    # Assuming you have a function to retrieve folders from the database
    folders = database.get_folders()  # Implement this function according to your database schema

    # Assuming each folder is represented as a dictionary with 'folder_id' and 'folder_name' keys
    folders_data = [{'folder_id': folder['folder_id'], 'folder_name': folder['folder_name']} for folder in folders]

    # Return the folder data as JSON
    return jsonify(folders_data)

if __name__ == '__main__':
    app.run(debug=True)

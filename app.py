<<<<<<< HEAD
from flask import Flask, render_template, request, make_response, redirect, url_for
=======
from flask import Flask, render_template, request
from flask_mail import Mail, Message
<<<<<<< Updated upstream
=======
>>>>>>> f08ba4792b5b09093931c907e956dea518e68487
>>>>>>> Stashed changes
import random
import string
import pyperclip
import database

app = Flask(__name__)


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


@app.route("/", methods=["GET", "POST"])
@app.route('/generate_password', methods=['POST'])
def handle_generate_password():
    length = int(request.form['total_length'])
    min_length = int(request.form['min_length'])
    min_numbers = int(request.form['min_numbers'])
    min_special_chars = int(request.form['min_special_chars'])
    special_chars = request.form.getlist('special_chars')
    avoid_ambiguous = 'avoid_ambiguous' in request.form

    password = generate_password(length, min_length, min_numbers, min_special_chars, special_chars, avoid_ambiguous)
    return render_template('encryption_helper.html', encrypted_password=password)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        options = request.form.get("options")
        password_type = request.form.get("password_type")
        total_length = int(request.form.get("total_length"))
        min_length = int(request.form.get("min_length"))
        min_numbers = int(request.form.get("min_numbers"))
        min_special_chars = int(request.form.get("min_special_chars"))
        special_chars = request.form.getlist("special_chars")
        avoid_ambiguous = "avoid_ambiguous" in request.form

        if options == "Password":
            password = generate_password(
                total_length,
                min_length,
                min_numbers,
                min_special_chars,
                special_chars,
                avoid_ambiguous,
            )
            return render_template("index.html", password=password)
        elif options == "Username":
            # Implement username generation logic here
            username = (
                "SampleUsername"  # Replace this with your username generation logic
            )
            return render_template("index.html", password=username)
        if options == 'Password':
            password = generate_password(total_length, min_length, min_numbers, min_special_chars, special_chars, avoid_ambiguous)
            return render_template('index.html', password=password)
        elif options == 'Encrypted':
            # Implement logic for encrypted password generation here
            encrypted_password = "EncryptedPassword"  # Replace this with your encrypted password generation logic
            return render_template('index.html', password=encrypted_password)

    return render_template("index.html", password="")
    
@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/loginAction', methods=['GET', 'POST'])
def loginAction():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = database.connect(db_file)
        if conn is None:
            flash("Failed to connect to the database.")
            return redirect(url_for('login'))

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM REGISTRATION WHERE EMAIL = ? AND MASTER_PASSWORD = ?", (email, password))
        user = cursor.fetchone()

        if user:
            session['email'] = email
            flash("Login successful.")
            return redirect(url_for('profile'))
        else:
            flash("Invalid email or password. Please try again.")
        cursor.close()
        conn.close()

    return render_template('index.html')


@app.route('/registration')
def registration():
    return render_template('registration.html')


@app.route('/registrationAction', methods=['POST'])
def registrationAction():
    email = request.form.get("email_address")
    name = request.form.get("name")
    password = request.form.get("master_password")
    password_hint = request.form.get("hint")

    messages = []  # List to store messages
    message_type = "error"  # Default message type

    try:
        # Establish database connection
        conn = database.connect(db_file)
        cursor = conn.cursor()

        # Check if username already exists in the database
        cursor.execute("SELECT email FROM REGISTRATION WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            messages.append("Email already taken. Please choose a different email.")

        # Check if password and password hint match
        if password == password_hint:
            messages.append("Password hint should not be the same as the password.")

        # Check password complexity
        if len(password) < 8 or not re.search("[A-Z]", password) or not re.search("[!@#$%^&*]", password):
            messages.append("Password must be at least 8 characters long, contain at least one capital letter, and at least one symbol.")

        # Check if passwords match
        if request.form.get("master_password") != request.form.get("confirm_password"):
            messages.append("Passwords do not match.")

        if not messages:
            # Execute SQL query
            cursor.execute("INSERT INTO REGISTRATION (EMAIL, NAME, MASTER_PASSWORD, PASSWORD_HINT) VALUES (?, ?, ?, ?)",
                           (email, name, password, password_hint))
            conn.commit()
            messages.append("Account created successfully.")
            message_type = "success"

    except database.Error as e:
        messages.append("Failed to signup. Try again!")
        print("Database Error:", e)

    except Exception as e:
        messages.append("Failed to create your account. Try again!")
        print("Error:", e)

    # Render the template with the messages and message type
    return render_template('registration.html', messages=messages, message_type=message_type)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/profile')
def profileaction():
    # Check if user is logged in
    if 'email' in session:
        email = session['email']
        # Connect to the database
        conn = database.connect(db_file)
        if conn is None:
            flash("Failed to connect to the database.")
            return redirect(url_for('login'))

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM REGISTRATION WHERE EMAIL = ?", (email,))
        user_info = cursor.fetchone()
        cursor.close()
        conn.close()

        return render_template('profile.html', user_info=user_info)
    else:
        flash("You are not logged in.")
        return redirect(url_for('login'))

@app.route('/encryption_helper', methods=['GET', 'POST'])
def encryption_helper():
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
            password = generate_password(total_length, min_length, min_numbers, min_special_chars, special_chars, avoid_ambiguous)
            return render_template('encryption_helper.html', encrypted_password=password)

    return render_template('encryption_helper.html', encrypted_password='')

@app.route('/new_item')
def new_item():
    return render_template('new_item.html')

@app.route('/vault')
def vault():
    return render_template('vault.html')

@app.route('/test')
def test():
    return render_template('test.html')

<<<<<<< Updated upstream
@app.route("/copy", methods=["POST"])
=======
<<<<<<< HEAD

@app.route('/preferences')
def preferences():
    return render_template('MyPreferences.html')



@app.route('/tools')
def tools():
    return render_template('encryption_helper.html')





@app.route('/copy', methods=['POST'])
=======
@app.route("/copy", methods=["POST"])
>>>>>>> f08ba4792b5b09093931c907e956dea518e68487
>>>>>>> Stashed changes
def copy():
    password = request.form.get("password")
    pyperclip.copy(password)
    return "Password copied to clipboard"

    return 'Password copied to clipboard'

def main():
    # Call the function to initialize the database
    database.initialize_database()


if __name__ == "__main__":
    app.run(debug=True)

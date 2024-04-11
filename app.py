from flask import Flask, render_template, request
from flask_mail import Mail, Message
import random
import string
import pyperclip
import database

app = Flask(__name__)

secret_key = secrets.token_hex(16)  # Generates a random hex string of 16 bytes (32 characters)
print("Generated Secret Key:", secret_key)

app.config['SECRET_KEY'] = 'secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''

mail = Mail(app)

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
    return render_template('login.html')

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
            return redirect(url_for('comp'))
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
    master_password = request.form.get("master_password")
    password_hint = request.form.get("hint")

    try:
        conn = database.connect(db_file)
        if conn is None:
            raise Exception("Failed to connect to the database.")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO REGISTRATION (EMAIL, NAME, MASTER_PASSWORD, PASSWORD_HINT) VALUES (?, ?, ?, ?)",
                       (email, name, master_password, password_hint))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('profile'))
    except Exception as e:

        flash("Failed to create your account. Try again!")
        print("Error:", e)  # Print error for debugging purposes

        return redirect(url_for('registration'))

@app.route('/profile')
def comp():
    return render_template('profile.html')

@app.route('/profile')
def profile():
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

@app.route("/copy", methods=["POST"])
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

from flask import Flask, render_template, request
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
    return render_template('login.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

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

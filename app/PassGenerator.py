import os
import secrets
import string
import random
from flask import (
    Blueprint,
    g,
    request,
    flash,
    session,
    redirect,
    render_template,
    url_for,
    jsonify,
)
from app.forms import SearchForm
from app.auth import login_required
from app.db import get_db

# bp = Blueprint("password_generator", __name__, url_prefix="/password_generator", template_folder="templates")
bp = Blueprint("vault", __name__, url_prefix="/vault", template_folder="templates")


def generate_password(
    length=15, number_digits=0, number_upper=0, number_special=0, special=None
):
    alphabet = string.ascii_letters + string.digits
    if number_special and special:
        alphabet += special
    while True:
        password = "".join(secrets.choice(alphabet) for i in range(length))
        if (
            any(c.islower() for c in password)
            # Contains number of upper
            and sum(c.isupper() for c in password) == number_upper
            # Contains number of digits
            and sum(c.isdigit() for c in password) >= number_digits
            and (
                # Check for number of special
                (number_special == 0)
                # Then check for special
                or (sum(c in special for c in password) == number_special)
            )
        ):
            break

    return password


def generate_number(length):
    digits = string.digits
    return "".join(secrets.choice(digits) for i in range(length))


"""def generate_password(
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
    remaining_length = length - len(password)
    for _ in range(remaining_length):
        password += random.choice(characters)

    password = "".join(random.sample(password, len(password)))
    return password"""

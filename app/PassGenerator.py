import os
from pathlib import Path
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


def generate_passphrase(
    length=4, delimiter="-", capitalize=False, include_number=False
):
    # Delimiter can be a single character
    if len(delimiter) > 1:
        return None
    # Max length
    if length > 20:
        return None
    filepath = Path(__file__).parent / "AgileWords.txt"
    with open(filepath) as wordlist:
        words = [word.strip() for word in wordlist]
        password = delimiter.join(secrets.choice(words) for i in range(length))

    if capitalize:
        password = password.title()

    if include_number:
        index = password.index(delimiter)
        password = password[:index] + generate_number(1) + password[index:]
    return password


def generate_username():
    pass

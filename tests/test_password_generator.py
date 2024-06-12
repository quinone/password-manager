from pathlib import Path
import pytest
from app.PassGenerator import generate_passphrase, generate_password, generate_username


def test_generate_passphrase_default():
    passphrase = generate_passphrase()
    wordlist = passphrase.split("-")
    assert len(wordlist) == 4


def test_generate_passphrase_random():
    assert generate_passphrase() != generate_passphrase()


@pytest.mark.parametrize(
    ("length", "delimeter", "result"),
    (
        (2, "-", 2),
        (6, "!", 6),
        (5, ":", 5),
        (20, "£", 20),
        (5, "#", 5),
        (3, "", 1),
    ),
)
def test_generate_passphrase(length, delimeter, result):
    passphrase = generate_passphrase(length=length, delimiter=delimeter)
    print(passphrase)
    if not delimeter:
        wordlist = [passphrase]
    else:
        wordlist = passphrase.split(delimeter)
    print(wordlist)
    assert len(wordlist) == result


def test_generate_passphrase_too_large():
    passphrase = generate_passphrase(
        length=21,
    )
    assert passphrase == None


def test_generate_passphrase_delimiter_too_large():
    passphrase = generate_passphrase(delimiter="--")
    assert passphrase == None


def test_generate_passphrase_capitalize():
    passphrase = generate_passphrase(capitalize=True)
    wordlist = passphrase.split("-")
    print(wordlist)
    for word in wordlist:
        assert word[0].isupper()


def test_generate_passphrase_add_number():
    passphrase = generate_passphrase(include_number=True)
    print(passphrase)
    assert any(c.isdigit() for c in passphrase)
    assert passphrase.isalpha() == False


@pytest.fixture
# load wordlist
def wordlist():
    filepath = Path(__file__).parent / "AgileWords.txt"
    with open(filepath) as wordlist:
        return [word.strip() for word in wordlist]


def test_generate_username(wordlist):
    username = generate_username()
    assert username[:-4] in wordlist
    assert username[-4:].isdigit()


def test_generate_username_capitalize_true():
    username = generate_username(capitalize=True)
    assert username[0].isupper()


def test_generate_username_capitalize_false():
    username = generate_username()
    assert username[0].islower()


def test_generate_username_number_false():
    username = generate_username(include_number=False)
    assert username[-4:].isalpha()


def test_generate_username_random():
    assert generate_username() != generate_username()


def test_generate_password_randoom():
    assert generate_password() != generate_password()


def test_generate_password_default():
    password = generate_password()
    assert len(password) == 15

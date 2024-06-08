import pytest
from app.PassGenerator import generate_passphrase


def test_generate_passphrase_default():
    passphrase = generate_passphrase()
    wordlist = passphrase.split("-")
    assert len(wordlist) == 4


@pytest.mark.parametrize(
    ("length", "delimeter", "result"),
    (
        (2, "-", 2),
        (6, "-", 6),
        (5, ":", 5),
    ),
)
def test_generate_passphrase(length, delimeter, result):
    passphrase = generate_passphrase(length=length, delimiter=delimeter)
    print(passphrase)
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
    for word in wordlist:
        assert word[0].isupper

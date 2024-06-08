import pytest
from app.PassGenerator import generate_passphrase




def test_generate_passphrase():
    passphrase = generate_passphrase() 
    print(passphrase)
    wordlist = passphrase.split('-')
    print(wordlist)
    assert len(wordlist) == 4
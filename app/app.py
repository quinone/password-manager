from flask import Flask

# Test file to check if flask is working for now
# Will call the create_app function 

# TODO move Flask to create_app function in __init__.py in app folder
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
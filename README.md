# Password-manager
Password management application for a college group project. 

## Features
- Account sign up [complete]
- Login [complete]
- Add password items [complete]
- Read password items [complete]
- Generate random passwords (incomplete)
- Confirm email address (incomplete)


## Installation 

### Install Flask

Follow the steps on the [Flask](https://flask.palletsprojects.com/en/3.0.x/installation/) website.

## Run Flask Application
Clone repository with 
```
git clone git@github.com:quinone/password-manager.git
```

Initialize the database using the your IDE's terminal:  
```
flask init-db
```

Run application using the your IDE's terminal: 
```
flask run
```

## Testing 
Using Pytest 
While in the parent directory using the your IDE's terminal use: 
```
pytest
```
Specific test scripts can be ran alone:
```
pytest <path to test scripts>/<test_name>.py
```
Example:
```
pytest ./tests/test_folder.py
```

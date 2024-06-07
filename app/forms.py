from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class NewItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 50)])
    username = StringField("Username", validators=[Length(0, 250)])
    password = PasswordField("Password")
    uri = StringField("URI", validators=[Length(0, 250)])
    notes = TextAreaField("Notes")
    folder_name = StringField("Folder")
    submit = SubmitField("Submit")


# Search form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Password Generate form
class PasswordForm(FlaskForm):
    pass

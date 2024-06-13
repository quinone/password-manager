from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from wtforms import SelectField, HiddenField


class NewItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 50)])
    username = StringField("Username", validators=[Length(0, 250)])
    password = PasswordField("Password")
    #show_password = BooleanField("Show Password")
    uri = StringField("URI", validators=[Length(0, 250)])
    notes = TextAreaField("Notes")
    folder_select = SelectField("Select Folder", choices=[], coerce=str)
    new_folder_name = StringField("New Folder Name", validators=[Length(0, 50)])
    submit = SubmitField("Submit")



# Search form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")

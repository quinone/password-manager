from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Length


class NewItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 50)])
    username = StringField("Username", validators=[Length(0, 250)])
    password = PasswordField("Password")
    uri = StringField("URI", validators=[Length(0, 250)])
    notes = TextAreaField("Notes")
    folderID = StringField("Folder")
    submit = SubmitField("Submit")

class NewItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=250)])
    username = StringField('Username', validators=[Length(max=250)])
    password = PasswordField('Password', validators=[Length(max=250)])
    uri = StringField('URI', validators=[Length(max=250)])
    notes = TextAreaField('Notes', validators=[Length(max=250)])
    folderID = SelectField('Folder', validators=[DataRequired()], coerce=str)

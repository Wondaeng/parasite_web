from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.fields.html5 import EmailField, IntegerRangeField
from wtforms.validators import DataRequired, InputRequired, Length, EqualTo, Email, NumberRange

class RegisterForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Email()])
    userid = StringField('userid', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('re_password', 'Password does not match')])
    re_password = PasswordField('re_password', validators=[DataRequired()])

class UserLoginForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('password', validators=[DataRequired()])

class FileUploadForm(FlaskForm):
    user_name = StringField('user_name', validators=[DataRequired()])
    email_address = StringField('email_address', validators=[DataRequired()])
    task_name = StringField('task_name', validators=[DataRequired()])
    sensitivity = IntegerRangeField('sensitivity', validators=[DataRequired()]) # Not WORKING? 
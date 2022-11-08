from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, EmailField, IntegerRangeField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class RegisterForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('re_password', 'Password does not match')])
    re_password = PasswordField('re_password', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired(), Email()])


class UserLoginForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('password', validators=[DataRequired()])

class FileUploadForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=25)])
    taskname = StringField('taskname', validators=[DataRequired()])
    threshold = IntegerRangeField('threshold', validators=[DataRequired()])
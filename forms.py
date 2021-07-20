from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from models import User
from passlib.hash import pbkdf2_sha256

class Registration(FlaskForm):
    username = StringField('username', validators=[InputRequired(message="Username required"), Length(
        min=4, max=12, message="Username must be between 4 and 25 characters")])
    email = EmailField("email", validators=[InputRequired("Please Enter valid email address"), Length(
        min=8, max=40, message="Email must be between 8 to 20 characters")])
    password = PasswordField("password", validators=[InputRequired("password required"), Length(
        min=6, max=18, message="Password must be between 6 to 18 characters")])
    confirm = PasswordField("confirm", validators=[InputRequired(
        "Password required"), EqualTo("password", message="Password must match")])
    role = StringField("role",validators=[InputRequired("Role Required")])
    
    def validate_username(self,username):
        user_object = User.query.filter_by(username=username).first()
        if user_object:
            raise ValidationError("Username already Exists!")


def validator(form,field):
    username = form.username.data
    password = field.data
    user_data = User.query.filter_by(username=username).first()
    if user_data is None:
        raise ValidationError("Username or Password Incorrect")
    elif(not pbkdf2_sha256.verify(password,user_data.password)):
        raise ValidationError("Username or Password Incorrect")
    else:
        return True

class Login(FlaskForm):
	username = StringField('username', validators=[InputRequired(message="Username required"), Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
	password = PasswordField("password", validators=[InputRequired("password required"),validator])


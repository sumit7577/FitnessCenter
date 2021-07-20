from flask import Flask,render_template,redirect,request
from flask_login.utils import login_required
from flask_sqlalchemy import SQLAlchemy
from models import *
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/fitness"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'the random string'
db = SQLAlchemy(app)
login = LoginManager(app)
login.init_app(app)


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
    
    def validate_username(form,username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already Exists!")


def validator(form,field):
    username = form.username.data
    password = field.data
    print(password)
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



@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@app.route("/register", methods=["GET", "POST"])
def register():
    message = None
    registrationForm = Registration()
    if(registrationForm.validate_on_submit()):
        username = registrationForm.username.data
        email = registrationForm.email.data
        password = registrationForm.password.data
        enc = pbkdf2_sha256.hash(password)
        role = registrationForm.role.data
        user = User(username=username, email=email, password=enc, role=role)
        db.session.add(user)
        try:
            db.session.commit()
            message = "Registration Successfull"
        except:
            message = "Something error happened"
        
    else:
        message = "Please fill up the form correctly"

    return render_template("register.html", message=message, reg_form=registrationForm)


@app.route("/login", methods=["GET", "POST"])
def login():
    loginForm = Login()
    if(loginForm.validate_on_submit()):
        username = loginForm.username.data
        user = User.query.filter_by(username=username).first()
        login_user(user)
        if(current_user.is_authenticated):
            return redirect("/")
        else:
            return redirect("/register")

    return render_template("login.html", login_form=loginForm)


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if not current_user.is_authenticated:
        return redirect("/login")
    return render_template("home.html")


@app.route("/class",methods=["GET","POST"])
@login_required
def clas():
    message = None
    if current_user.role == "Trainer":
        memeberData = Event.query.filter_by(owner= current_user).all()

        if(request.method == "POST"):
            title = request.form.get("title")
            subtitle = request.form.get("sub")
            start = request.form.get("start")
            end = request.form.get("end")
            desc = request.form.get("desc")
            classData = Event(Title= title,Subtitle=subtitle,Start=start,End=end,Description=desc,owner_id=current_user.id)
            db.session.add(classData)
            try:
                db.session.commit()
                message = "Class Scheduled Successfully"
            except:
                message = "Somthing error happened"
    else:
        memeberData = Event.query.all()
    return render_template("class.html",message=message,data=memeberData)


@app.route("/class/<string:id>/",methods=["GET","POST"])
def edit(id):
    classData = Event.query.filter_by(id=id).first()
    subscribedUsers = Subscribed.query.filter_by(projectName=classData.Title).all()
    message = None
    if current_user.role == "Member":
        if request.method == "POST":
            projectName = classData.Title
            userName= current_user.username
            subscribers = Subscribed(projectName=projectName,username=userName)
            db.session.add(subscribers)
            try:
                db.session.commit()
                message = "Class Subscribed Successfull"
            except:
                message = "Something Error happened"
    return render_template("edit.html",data=classData,message=message,users=subscribedUsers)

@app.route("/delete/<string:id>/",methods=["GET","POST"])
def delete(id):
    classData = Event.query.filter_by(id=id).first()
    if(current_user.username == "sumit"):
        db.session.delete(classData)
        db.session.commit()
        return redirect ("/class")



@app.route("/deleteuser/<string:id>/",methods=["GET","POST"])
def deleter(id):
    userData = User.query.filter_by(id=id).first()
    if(current_user.username == "sumit"):
        db.session.delete(userData)
        db.session.commit()
        return redirect ("/class")



@app.route("/admin",methods=["GET","POST"])
@login_required
def admin():
    if(current_user.username != "sumit"):
        return redirect("/")
    message = None
    users = User.query.all()
    trainer = User.query.filter_by(role="Trainer").all()
    classes = Event.query.all()
    if request.method == "POST":
        username = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password") 
        role = request.form.get("role")
        title = request.form.get("title")
        subtitle = request.form.get("sub")
        start = request.form.get("start")
        end = request.form.get("end")
        desc = request.form.get("desc")
        trainer = request.form.get("trainer")
        if username != None:
            enc = pbkdf2_sha256.hash(password)
            user = User(username=username,email=email,password=enc,role=role)
            db.session.add(user)
            db.session.commit()
            message = "User added Successful"
        elif(title != None):
            event = Event(Title=title,Subtitle=subtitle,Start=start,End=end,Description=desc,owner_id=trainer)
            db.session.add(event)
            db.session.commit()    
            message = "Class Scheduled Successfull"
    return render_template("admin.html",user=users,message=message,clas=classes,trainer=trainer)

@app.route("/logout")
def logout():
	logout_user()
	return redirect("/login")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)

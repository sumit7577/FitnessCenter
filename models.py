from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import backref

db = SQLAlchemy()

class User(UserMixin,db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(12), unique=True, nullable=False)
	email = db.Column(db.String(40), nullable=False, unique=False)
	password = db.Column(db.String(200),nullable =False,unique=False)
	role = db.Column(db.String(25),nullable = False,unique=False)
	events = db.relationship("Event",backref="owner")


class Event(db.Model):
	__tablename__ = "Event"
	id = db.Column(db.Integer, primary_key = True)
	Title = db.Column(db.String(25),nullable = False)
	Subtitle = db.Column(db.String(25), nullable=True)
	Start = db.Column(db.DateTime,default=datetime.now)
	End = db.Column(db.DateTime)
	Description= db.Column(db.String(200), nullable= False)
	owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Subscribed(db.Model):
	__tablename__= "subscription"
	id = db.Column(db.Integer,primary_key = True)
	username = db.Column(db.String(25),nullable = False)
	projectName = db.Column(db.String(30),nullable = False)
	



	

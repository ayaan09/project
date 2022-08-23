from flask import Flask, redirect, url_for, render_template, request, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import timedelta
import datetime
app = Flask(__name__)



app.secret_key="secret"
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///users.sqlite3' 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.permanent_session_lifetime = timedelta(minutes=45)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id",db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    balance = db.Column(db.Float)
    card_no = db.Column(db.Integer)
    

    def __init__(self, name, email, username, password,balance):
        self.name=name
        self.email=email
        self.username=username
        self.password=password
        self.balance = balance
        self.card_no=0

    def add_balance(self, amount):
        self.balance+=amount

    def deduct_balance(self, amount):
        self.balance-=amount

class transactions(db.Model):
    _id = db.Column("id",db.Integer, primary_key=True)
    payee_id = db.Column(db.Integer)
    payer_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, payee, payer, amount):
        self.payee_id= payee
        self.payer_id = payer
        self.amount = amount


class loans(db.Model):
    _id = db.Column("id",db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    loanPaid = db.Column(db.Boolean, default=False)
    loanReceipientId = db.Column(db.Integer)


    def __init__(self, amount, receipient):
        self.amount = amount
        self.loanReceipientId = receipient
    
    def loan_paid(self):
        loanPaid = True

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    phone_no = db.Column(db.String(15), unique=True)  
    is_admin = db.Column(db.Boolean, default=False) 
    password = db.Column(db.String(150))
    account = db.relationship("Account", uselist=False, back_populates="user")


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    amount = db.Column(db.Numeric(9, 2))
    created = db.Column(db.DateTime(timezone=True), default=func.now() ) 
    updated = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.String(150)) #active or inactive
    user = db.relationship("User", back_populates="account")
    transactions = db.relationship("Transaction", back_populates="account")


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"))
    transaction_type = db.Column(db.String(150)) #deposit or withdraw
    amount = db.Column(db.Numeric(9, 2))
    created = db.Column(db.DateTime(timezone=True), default=func.now() )
    account = db.relationship("Account", back_populates="transactions")
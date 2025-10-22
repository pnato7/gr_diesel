from flask import session
from ..models.login import User
from ..connection import db
from werkzeug.security import check_password_hash

def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['is_owner'] = user.is_owner
        return True
    return False

def logout():
    session.clear()

def create_owner(username, password_hash):
    if User.query.filter_by(username=username).first():
        return None
    u = User(username=username, password=password_hash, is_owner=True)
    db.session.add(u)
    db.session.commit()
    return u

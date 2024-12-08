import hashlib
from linecache import cache

from app import db
from app.models import User


def check_login(username, password):
    password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()

def add_user(username, password, first_name, last_name):
    try:
        user = User(username = username, password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest()), first_name = first_name, last_name = last_name)
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        return None

def get_user_by_id(user_id):
    return User.query.get(user_id)
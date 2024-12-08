import hashlib

from app import db, Genre
from app.models import User, Book


def check_login(username, password):
    try:
        password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
        return User.query.filter(User.username == username,
                                 User.password == password).first()
    except Exception as e:
        return None


def add_user(username, password, first_name, last_name):
    try:
        user = User(username=username, password=str(hashlib.md5(password.strip().encode("utf-8")).hexdigest()),
                    first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        return None


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_all_book(orderby):
    if orderby:
        if orderby == "o1":
            return Book.query.order_by(Book.price.asc()).all()
        elif orderby == "o2":
            return Book.query.order_by(Book.price.desc()).all()
    else:
        return Book.query.order_by(Book.create_date.desc()).all()


def get_book_by_genre(genre_name):
    return Book.query.join(Book.genres).filter(Genre.name == genre_name).all()

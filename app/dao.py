import hashlib

from app import db, Genre, Order, OrderStatus
from app.models import User, Book, OrderDetail


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

def get_cart(user_id):
    return Order.query.filter_by(customer_id=user_id, order_status=OrderStatus.PENDING).first()


def create_cart(user_id):
    cart = get_cart(user_id)
    if cart is None:
        cart = Order(customer_id=user_id, order_status=OrderStatus.PENDING)
        db.session.add(cart)
        db.session.commit()
    return cart

def create_order_cart(**kwargs):
    o = OrderDetail(**kwargs)
    current_order = OrderDetail.query.filter_by( book_id=o.book_id, order_id = o.order_id ).first()
    if current_order is None:
        db.session.add(o)
    else:
        current_order.quantity += int(o.quantity)
    db.session.commit()

def get_total_price(cart):
    rs = 0
    for cart_detail in cart.order_details:
        rs += cart_detail.unit_price
    return rs

def delete_cart_detail(id, user_id):
    o = OrderDetail.query.join(Order, Order.id == OrderDetail.order_id).filter(OrderDetail.id == id, Order.customer_id == user_id).first()
    if o:
        db.session.delete(o)
        db.session.commit()

def update_cart_detail(cart_id, new_quantity):
    o = OrderDetail.query.filter_by(id=cart_id).first()
    o.quantity = new_quantity
    db.session.commit()

def get_book_detail(id):
    return Book.query.get(id)
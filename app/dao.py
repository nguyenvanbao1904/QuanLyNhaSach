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

def get_cart_by_user_id(user_id):
    return Order.query.filter_by(customer_id=user_id, order_status=OrderStatus.PENDING).first()

def create_cart(user_id):
    cart = get_cart_by_user_id(user_id)
    if cart is None:
        print("eyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
        cart = Order(customer_id=user_id, order_status=OrderStatus.PENDING)
        db.session.add(cart)
        db.session.commit()
    return cart

def add_product_in_cart(**kwargs):
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

def delete_product_in_cart(cart_id, user_id):
    o = OrderDetail.query.join(Order, Order.id == OrderDetail.order_id).filter(OrderDetail.id == cart_id, Order.customer_id == user_id).first()
    if o:
        db.session.delete(o)
        db.session.commit()

def update_cart(product_in_cart_id, new_quantity):
    o = OrderDetail.query.filter_by(id=product_in_cart_id).first()
    o.quantity = new_quantity
    db.session.commit()

def get_cart_total_quantity(user_id):
    cart = create_cart(user_id)
    rs = 0
    for cart_detail in cart.order_details:
        rs += cart_detail.quantity
    return rs

def get_product_detail(product_id):
    return Book.query.get(product_id)

def get_order_by_id(order_id, user_id = None, status = None):
    if user_id:
        return Order.query.filter_by(customer_id=user_id, id=order_id).first()
    return Order.query.get(order_id)

def change_status_order(order, new_created_date, order_status):
    o = Order.query.filter_by(id=order.id, order_status=order.order_status).first()
    o.order_status = order_status
    o.created_date = new_created_date
    db.session.commit()
import enum
from app import db, app
import datetime

class Item(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.now())

class AccountRole(enum.Enum):
    ADMIN = 'admin'
    NhanVien = 'nhanVien'
    QuanLyKho = 'quanLyKho'
    KhachHang = 'khachHang'


class User(Item):
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    first_name = db.Column(db.String(30), unique=True, nullable=False)
    last_name = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    account_role = db.Column(db.Enum(AccountRole), nullable=False, default=AccountRole.KhachHang)
    book_receipts = db.relationship('BookReceipt', backref='user', lazy=True)
    buy_others = db.relationship('Order', backref='customer', lazy=True, foreign_keys='Order.customer_id')
    sell_others = db.relationship('Order', backref='seller', lazy=True, foreign_keys='Order.employee_id')

    def __str__(self):
        return self.first_name + ' ' + self.last_name

Book_Author = db.Table('book_author',
                       db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True),
                       db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True))

Book_Genre = db.Table('book_genre',
                       db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
                       db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True))


class Author(Item):
    name = db.Column(db.String(50), unique=True, nullable=False)
    def __str__(self):
        return self.name

class Genre(Item):
    name = db.Column(db.String(50), unique=True, nullable=False)
    def __str__(self):
        return self.name

class Book(Item):
    name = db.Column(db.String(50), unique=True, nullable=False)
    authors = db.relationship('author', secondary=Book_Author, lazy=True, backref=db.backref('books', lazy=True))
    genres = db.relationship('genre',  secondary=Book_Genre ,backref=db.backref('books', lazy=True), lazy=True)
    price = db.Column(db.Float, nullable=False)

    book_receipts = db.relationship('BookReceiptDetail', backref='book', lazy=True)
    order_details = db.relationship('OrderDetail', backref='book', lazy=True)
    book_inventory = db.relationship('BookInventory', backref='book', lazy=True, uselist=False)

    def __str__(self):
        return self.name

class BookReceipt(Item):
    book_receipt_details = db.relationship('BookReceiptDetail', backref='receipt', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    def __str__(self):
        return f"Receipt {self.id}"

class BookReceiptDetail(db.Model):
    book_id = db.Column(db.Integer, db.ForeignKey(Book.id), primary_key=True)
    book_receipt_id = db.Column(db.Integer, db.ForeignKey(BookReceipt.id), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

class BookInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_quantity = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey(Book.id), nullable=False, unique=True)

class OrderStatus(enum.Enum):
    DONE = 'done'
    PROCESSING = 'processing'
    FAILED = 'failed'

class Order(Item):
    customer_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    other_details = db.relationship('OrderDetail', backref='order', lazy=True, cascade='all,delete')
    order_status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.DONE)


class OrderDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey(Book.id), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey(Order.id), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        if int(input('1:Tao moi\n0:Xoa\n')):
            db.create_all()
        else:
            db.drop_all()
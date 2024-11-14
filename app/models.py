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

class Account(Item):
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    account_role = db.Column(db.Enum(AccountRole), nullable=False, default=AccountRole.KhachHang)
    user = db.relationship('User', backref='account', uselist=False, cascade="all, delete-orphan")

    def __str__(self):
        return self.user_name

class User(Item):
    first_name = db.Column(db.String(30), unique=True, nullable=False)
    last_name = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey(Account.id), nullable=False, unique=True)
    book_receipt = db.relationship('BookReceipt', backref='user', lazy=True)
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
    authors = db.relationship('Author', secondary=Book_Author, lazy=True, backref=db.backref('books', lazy=True))
    genres = db.relationship('Genre',  secondary=Book_Genre ,backref=db.backref('books', lazy=True), lazy=True)
    book_receipts = db.relationship('BookReceiptDetail', backref='book', lazy=True)
    price = db.Column(db.Float, nullable=False)
    def __str__(self):
        return self.name

class BookReceipt(Item):
    books = db.relationship('BookReceiptDetail', backref='receipt', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    book_store_id = db.Column(db.Integer, db.ForeignKey('book_store.id'), nullable=False)



class BookReceiptDetail(db.Model):
    book_id = db.Column(db.Integer, db.ForeignKey(Book.id), primary_key=True)
    book_receipt_id = db.Column(db.Integer, db.ForeignKey(BookReceipt.id), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)


class BookStore(Item):
    name = db.Column(db.String(50), unique=True, nullable=False)
    book_receipts = db.relationship('BookReceipt', backref='bookStore', lazy=True)

    def __str__(self):
        return self.name

if __name__ == '__main__':
    with app.app_context():
        if int(input('1:Tao moi\n0:Xoa\n')):
            db.create_all()
        else:
            db.drop_all()
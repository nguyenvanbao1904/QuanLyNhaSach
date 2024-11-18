from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app, db
from app.models import User, Book, Author, Genre, BookReceipt, BookReceiptDetail,BookInventory, Order, OrderDetail

admin = Admin(app=app, name='Book Store Admin')


class UserView(ModelView):
    form_excluded_columns = ('book_receipts','create_date','buy_others', 'sell_others')

admin.add_view(UserView(User, db.session))

class BookView(ModelView):
    form_excluded_columns = ('book_receipts','create_date', 'order_details', 'book_inventory')

admin.add_view(BookView(Book, db.session))

class BookReceiptView(ModelView):
    form_excluded_columns = ('books',)

admin.add_view(BookReceiptView(BookReceipt, db.session))


class BookReceiptDetailView(ModelView):
    form_excluded_columns = ('book_store_id',)

admin.add_view(BookReceiptDetailView(BookReceiptDetail, db.session))

class BaseView(ModelView):
    form_excluded_columns = ('create_date')

admin.add_view(BaseView(Author, db.session))
admin.add_view(BaseView(Genre, db.session))

class OrderView(ModelView):
    form_excluded_columns = ('other_details', 'create_date')

admin.add_view(OrderView(Order, db.session))

class OrderDetailView(ModelView):
    form_excluded_columns = ('create_date', 'unit_price')

admin.add_view(OrderDetailView(OrderDetail, db.session))

admin.add_view(ModelView(BookInventory, db.session))





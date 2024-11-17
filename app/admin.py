from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app, db
from app.models import Account, User, Book, Author, Genre, BookReceipt, BookStore, BookReceiptDetail, Order, OrderDetail

admin = Admin(app=app, name='Quản lý của hàng sách')


class AccountView(ModelView):
    form_excluded_columns = ('user','create_date')

admin.add_view(AccountView(Account, db.session))


class UserView(ModelView):
    form_excluded_columns = ('book_receipt','create_date','buy_other_ids', 'sell_other_ids')

admin.add_view(UserView(User, db.session))


class BookView(ModelView):
    form_excluded_columns = ('book_receipts','create_date')

admin.add_view(BookView(Book, db.session))


class BookReceiptView(ModelView):
    form_excluded_columns = ('books',)

admin.add_view(BookReceiptView(BookReceipt, db.session))


class BookReceiptDetailView(ModelView):
    form_excluded_columns = ('book_store_id',)

admin.add_view(BookReceiptDetailView(BookReceiptDetail, db.session))


class BookStoreView(ModelView):
    form_excluded_columns = ('book_store_logs','book_receipts')

admin.add_view(BookStoreView(BookStore, db.session))

class BaseView(ModelView):
    form_excluded_columns = ('create_date')

admin.add_view(BaseView(Author, db.session))
admin.add_view(BaseView(Genre, db.session))

class OrderView(ModelView):
    form_excluded_columns = ('other_details', 'create_date')

admin.add_view(OrderView(Order, db.session))
admin.add_view(BaseView(OrderDetail, db.session))





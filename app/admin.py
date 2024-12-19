import hashlib

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app import app, db
from app.models import User, Book, Author, Genre, BookReceipt, BookReceiptDetail, BookInventory, Order, OrderDetail, \
    ConfigSystem

from flask_wtf.file import FileField, FileAllowed
from wtforms import validators
import cloudinary.uploader

admin = Admin(app=app, name='Book Store Admin', url='/flask_admin')


class UserView(ModelView):
    form_excluded_columns = ('is_active', 'book_receipts', 'buy_orders', 'sell_orders', 'create_date')

    form_extra_fields = {
        'avatar': FileField('Avatar', validators=[
            validators.Optional(),
            FileAllowed(['jpg', 'jpeg', 'png'], 'Only images are allowed!')
        ])
    }

    def on_model_change(self, form, model, is_created):
        # Upload trực tiếp lên Cloudinary
        if form.avatar.data:
            upload_result = cloudinary.uploader.upload(form.avatar.data)
            model.avatar = upload_result.get('url')  # Lưu link ảnh vào DB

        if form.password.data:
            model.password = str(hashlib.md5(form.password.data.strip().encode("utf-8")).hexdigest())
        super(UserView, self).on_model_change(form, model, is_created)


admin.add_view(UserView(User, db.session))


class BookView(ModelView):
    form_excluded_columns = ('book_receipts', 'create_date', 'order_details', 'book_inventory')


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
    form_excluded_columns = ('other_details')


admin.add_view(OrderView(Order, db.session))


class OrderDetailView(ModelView):
    form_excluded_columns = ('create_date', 'unit_price')


admin.add_view(OrderDetailView(OrderDetail, db.session))

admin.add_view(ModelView(BookInventory, db.session))

admin.add_view(ModelView(ConfigSystem, db.session))

import hashlib

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from wtforms.validators import ValidationError

from app import app, db, models
from flask_admin.base import AdminIndexView

from flask_wtf.file import FileField, FileAllowed
from wtforms import validators
import cloudinary.uploader
import re

class BaseAdminView(ModelView):
    column_searchable_list = ['name']


class BookAdminView(BaseAdminView):
    column_filters = ['genres.name', 'authors.name']
    column_labels = {
        'genres.name': 'Filter by genre',
        'authors.name': 'Filter by author',
    }

    form_excluded_columns = ('book_receipts', 'order_details', 'book_inventory', 'create_date')

    form_extra_fields = {
        'image': FileField('image', validators=[
            validators.Optional(),
            FileAllowed(['jpg', 'jpeg', 'png'], 'Only images are allowed!')
        ])
    }

    def on_model_change(self, form, model, is_created):
        if form.image.data:
            upload_result = cloudinary.uploader.upload(form.image.data)
            model.image = upload_result.get('url')


class MyAdminIndexView(AdminIndexView):
    def is_visible(self):
        return False


class AuthorAdminView(BaseAdminView):
    form_columns = ['name']


class GenreAdminView(BaseAdminView):
    form_columns = ['name']


class UserView(ModelView):
    form_excluded_columns = ('is_active', 'book_receipts', 'buy_orders', 'sell_orders', 'create_date')

    form_extra_fields = {
        'avatar': FileField('Avatar', validators=[
            validators.Optional(),
            FileAllowed(['jpg', 'jpeg', 'png'], 'Only images are allowed!')
        ])
    }

    def on_model_change(self, form, model, is_created):
        if form.avatar.data:
            upload_result = cloudinary.uploader.upload(form.avatar.data)
            model.avatar = upload_result.get('url')

        if form.password.data:
            pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$'
            if not re.match(pattern, model.password):
                raise ValidationError(
                    "Mật khẩu phải có ít nhất 8 ký tự, bao gồm ít nhất một chữ cái viết hoa, một chữ cái viết thường và một chữ số.")  # W

            model.password = str(hashlib.md5(form.password.data.strip().encode("utf-8")).hexdigest())
        super(UserView, self).on_model_change(form, model, is_created)


admin = Admin(app=app, name='', url='/flask-admin', index_view=MyAdminIndexView())
admin.add_view(BookAdminView(models.Book, db.session, name="Quản lý Sách"))
admin.add_view(AuthorAdminView(models.Author, db.session, name="Tác giả"))
admin.add_view(GenreAdminView(models.Genre, db.session, name="Thể loại"))
admin.add_view(UserView(models.User, db.session, name="Quản lý người dùng"))

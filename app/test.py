from sqlalchemy import func
from sqlalchemy.sql.functions import user

from app import db, app
from app import models

def addBook(user, book_store, book_quantity_arr):
   pass

def updateBook(order_id, book_store):
    pass


def orderBook(customer, seller, book_quantity_arr, book_store):
   pass

if __name__ == '__main__':
    with app.app_context():
        # customer = models.User.query.filter_by(id = 1).first()
        # seller = models.User.query.filter_by(id = 2).first()
        # user = models.User.query.filter_by(id = 3).first()
        # book_store = models.BookStore.query.first()
        # book1 = models.Book.query.first()
        # book2 = models.Book.query.filter_by(id=4).first()
        # updateBook(3, book_store)
        pass
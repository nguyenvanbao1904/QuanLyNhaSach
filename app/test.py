from sqlalchemy import func
from sqlalchemy.sql.functions import user

from app import db, app
from app import models

def addBook(user, book_store, book_quantity_arr):
    try:
        book_receipt = models.BookReceipt(user_id=user.id, book_store_id=book_store.id)
        db.session.add(book_receipt)
        db.session.commit()
        book_receipt_detail = []
        for book, quantity in book_quantity_arr:
            print(book_receipt.id)
            book_receipt_detail_tmp = models.BookReceiptDetail(book_id=book.id, quantity=quantity, book_receipt_id=book_receipt.id)
            book_receipt_detail.append(book_receipt_detail_tmp)
        book_receipt.books = book_receipt_detail
        db.session.commit()
        print("done")
    except Exception as e:
        print("huhu :((")
        print(e)

def get_books_in_store(book_store_id):
    results = db.session.query(
        models.Book.id,
        models.Book.name,
        func.sum(models.BookReceiptDetail.quantity).label("total_quantity")
    ).join(models.BookReceiptDetail, models.Book.id == models.BookReceiptDetail.book_id
    ).join(models.BookReceipt, models.BookReceiptDetail.book_receipt_id == models.BookReceipt.id
    ).filter(models.BookReceipt.book_store_id == book_store_id
    ).group_by(models.Book.id, models.Book.name).all()

    # In kết quả
    for book_id, book_name, total_quantity in results:
        print(f"Book ID: {book_id}, Name: {book_name}, Total Quantity: {total_quantity}")

def updateBook(order_id, book_store):
    order_details = models.OrderDetail.query.filter_by(order_id=order_id).all()
    book_receipts = book_store.book_receipts
    ######################Tiếp tục ở đây##################################


def orderBook(customer, seller, book_quantity_arr, book_store):
    try:
        order = models.Order(customer_id=customer.id, employee_id=seller.id)
        order_details = []
        for book, quantity in book_quantity_arr:
            order_detail_tmp = models.OrderDetail(book_id=book.id, quantity=quantity, unit_price=book.price * quantity)
            order_details.append(order_detail_tmp)

        order.other_details = order_details
        order.order_status = models.OrderStatus.DONE
        db.session.add(order)
        db.session.commit()
        updateBook(order.id, book_store)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    with app.app_context():
        customer = models.User.query.filter_by(id = 1).first()
        seller = models.User.query.filter_by(id = 2).first()
        # user = models.User.query.filter_by(id = 3).first()
        book_store = models.BookStore.query.first()
        book1 = models.Book.query.first()
        book2 = models.Book.query.filter_by(id=4).first()
        # addBook(user=user, book_store=book_store, book_quantity_arr=[(book1, 140), (book2, 160)])
        # get_books_in_store(book_store_id=1)
        # orderBook(customer=customer, seller=seller, book_quantity_arr=[(book1, 30), (book2, 50)], book_store=book_store)
        updateBook(3, book_store)
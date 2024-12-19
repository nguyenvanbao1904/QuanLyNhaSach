def get_total_revenue_and_books_every_month(order_details_status_done):
    data_total_revenue_and_books_every_month = {}
    for order_detail_status_done in order_details_status_done:
        key = f'{order_detail_status_done.order.create_date.month}/{order_detail_status_done.order.create_date.year}'
        revenue = order_detail_status_done.quantity * order_detail_status_done.book.price
        if key in data_total_revenue_and_books_every_month:
            data_total_revenue_and_books_every_month[key]['revenue'] += revenue
            data_total_revenue_and_books_every_month[key]['books_sold'] += order_detail_status_done.quantity
        else:
            data_total_revenue_and_books_every_month[key] = {
                'revenue': revenue,
                'books_sold': order_detail_status_done.quantity
            }

    revenue_data = sorted(
        [
            (key, value['revenue'], value['books_sold'])
            for key, value in data_total_revenue_and_books_every_month.items()
        ],
        key=lambda item: tuple(map(int, item[0].split('/')))
    )
    return revenue_data

def get_sales_data_by_month_and_book(order_details_status_done):
    from collections import defaultdict
    sales_data = defaultdict(lambda: defaultdict(int))

    for order_detail in order_details_status_done:
        month_year = f"{order_detail.order.create_date.month:02d}/{order_detail.order.create_date.year}"
        book_name = order_detail.book.name
        quantity = order_detail.quantity
        sales_data[month_year][book_name] += quantity

    result = []
    for month_year, books in sales_data.items():
        for book_name, quantity in books.items():
            result.append((month_year, book_name, quantity))
    return result

def get_total_book_in_inventory(inventory):
    rs = 0
    for item in inventory:
        rs += item.current_quantity
    return rs

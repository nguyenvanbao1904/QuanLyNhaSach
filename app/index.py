import random
from datetime import datetime, timedelta

from app import app, login_manager, dao, OrderStatus, redis_client, models
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import login_user, logout_user, current_user
from redis_tasks import redis_utils
from app.decorator import role_required


@app.context_processor
def inject_cart_quantity():
    if current_user.is_authenticated and current_user.account_role == models.AccountRole.KhachHang:
        cart_total_quantity = dao.get_cart_total_quantity(current_user.id)
        return {'cart_total_quantity': cart_total_quantity}
    return {'cart_total_quantity': 0}


@app.route('/')
def home():
    genre = request.args.get('genre')
    orderby = request.args.get('orderby')
    if genre:
        books = dao.get_book_by_genre(genre)
    else:
        books = dao.get_all_book(orderby)

    title_book = books[random.randint(0, len(books) - 1)]
    return render_template('index.html', books=books, title_book=title_book, genre=genre)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    err_msg = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = dao.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            if user.account_role == models.AccountRole.KhachHang:
                return redirect(url_for('home'))
            elif user.account_role == models.AccountRole.NhanVien:
                return redirect(url_for('staff'))
        else:
            err_msg = "Something wrong!!!"

    return render_template("login.html", err_msg=err_msg)


@app.route("/logout")
@role_required(['khachHang', 'nhanVien'])
def logout():
    logout_user()
    return redirect('/')


@app.route("/signup", methods=["get", "post"])
def signup():
    if session.get('user'):
        return redirect(request.url)
    err_msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        if password.strip() != password_confirm.strip():
            err_msg = "Passwords don't match!"
        else:
            if dao.add_user(username=username, password=password, first_name=first_name, last_name=last_name):
                return redirect(url_for("login"))
            else:
                err_msg = "Something Wrong!!!"

    return render_template("signup.html", err_msg=err_msg)


@app.route('/cart', methods=['GET', 'POST'])
@role_required(['khachHang'])
def cart():
    if request.method == 'POST':
        try:
            my_cart = dao.create_cart(current_user.id)
            product = request.form.to_dict()
            product['order_id'] = my_cart.id
            dao.add_product_in_cart(**product)
            return jsonify({
                'success': True,
                'message': 'Item added to cart successfully'
            }), 201
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }), 500

    my_carts = dao.get_cart_by_user_id(current_user.id)
    total_price = 0
    if my_carts:
        total_price = dao.get_total_price(my_carts)
    return render_template('cart.html', carts=my_carts, total_price=total_price)


@app.route('/delete/cart/<int:cart_id>', methods=['DELETE'])
@role_required(['khachHang'])
def delete_product_in_cart(cart_id):
    try:
        dao.delete_product_in_cart(cart_id, current_user.id)
        return '', 204
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500


@app.route('/products/<int:product_id>', methods=['GET'])
def products_detail(product_id):
    book = dao.get_product_detail(product_id)
    if book:
        return render_template('products_detail.html', book=book)
    else:
        return redirect(url_for('home'))


@app.route('/update-cart', methods=['PATCH'])
@role_required(['khachHang'])
def update_cart():
    data = request.get_json()
    product_in_cart_id = data.get("product_in_cart_id")
    quantity = data.get("quantity")
    try:
        dao.update_cart(product_in_cart_id, quantity)
        return jsonify({
            'success': True,
            'message': 'Item update successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500


@app.route('/checkout', methods=['GET'])
@role_required(['khachHang'])
def checkout():
    carts = dao.get_cart_by_user_id(current_user.id)
    if carts is None:
        return redirect(url_for('not_found_page'))
    total_price = 0
    if carts:
        total_price = dao.get_total_price(carts)
    return render_template('checkout_templates/checkout.html', carts=carts, total_price=total_price)


def checkout_method(method, ttl):
    order_id = request.args.get('order_id')
    carts = dao.get_cart_by_user_id(current_user.id)
    if carts is None:
        return redirect(url_for('not_found_page'))
    total_price = dao.get_total_price(carts)
    carts.create_date = datetime.now()
    deadline = carts.create_date + timedelta(seconds=ttl)
    dao.change_status_order(carts, carts.create_date, OrderStatus.PROCESSING)
    redis_utils.set_ttl_order(order_id, ttl, "PROCESSING")
    return render_template(f'/checkout_templates/checkout_{method}.html', order_id=int(order_id),
                           total_price=total_price, deadline=deadline)


@app.route('/checkout/offline', methods=['GET'])
@role_required(['khachHang'])
def checkout_offline():
    return checkout_method("offline", 60)


@app.route('/checkout/online', methods=['GET'])
@role_required(['khachHang'])
def checkout_online():
    return checkout_method("online", 60)


@app.route('/checkout/confirm', methods=['POST'])
@role_required(['khachHang', 'nhanVien'])
def checkout_confirm():
    data = request.get_json()
    order_id = data.get("order_id")
    order = None
    if current_user.account_role == models.AccountRole.KhachHang:
        order = dao.get_order_by_id(order_id, current_user.id)
    elif current_user.account_role == models.AccountRole.NhanVien:
        order = dao.get_order_by_id(order_id)
    if order is None:
        return jsonify({'success': False, 'message': 'order not found'})
    dao.change_status_order(order, order.create_date, OrderStatus.DONE)
    redis_client.delete(int(order_id))
    return jsonify({'success': True, 'message': 'Checkout done'})


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


# staff

@app.route('/staff', methods=['GET'])
@role_required(['nhanVien'])
def staff():
    return render_template('/staff/staff.html')

@app.route("/staff/receive-online-order", methods=['GET'])
@role_required(['nhanVien'])
def receive_online_order():
    return render_template("/staff/receive_online_order.html")

@app.route('/staff/receive-online-order/find_order', methods=['POST'])
@role_required(['nhanVien'])
def receive_online_get_order():
    data = request.get_json()
    order_id = data.get("order_id")
    order = dao.get_order_by_id(order_id)
    if order:
        return jsonify({'success': True, 'order': {
            'first_name': order.customer.first_name,
            'last_name': order.customer.last_name,
            'total_price': dao.get_total_price(order),
            'phone_number': order.customer.phone_number,
            'order_status': order.order_status.value
            }
        })
    return jsonify({'success': False, 'message': "order not found"} )
if __name__ == '__main__':
    from app.admin import *

    app.run(debug=True)

import random
from datetime import datetime, timedelta

from app import app, login_manager, dao, OrderStatus, redis_client
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from redis_tasks import redis_utils


@app.context_processor
def inject_cart_quantity():
    if current_user.is_authenticated:
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
            return redirect(url_for('home'))
        else:
            err_msg = "Something wrong!!!"

    return render_template("login.html", err_msg=err_msg)


@app.route("/logout")
@login_required
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
def cart():
    if current_user.is_authenticated:
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
    return redirect(url_for('login'))

@app.route('/delete/cart/<int:cart_id>', methods=['DELETE'])
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


@login_required
@app.route('/update-cart', methods=['PATCH'])
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
def checkout():
    if current_user.is_authenticated:
        carts = dao.get_cart_by_user_id(current_user.id)
        if carts is None:
            return redirect(url_for('not_found_page'))
        total_price = 0
        if carts:
            total_price = dao.get_total_price(carts)
        return render_template('checkout_templates/checkout.html', carts=carts, total_price=total_price)
    return redirect(url_for('login'))


def checkout_method(method, ttl):
    if current_user.is_authenticated:
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
def checkout_offline():
    return checkout_method("offline", 10)


@app.route('/checkout/online', methods=['GET'])
def checkout_online():
    return checkout_method("online", 30)


@app.route('/checkout/confirm', methods=['POST'])
def checkout_confirm():
    if current_user.is_authenticated:
        data = request.get_json()
        order_id = data.get("order_id")
        order = dao.get_order_by_id(order_id, current_user.id)
        if order is None:
            return jsonify({'success': False, 'message': 'order not found'})
        dao.change_status_order(order, order.create_date, OrderStatus.DONE)
        redis_client.delete(order_id)
        return jsonify({'success': True, 'message': 'Checkout done'})
    return jsonify({'success': False, 'message': 'Please login'})


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    from app.admin import *

    app.run(debug=True)

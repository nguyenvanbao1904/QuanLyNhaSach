import random

from app import app, login_manager, dao
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user

@app.route('/')
def home():
    genre = request.args.get('genre')
    orderby = request.args.get('orderby')
    if genre :
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
    if request.method == 'POST':
        try:
            my_cart = dao.create_cart(current_user.id)
            dic = request.form.to_dict()
            dic['order_id'] = my_cart.id
            print(dic)
            dao.create_order_cart(**dic)
            return jsonify({
                'success': True,
                'message': 'Item added to cart successfully'
            }), 201
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }), 500
    if current_user.is_authenticated:
        my_carts = dao.get_cart(current_user.id)
        total_price = 0
        if my_carts:
            total_price = dao.get_total_price(my_carts)
        return render_template('cart.html', carts=my_carts, total_price=total_price)
    return redirect(url_for('login'))

@app.route('/delete/cart/<int:id>', methods=['DELETE'])
def delete_cart_detail(id):
    try:
        dao.delete_cart_detail(id, current_user.id)
        return '',204
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

@app.route('/products/<int:id>', methods=['GET'])
def products_detail(id):
    book = dao.get_book_detail(id)
    if book:
        return render_template('products_detail.html', book=book)
    else:
        return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == '__main__':
    from app.admin import *
    app.run(debug=True)
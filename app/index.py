import random

from app import app, login_manager, dao
from flask import render_template, redirect, url_for, request, session
from flask_login import login_user, login_required, logout_user

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

@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == '__main__':
    from app.admin import *
    app.run(debug=True)
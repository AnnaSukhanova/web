import os
import flask_login
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.utils import redirect
from data.registration import RegisterForm
from data.users import User
from data.login import LoginForm
from data.change_pf import ProfileForm
from data.product import Product
from data.category import Category
from data.cart import Cart
from data.carts_product import CartsProduct

from data.pay import PayForm
from data import db_session
import data

db_session.global_init("blogs.db")
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "yandex_lyceum"
# сумма покупки
summ = 0


# начальная страница
@app.route('/')
def base():
    return render_template('main.html', title='Главная страница')


# функция для получения пользователя, украшенная декоратором
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# обработчик адреса
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация', form=form, message="Неверный пароль")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.id == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        data.create_user(id=form.email.data,
                         name=form.name.data,
                         status=0,
                         password=form.password.data)
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Профиль')


# изменение профиля
@app.route('/change_pf', methods=['GET', 'POST'])
@login_required
def change_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('change_pf.html', title='Изменение профиля', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.id == form.email.data).first():
            if form.email.data == flask_login.current_user.id:
                pass
            else:
                return render_template('change_pf.html', title='Изменение профиля', form=form,
                                       message="Такой пользователь уже есть")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
        user.id = form.email.data
        user.set_password(form.password.data)
        user.Name = form.name.data
        db_sess.commit()
        login_user(user, remember=False)
        return redirect('/profile')
    return render_template('change_pf.html', title='Изменение профиля', form=form)


@login_required
@app.route('/delete_profile', methods=['GET', 'POST'])
def delete_profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
    Id = db_sess.query(Cart.Id).filter(Cart.Owner == flask_login.current_user.id).first()
    car_t = db_sess.query(Cart).filter(Cart.Owner == flask_login.current_user.id).first()
    prd = db_sess.query(CartsProduct).filter(CartsProduct.OwnerCart == Id[0]).all()
    for i in prd:
        db_sess.delete(i)
    db_sess.delete(car_t)
    db_sess.delete(user)
    db_sess.commit()
    return redirect('/')


# страница с футболками
@app.route('/t-shirts', methods=['GET', 'POST'])
def cat1():
    db_sess = db_session.create_session()
    if request.method == 'POST':
        # проверка авторизирован ли пользователь
        if flask_login.current_user.is_anonymous:
            return redirect('/registration')
        elif not flask_login.current_user.is_anonymous:
            user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
            data.add_to_cart(user, int(request.form['add']))
    ID = db_sess.query(Category.Id).filter(Category.Name == 'Футболки').first()[0]
    products = db_sess.query(Product.Name, Product.Price, Product.ImageId, Product.Id,
                             Product.Count).filter(Product.Category == int(ID)).all()
    return render_template('t-shirts.html', title='Футболки', products=products)


# страница с худи
@app.route('/hoodies', methods=['GET', 'POST'])
def cat2():
    db_sess = db_session.create_session()
    if request.method == 'POST':
        if flask_login.current_user.is_anonymous:
            return redirect('/registration')
        elif not flask_login.current_user.is_anonymous:
            user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
            data.add_to_cart(user, int(request.form['add']))
    ID = db_sess.query(Category.Id).filter(Category.Name == 'Худи').first()[0]
    products = db_sess.query(Product.Name, Product.Price, Product.ImageId, Product.Id,
                             Product.Count).filter(Product.Category == int(ID)).all()
    return render_template('hoodies.html', title='Худи', products=products)


# страница с описанием продукта
@app.route('/t-shirts/<int:prod>', methods=['GET', 'POST'])
def prod(prod):
    db_sess = db_session.create_session()
    ID = int(str(request.url).split('/')[-1])
    if request.form.get("add"):
        if flask_login.current_user.is_anonymous:
            return redirect('/registration')
        elif not flask_login.current_user.is_anonymous:
            user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
            data.add_to_cart(user, ID)
    res = db_sess.query(Product.Name, Product.Price, Product.Description, Product.ImageId,
                        Product.Count).filter(Product.Id == ID).all()[0]
    return render_template('product.html', title=res[0], product=res, Cate='t-shirts')


# страница с описанием продукта
@app.route('/hoodies/<int:prod>', methods=['GET', 'POST'])
def prod2(prod):
    db_sess = db_session.create_session()
    # получаем номер товара
    ID = int(str(request.url).split('/')[-1])
    if request.form.get("add"):
        if flask_login.current_user.is_anonymous:
            return redirect('/registration')
        elif not flask_login.current_user.is_anonymous:
            user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
            data.add_to_cart(user, ID)
    res = db_sess.query(Product.Name, Product.Price, Product.Description, Product.ImageId,
                        Product.Count).filter(Product.Id == ID).all()[0]
    return render_template('product.html', title=res[0], product=res, Cate='hoodies')


# корзина
@app.route('/cart')
def cart():
    global summ
    summ = 0
    db_sess = db_session.create_session()
    if flask_login.current_user.is_anonymous:
        return redirect('/registration')
    elif not flask_login.current_user.is_anonymous:
        res = db_sess.query(Cart.Id).filter(Cart.Owner == flask_login.current_user.id).first()
        prodcts = db_sess.query(CartsProduct.ProductId, CartsProduct.Id).filter(CartsProduct.OwnerCart == res[0]).all()
        products = []
        for prd in prodcts:
            product = db_sess.query(Product).filter(Product.Id == prd[0]).first()
            price = db_sess.query(Product.Price).filter(Product.Id == prd[0]).first()
            summ += price[0]
            ID = prd[1]
            products.append([product, ID])
        return render_template('cart.html', title='Коризна', products=products, summ=summ)


# удаление продукта в корзине
@app.route('/delete/<product>')
def delete_c_p(product):
    global summ
    db_sess = db_session.create_session()
    res = db_sess.query(CartsProduct).filter(CartsProduct.Id == product).first()
    db_sess.delete(res)
    db_sess.commit()
    summ = 0
    return redirect('/cart')


@app.route('/pay', methods=['GET', 'POST'])
def payment():
    global summ
    form = PayForm()
    if request.method == 'POST':
        db_sess = db_session.create_session()
        owner = db_sess.query(Cart.Id).filter(Cart.Owner == flask_login.current_user.id).first()
        res = db_sess.query(CartsProduct).filter(CartsProduct.OwnerCart == owner[0]).all()
        for product in res:
            db_sess.delete(product)
            db_sess.commit()
        summ = 0
        return redirect('/success')
    return render_template('pay.html', title='Оплата', form=form, summ=summ)


@app.route('/success')
def success():
    return render_template('success.html', title='Успешно')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

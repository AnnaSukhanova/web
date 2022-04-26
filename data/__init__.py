from data.users import User
from data import db_session
from data.product import Product
from data.cart import Cart
from data.carts_product import CartsProduct


# файл с созданем и сохранением данных
# создавала пользователя
def create_user(id, name, password, status):
    db_sess = db_session.create_session()
    user = User(id=id, Name=name, Status=status)
    user.set_password(password)
    create_cart(user, db_sess)
    db_sess.add(user)
    db_sess.commit()


# создавала корзину


def create_cart(user, db_sess):
    cart = Cart(Owner=user.id)
    db_sess.add(cart)
    db_sess.commit()


# функция для добавления продукта в корзину
def add_to_cart(user, product):
    db_sess = db_session.create_session()
    if isinstance(user, User):
        cartId = db_sess.query(Cart.Id).filter(Cart.Owner == user.id).first()[0]
    elif isinstance(user, int):
        cartId = db_sess.query(Cart.Id).filter(Cart.Owner == user).first()[0]
    else:
        raise Exception("Недопустимый класс")
    if isinstance(product, Product):
        product = product
    elif isinstance(product, int):
        product = db_sess.query(Product).filter(Product.Id == product).first()
    else:
        raise Exception("Недопустимый класс")
    cartproduct = CartsProduct(OwnerCart=cartId,
                               ProductId=product.Id,
                               Status=0,
                               RealTimePrice=product.Price)
    db_sess.add(cartproduct)
    db_sess.commit()


# функция для покупки продукта
def buy_product(user_or_cart):
    db_sess = db_session.create_session()
    if isinstance(user_or_cart, User):
        cart = db_sess.query(Cart).filter(Cart.Owner == user_or_cart.Id).first()
    elif isinstance(user_or_cart, Cart):
        cart = user_or_cart
    else:
        raise Exception("Недопустимый класс")
    all_prod = db_sess.query(CartsProduct).filter(CartsProduct.Status == 0,
                                                  CartsProduct.OwnerCart == cart.Id)
    return all_prod


if __name__ == '__main__':
    pass

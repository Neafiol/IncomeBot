from flask import Flask, send_from_directory, request, render_template, redirect

from models import Shops, Items, Adress, Users, Order

app = Flask(__name__)


@app.route('/')
def root():
    shops = Shops.select()
    return render_template('index.html', shops=shops)


@app.route('/cmd', methods=['POST'])
def com():
    c = request.form.to_dict()
    comand = c["cmd"]
    del c["cmd"]
    print(c)

    if comand == "send_mes":
        print("sent_message: " + c["message"])

    elif comand == "new_shop":
        Shops.create(**c)
        return "Магазин добавлен"

    elif comand == "new_item":
        c["cost"] = "100"
        c["buycost"] = "50"
        Items.create(**c)
        return "Товар добавлен"

    elif comand == "new_adress":
        Adress.create(**c)
        return "Адресс добавлен"

    elif comand == "upload_shop":
        Shops.update(c).where(Shops.id == c["id"]).execute()
        return "Магазин обновлен"

    elif comand == "upload_user":
        Users.update(c).where(Users.id == c["id"]).execute()
        return "Пользователь обновлен"

    elif comand == "update_order":
        if(c["status"]=="del"):
            Order.delete_by_id(c["id"])
        else:
            o = Order.get_by_id(c["id"])
            o.status=c["status"]
            o.save()

        return "Статус заказа обновлен"

    elif comand == "delete_user":
        Users.delete_by_id(c["id"])
        return redirect("/users")

    return "OK"


@app.route('/shops')
def shops():
    shops = Shops.select().order_by(Shops.id).execute()

    return render_template('shops.html', shops=shops)


@app.route('/items/<int:id>')
def items(id=0):
    print(id)
    items = Items.select().where(Items.shopid == id).execute()
    shops = Shops.select().execute()

    return render_template('items.html', items=items, shops=shops)


@app.route('/users')
def quizs():
    users = Users.select().execute()
    return render_template('users.html', users=users)\

@app.route('/orders')
def orders():
    orders = Order.select().execute()
    return render_template('orders.html', orders=orders)


@app.route('/', methods=['POST'])
def upload_view():
    file = request.files['TEST']
    print(file)
    # file.save('ff.txt')
    pass


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9000, debug=False)

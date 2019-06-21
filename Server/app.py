import os

import telebot
from flask import Flask, send_from_directory, request, render_template, redirect, make_response

from config import order_status, tel_token, PASS
from models import Shops, Items, Adress, Users, Order, Comment

app = Flask(__name__)
bot = telebot.TeleBot(tel_token)


def pass_check(function_to_decorate):
    def wrapper(*args, **kwargs):
        p = request.cookies.get('PASS')
        if p == PASS:
            return function_to_decorate(*args, **kwargs)
        else:
            return redirect("/login")

    wrapper.__name__ = function_to_decorate.__name__
    return wrapper


@app.route('/login')
def login():
    if request.method == 'GET':
        p = request.args.get('pas')
        if p == PASS:
            resp = make_response(redirect('/'))
            resp.set_cookie('PASS', p)
            return resp

        return render_template("login.html")


@app.route('/')
@pass_check
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
        users = Users.select()
        for u in users:
            bot.send_message(u.tel_id,
                             c["message"],
                             parse_mode="Markdown")
        print(f"Отправлено {len(users)} cообщений")

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
        if (c["status"] == "del"):
            Order.delete_by_id(c["id"])
        else:
            o = Order.get_by_id(c["id"])
            u = Users.get_by_id(o.userid)
            try:
                bot.send_message(u.tel_id,
                                 f"Статус заказа {o.name} обновлен: _{order_status[int(c['status'])]}_",
                                 parse_mode="Markdown")
            except:
                pass
            o.status = int(c["status"])
            o.save()

        return "Статус заказа обновлен"

    elif comand == "delete_user":
        Users.delete_by_id(c["id"])
        return redirect("/users")

    return "OK"


@app.route('/shops')
@pass_check
def shops():
    shops = Shops.select().order_by(Shops.id).execute()

    return render_template('shops.html', shops=shops)


@app.route('/items/<int:id>')
@pass_check
def items(id=0):
    print(id)
    items = Items.select().where(Items.shopid == id).execute()
    shops = Shops.select().execute()

    return render_template('items.html', items=items, shops=shops)


@app.route('/users')
@pass_check
def quizs():
    users = Users.select().execute()
    return render_template('users.html', users=users)


@app.route('/coments')
@pass_check
def coments():
    coments = Comment.select().execute()
    return render_template('coments.html', coments=coments)


@app.route('/orders/<type>')
@pass_check
def orders(type):
    if type == "all":
        orders = Order.select().execute()
    elif type == "active":
        orders = Order.select().where(Order.id << [0, 2]).execute()
    elif type == "way":
        orders = Order.select().where(Order.id << [1, 4]).execute()
    elif type == "drop":
        orders = Order.select().where(Order.id == 3).execute()
    elif type == "payed":
        orders = Order.select().where(Order.id == 6).execute()
    elif type == "received":
        orders = Order.select().where(Order.id == 5).execute()
    elif type == "cancle":
        orders = Order.select().where(Order.id == 7).execute()
    elif type == "close":
        orders = Order.select().where(Order.id == 8).execute()
    else:
        return "Тип сортировки не указан"

    return render_template('orders.html', orders=orders, order_status=order_status)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


if __name__ == '__main__':

    if 'DYNO' in os.environ:
        DEBUG = False
    else:
        DEBUG = True
    port = os.environ.get('PORT', 5000)
    '''
    Запуск возможен в 2ух режимах,
    при запуске на продакшен используется waitress
    '''
    if DEBUG:
        app.run('127.0.0.1', port, debug=True)
    else:
        app.run('0.0.0.0', port, debug=False)
        # serve(app, host='0.0.0.0', port=port)

# -*- coding: utf-8 -*-
import json
import sys
from datetime import datetime

import requests

sys.path.append('../')
from models import *
import telebot
from telebot import types
from Bot.TextConstants import *



import logging

# add filemode="w" to overwrite
logging.basicConfig(filename="sample.log", level=logging.INFO)



#BOT CODE

bot = telebot.TeleBot(tel_token)
base_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
base_keyboard1 = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

base_button_1 = types.KeyboardButton(text=BTN_1_TEXT)
base_button_2 = types.KeyboardButton(text=BTN_2_TEXT)
base_button_3 = types.KeyboardButton(text=BTN_3_TEXT)
base_button_4 = types.KeyboardButton(text=BTN_4_TEXT)
base_keyboard.row(base_button_1, base_button_2)
base_keyboard.row(base_button_3, base_button_4)

base_button_1 = types.KeyboardButton(text=BTN_11_TEXT)
base_button_2 = types.KeyboardButton(text=BTN_12_TEXT)
base_button_3 = types.KeyboardButton(text=BTN_13_TEXT)
base_button_4 = types.KeyboardButton(text=BTN_14_TEXT)
base_keyboard1.add(base_button_1, base_button_2, base_button_3, base_button_4)


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    u = Users.get(Users.tel_id == message.chat.id)
    if u.dstage == 0:
        bot.send_message(chat_id=message.chat.id,
                         text=I_NOT_RESPONSE)
        return
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)

    downloaded_file = bot.download_file(file_info.file_path)

    files = {'image': downloaded_file}
    headers = {'Authorization': "TOKEN " + IMAGE_BAN_TOKEN}
    r = requests.post("https://api.imageban.ru/v1", headers=headers, files=files)

    url = json.loads(r.content.decode('utf-8'))["data"]["link"]
    print("Upload photo", url)

    if u.dstage == 8:
        order = Order.get_by_id(u.active_order)
        order.other_data["photo_2"] = url
        order.status = 0
        order.save()
        u.dstage = 0
        bot.send_message(chat_id=message.chat.id,
                         text=INFO_UPLOAD)
    elif u.dstage == 6:
        order = Order.get_by_id(u.active_order)
        order.other_data["photo_1"] = url
        order.status = 2
        order.save()
        u.dstage = 0
        bot.send_message(chat_id=message.chat.id,
                         text=INFO_UPLOAD)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Фото не ожидалось")


# Comand for enter in bot
@bot.message_handler(commands=[PASS_TG])
def repeat_all_messages(message):
    u = Users.get(Users.tel_id == message.chat.id)
    u.level = 1
    u.save()
    bot.send_message(message.chat.id, HELLO_TEXT, reply_markup=base_keyboard)


# Start Fanction
@bot.message_handler(commands=['start'])
def repeat_all_messages(message):  # Название функции не играет никакой роли, в принципе

    u = Users.get_or_none(Users.tel_id == message.chat.id)
    if u == None:
        Users.create(tel_id=message.chat.id, name=str(message.from_user.last_name),
                     nicname="Anonim", level=0)

        bot.send_message(message.chat.id, FIRST_TEXT)
    else:
        print(u.tel_id)
        bot.send_message(message.chat.id, YOU_THERE_TEXT, reply_markup=base_keyboard)


@bot.callback_query_handler(func=lambda call: True)
def repeat_all_messages(call):
    if call.from_user:
        cal = str(call.data)
        try:
            print(cal)
            if (cal.find("country") >= 0):
                country = cal.split("_")[1]
                level = Users.get(Users.tel_id == call.message.chat.id).level
                markup = types.InlineKeyboardMarkup(row_width=1)
                buttons = []

                shops = Shops.select().where(Shops.country == country and Shops.minlevel <= level).execute()

                for s in shops:
                    buttons.append(types.InlineKeyboardButton(text=s.name, callback_data="shop_" + str(s.id)))
                markup.add(*buttons)

                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=SHOP_CHOICE,
                                      reply_markup=markup
                                      )

            elif (cal.find("shop") >= 0):
                shop = cal.split("_")[1]
                markup = types.InlineKeyboardMarkup(row_width=1)
                buttons = []

                items = Items.select().where(Items.shopid == int(shop)).execute()

                for i in items:
                    buttons.append(types.InlineKeyboardButton(text=i.name, callback_data="item_" + str(i.id)))
                markup.add(*buttons)

                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=FAVOURITE_ITEM,
                                      reply_markup=markup)

            elif (cal.find("item") >= 0):
                item = int(cal.split("_")[1])
                markup = types.InlineKeyboardMarkup(row_width=2)

                item = Items.get(Items.id == item)

                markup.add(types.InlineKeyboardButton(text=CANSLE, callback_data="drop" + str(item.id)))
                markup.add(types.InlineKeyboardButton(text=BOUGTH, callback_data="buy_" + str(item.id)))
                markup.add(types.InlineKeyboardButton(text="Открыть сайт", url=str(item.url)))

                bot.send_message(chat_id=call.message.chat.id,
                                 text="Вы выбрали *" + item.name + "*\nПожалуйста, проставте статус товару после завершения покупки",
                                 reply_markup=markup,
                                 parse_mode="Markdown")

            elif (cal.find("neworder") >= 0):
                u = Users.get(Users.tel_id == call.message.chat.id)
                o = Order(url="", data=datetime.now(), status=-1, userid=u.id, name="")
                o.save()
                u.dstage = 3
                u.active_order = o.id
                u.save()

                bot.send_message(chat_id=call.message.chat.id,
                                 text=ITEM_NAME,
                                 parse_mode="Markdown")

            elif (cal.find("buy") >= 0):
                item_id = int(cal.split("_")[1])
                u = Users.get(Users.tel_id == call.message.chat.id)
                item = Items.get_by_id(item_id)
                Order.create(url=item.url, data=datetime.now(), userid=u.id, name=item.name)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=NEW_UPLOAD,
                                      parse_mode="Markdown")

            elif cal.find("orderstatus") >= 0:
                order = int(cal.split("_")[2])
                cmd = cal.split("_")[1]
                order = Order.get_by_id(order)
                u = Users.get(Users.tel_id == call.message.chat.id)

                if cmd == "drop":
                    order.status = 7
                    bot.delete_message(chat_id=call.message.chat.id,
                                       message_id=call.message.message_id)
                    bot.send_message(chat_id=call.message.chat.id,
                                     text="Очень жаль!")
                    return

                u.active_order = order
                if cmd == "toes":
                    order.status = 2
                    u.dstage = 9
                    text = "Пришлите данные для доступа к дропу"

                elif cmd == "todrop":
                    order.status = 2
                    u.dstage = 8
                    text = "Пришлите скрин подтверждения доставки"

                elif cmd == "torus":
                    u.dstage = 8
                    order.status = 3
                    text = "Пришлите скрин подтверждения доставки"

                order.save()
                u.save()

                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Заказ на *" + order.name + "*\n" + text,
                                      parse_mode="Markdown")

            elif cal.find("getorders") >= 0:

                markup = types.InlineKeyboardMarkup(row_width=1)
                buttons = []
                u = Users.get(Users.tel_id == call.message.chat.id)
                orders = Order.select().where(Order.userid == u.id and Order.status >= 0 and Order.status < 5).execute()

                for o in orders:
                    buttons.append(types.InlineKeyboardButton(text=o.name, callback_data="order_" + str(o.id)))
                markup.add(*buttons)

                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=YOUR_ORDER,
                                      reply_markup=markup)



            elif (cal.find("order") >= 0):
                print(cal)
                order = int(cal.split("_")[1])
                markup = types.InlineKeyboardMarkup(row_width=2)
                order = Order.get(Order.id == order)

                markup.add(types.InlineKeyboardButton(text=COME_AWAY,
                                                      callback_data="orderstatus_drop_" + str(order.id)))

                if order.status == 1:  # oreder is active

                    markup.add(
                        types.InlineKeyboardButton(text=COME_TO_DROP,
                                                   callback_data="orderstatus_toes_" + str(order.id)))
                    markup.add(types.InlineKeyboardButton(text=COME_RESEND,
                                                          callback_data="orderstatus_todrop_" + str(order.id)))
                    markup.add(
                        types.InlineKeyboardButton(text=COME_TO_RUS,
                                                   callback_data="orderstatus_torus_" + str(order.id)))

                bot.send_message(chat_id=call.message.chat.id,
                                 text="Заказ *" + order.name + "*\nСтатус: _" + order_status[
                                     order.status] + "_\nВыбирете ноывй статус заказа",
                                 reply_markup=markup,
                                 parse_mode="Markdown")

            elif (cal.find("drop") >= 0):
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id)
        except:
            bot.send_message(chat_id=call.message.chat.id,
                             text=ERROR_TEXT,
                             parse_mode="Markdown")

        return True


@bot.message_handler(content_types=["text"])
# обработка ответа от участника
def repeat_all_messages(message):
    if message.text == BTN_1_TEXT:
        bot.send_message(message.chat.id, O_SERVICE_TEXT, reply_markup=base_keyboard1)

    elif message.text == BTN_11_TEXT:
        bot.send_message(message.chat.id, RULE_TEXT, parse_mode="Markdown")

    elif message.text == BTN_12_TEXT:
        text = "*Топ участников, набравших больше всего балов:*\n\n"
        users = Users.select().order_by(Users.balls.desc()).limit(20).execute()

        for i, u in enumerate(users):
            spase = 45 - len(str(u.balls)) - len(str(u.nicname)) - len(str(i))
            text += "*" + str(i + 1) + "*. " + str(u.nicname) + " " * spase + "_" + str(u.balls) + "_\n"

        bot.send_message(chat_id=message.chat.id,
                         text=text, parse_mode="Markdown")

    elif message.text == BTN_13_TEXT:
        Users.update({Users.dstage: 11}).where(Users.tel_id == message.chat.id).execute()
        bot.send_message(message.chat.id, "Пришлите ваш отзыв")

    elif message.text == BTN_14_TEXT:
        bot.send_message(message.chat.id, "Выбери действие", reply_markup=base_keyboard)

    elif (message.text == BTN_3_TEXT):
        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = []
        for c in COUNTRIES:
            buttons.append(types.InlineKeyboardButton(text=c, callback_data="country_" + COUNTRIES[c]))
        markup.add(*buttons)
        u = Users.get_or_none(Users.tel_id == message.chat.id)
        u.dstage = message.message_id + 1
        u.save()
        bot.send_message(message.chat.id, "Выберете страну", reply_markup=markup)

    elif (message.text == BTN_2_TEXT):
        u = Users.get(Users.tel_id == message.chat.id)
        n = Order.select().where(Order.userid == u.id).count()

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        base_button_1 = types.InlineKeyboardButton(text="Мои заказы ", callback_data="getorders")
        base_button_2 = types.InlineKeyboardButton(text="Добавить товар", callback_data="neworder")
        keyboard.add(base_button_1, base_button_2)
        bot.send_message(chat_id=message.chat.id,
                         text="На данный момент у вас " + str(n) + " активных заказов",
                         reply_markup=keyboard)

    elif message.text == BTN_4_TEXT:
        text = "*Доступные Вам адреса:*\n\n"
        u = Users.get(Users.tel_id == message.chat.id)
        adreses = Adress.select().where(Adress.minlevel <= u.level).execute()

        for i, a in enumerate(adreses):
            text += "*" + str(i + 1) + "*. " + a.name + ":  _" + a.adress + "_\n\n"

        bot.send_message(chat_id=message.chat.id,
                         text=text, parse_mode="Markdown")




    else:
        u = Users.get(Users.tel_id == message.chat.id)
        if u.dstage == 11:
            pass
            Comment.create(autor=u.name, text=message.text)
            bot.send_message(chat_id=message.chat.id,
                             text="Отзыв добавлен")
            u.dstage = 0
            u.save()
            return

        if u.dstage == 0:
            bot.send_message(chat_id=message.chat.id,
                             text="Я не отвечаю на сообщения")

        order = Order.get_by_id(u.active_order)
        if u.dstage == 9:
            order.other_data["dropinfo_1"] = message.text
            u.dstage = 0
            bot.send_message(chat_id=message.chat.id,
                             text=WAIT_MODERATOR)
        elif u.dstage == 3:
            order.name = message.text
            u.dstage = 4
            bot.send_message(chat_id=message.chat.id,
                             text=SEND_ORDER_URL)
        elif u.dstage == 4:
            order.name = message.text
            u.dstage = 5
            bot.send_message(chat_id=message.chat.id,
                             text=SEND_ORDER_COMMENT)
        elif u.dstage == 5:
            order.url = message.text
            u.dstage = 6
            bot.send_message(chat_id=message.chat.id,
                             text="Пришлите скриншот с ордером")


        u.save()
        order.save()

    print(str(message.from_user.last_name) + ' : ' + message.text)


def run(debag=True):
    while True:
        try:
            print("Income bot start")
            bot.polling(none_stop=True)
        except:
            print("Error")
            if (debag):
                exit(0)


# Main Fanction
if __name__ == '__main__':
    run(True)

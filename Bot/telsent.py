# -*- coding: utf-8 -*-
import sys
from datetime import datetime

from Bot.TextConstants import *

sys.path.append('../')

from models import *

import telebot
from telebot import types
from TextConstants import *


def log(txt):
    print(txt)


bot = telebot.TeleBot(tel_token)
base_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

base_button_1 = types.KeyboardButton(text=BTN_1_TEXT)
base_button_2 = types.KeyboardButton(text=BTN_2_TEXT)
base_button_3 = types.KeyboardButton(text=BTN_3_TEXT)
base_keyboard.row(base_button_1, base_button_2, base_button_3)


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    u = Users.get(Users.tel_id == message.chat.id)
    if u.dstage == 0:
        bot.send_message(chat_id=message.chat.id,
                         text=I_NOT_RESPONSE)
        return
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)

    downloaded_file = bot.download_file(file_info.file_path)
    path = "../res/photos/"
    photo_name = str(message.chat.id) + "_" + str(message.message_id) + '.jpg'

    out = open(path + photo_name, "wb")
    out.write(downloaded_file)
    out.close()

    if u.dstage == 2:
        order = Order.get_by_id(u.active_order)
        order.other_data["Photo Data"] = photo_name
        order.save()
        u.dstage = 0
        bot.send_message(chat_id=message.chat.id,
                         text=INFO_UPLOAD)
    if u.dstage == 5:
        order = Order.get_by_id(u.active_order)
        order.other_data["Order Photo"] = photo_name
        order.status = 1
        order.save()
        u.dstage = 0
        bot.send_message(chat_id=message.chat.id,
                         text=INFO_UPLOAD)


# Comand for enter in bot
@bot.message_handler(commands=['enter'])
def repeat_all_messages(message):
    u = Users.get(Users.tel_id == message.chat.id)
    u.level = 0
    u.save()
    bot.send_message(message.chat.id, HELLO_TEXT, reply_markup=base_keyboard)


# Start Fanction
@bot.message_handler(commands=['start'])
def repeat_all_messages(message):  # Название функции не играет никакой роли, в принципе

    u = Users.get_or_none(Users.tel_id == message.chat.id)
    if u == None:
        Users.create(tel_id=message.chat.id, name=str(message.from_user.last_name), level=-1)
        bot.send_message(message.chat.id, FIRST_TEXT)
    else:
        print(u.tel_id)
        bot.send_message(message.chat.id, YOU_THERE_TEXT, reply_markup=base_keyboard)


@bot.callback_query_handler(func=lambda call: True)
def repeat_all_messages(call):
    if call.from_user:
        cal = str(call.data)
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
            u = Users.get(Users.tel_id==call.message.chat.id)
            o = Order(url="",data=datetime.now(),userid=u.id,name="")
            o.save()
            u.dstage = 3
            u.active_order = o.id
            u.save()

            bot.send_message(chat_id=call.message.chat.id,
                             text=ITEM_NAME,
                             parse_mode="Markdown")

        elif cal.find("orderstatus") >= 0:
            order = int(cal.split("_")[2])
            cmd = cal.split("_")[1]
            order = Order.get_by_id(order)
            u = Users.get(Users.tel_id == call.message.chat.id)

            if cmd == "drop":
                order.status = -1
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id)
                bot.send_message(chat_id=call.message.chat.id,
                                 text="Очень жаль!")
                return

            u.active_order = order
            if cmd == "toes":
                order.status = 1
                u.dstage = 1
                text = "Пришлите данные для доступа к дропу"

            elif cmd == "todrop":
                order.status = 2
                u.dstage = 2
                text = "Пришлите скрин подтверждения доставки"

            elif cmd == "torus":
                u.dstage = 2
                order.status = 3
                text = "Пришлите скрин подтверждения доставки"

            order.save()
            u.save()

            bot.send_message(chat_id=call.message.chat.id,
                             text=text,
                             parse_mode="Markdown")

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="_Заказ Обробатывается_",
                                  reply_markup=None,
                                  parse_mode="Markdown")

        elif (cal.find("getorders") >= 0):

            markup = types.InlineKeyboardMarkup(row_width=1)
            buttons = []
            u = Users.get(Users.tel_id == call.message.chat.id)
            orders = Order.select().where(Order.userid == u.id and Order.status>=0).execute()

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
            markup.add(
                types.InlineKeyboardButton(text=COME_TO_DROP, callback_data="orderstatus_toes_" + str(order.id)))
            markup.add(types.InlineKeyboardButton(text=COME_RESEND,
                                                  callback_data="orderstatus_todrop_" + str(order.id)))
            markup.add(
                types.InlineKeyboardButton(text=COME_TO_RUS, callback_data="orderstatus_torus_" + str(order.id)))

            bot.send_message(chat_id=call.message.chat.id,
                             text="Заказ на *" + order.name + "*\nПожалуйста, проставте статус товару после завершения покупки",
                             reply_markup=markup,
                             parse_mode="Markdown")

        elif (cal.find("drop") >= 0):
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)

        return True


@bot.message_handler(content_types=["text"])
# обработка ответа от участника
def repeat_all_messages(message):
    if message.text == BTN_1_TEXT:
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        buttons.append(types.InlineKeyboardButton(text="Хочу присоеденитьмся", callback_data="wantadd"))
        markup.add(*buttons)

        bot.send_message(message.chat.id, RULE_TEXT, reply_markup=markup)

    if (message.text == BTN_3_TEXT):
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

    else:
        u = Users.get(Users.tel_id == message.chat.id)
        order = Order.get_by_id(u.active_order)


        if u.dstage == 0:
            bot.send_message(chat_id=message.chat.id,
                             text="Я не отвечаю на сообщения")

        if u.dstage == 1:
            order.other_data["Drop Data"] = message.text
            u.dstage = 0
            bot.send_message(chat_id=message.chat.id,
                             text="Информация обновлена, дождитесь проверки модератором 👤")
        elif u.dstage == 3:
            order.name = message.text
            u.dstage = 4
            bot.send_message(chat_id=message.chat.id,
                             text="Пришлите ссылку на товар")
        elif u.dstage == 4:
            order.url = message.text
            u.dstage = 5
            bot.send_message(chat_id=message.chat.id,
                             text="Пришлите скриншот с ордером")
        u.save()
        order.save()

    log(str(message.from_user.last_name) + ' : ' + message.text)


# Main Fanction
if __name__ == '__main__':
    while True:
        try:
            print("start")
            bot.polling(none_stop=True)
        except:
            print("Error")
            exit(0)

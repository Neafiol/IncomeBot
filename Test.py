from datetime import datetime

from models import Shops, Items, Order, Adress

Adress.create(name="Патрик Иванов",adress="Улица генерала Федерова, 17б 120232")
# Shops.select().where(Shops.country=="US" and Shops.minlevel<=0).execute()
# print(len(Shops))
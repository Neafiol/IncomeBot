from datetime import datetime

from models import Shops, Items, Order

Order.create(name="Nike Air",url="amazon.com",userid=1,data=datetime.now())
# Shops.select().where(Shops.country=="US" and Shops.minlevel<=0).execute()
# print(len(Shops))
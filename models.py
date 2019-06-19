
from peewee import *
from config import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField

db = PostgresqlExtDatabase(bdname, user=bduser, password=bdpassword,
                           host=bdhost, port=bdport)
class Users(Model):
    tel_id=IntegerField()
    name = TextField()
    dstage = IntegerField(default=0)
    active_order = IntegerField(default=0)
    level = IntegerField(default=0)

    class Meta:
        database = db
        db_table='Users'



class Shops(Model):
    url=TextField()
    name = TextField()
    country=TextField()
    minlevel=IntegerField(default=0)

    class Meta:
        database = db
        db_table='Shops'

class Items(Model):
    url=TextField()
    name = TextField()
    cost = TextField()
    buycost = IntegerField()
    shopid = IntegerField()
    minlevel = IntegerField(default=0)

    class Meta:
        database = db
        db_table='Items'

class Order(Model):
    url=TextField()
    name = TextField()
    data=DateTimeField()
    status=IntegerField(default=0)
    userid = IntegerField()
    other_data = JSONField(default={})

    class Meta:
        database = db
        db_table='Order'

Order.create_table()
Items.create_table()
Shops.create_table()
Users.create_table()

from peewee import *
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField

from config import *

db = PostgresqlExtDatabase(bdname, user=bduser, password=bdpassword,
                           host=bdhost, port=bdport)


class Users(Model):
    tel_id = IntegerField()
    name = TextField()
    nicname = TextField(null=True)
    balls = IntegerField(default=0)
    dstage = IntegerField(default=0)
    active_order = IntegerField(default=0)
    level = IntegerField(default=0)

    class Meta:
        database = db
        db_table = 'Users'


class Shops(Model):
    url = TextField()
    name = TextField()
    country = TextField()
    minlevel = IntegerField(default=0)

    class Meta:
        database = db
        db_table = 'Shops'


class Adress(Model):
    adress = TextField()
    name = TextField()
    country = TextField(null=True)
    minlevel = IntegerField(default=0)

    class Meta:
        database = db
        db_table = 'Adress'


class Items(Model):
    url = TextField()
    name = TextField()
    cost = TextField()
    buycost = IntegerField()
    shopid = IntegerField()
    minlevel = IntegerField(default=0)

    class Meta:
        database = db
        db_table = 'Items'


class Order(Model):
    url = TextField()
    name = TextField()
    data = DateTimeField()
    status = IntegerField(default=0)
    userid = IntegerField()
    other_data = JSONField(default={
        "photo_1": "",
        "photo_2": "",
        "photo_3": "",
        "dropinfo_1": "",
        "comment": ""
    })

    class Meta:
        database = db
        db_table = 'Order'


class Comment(Model):
    autor = TextField()
    text = TextField()
    verfited = BooleanField(default=False)

    class Meta:
        database = db
        db_table = 'Comment'


# Users.drop_table()
# Comment.drop_table()
# Adress.drop_table()
# Shops.drop_table()
# Order.drop_table()
# Items.drop_table()
#
#
# Order.create_table()
# Items.create_table()
# Shops.create_table()
# Users.create_table()
# Adress.create_table()
# Comment.create_table()

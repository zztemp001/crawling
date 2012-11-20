# coding=utf-8

from scrapy.item import Item, Field

class LocalItem(Item):
    title = Field()
    link = Field()
    body = Field()

class KpOriginItem(Item):
    url = Field()
    body = Field()
    timestamp = Field()

class KpShopItem(Item):
    shopid = Field()
    shopname = Field()
    description = Field()
    recommend = Field()
    latitude = Field()
    longitude = Field()
    commercialzone = Field()

class PlaceItem(Item):
    title = Field()
    parent = Field()
    level = Field()
    timestamp = Field()
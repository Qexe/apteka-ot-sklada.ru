# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
    url = scrapy.Field()
    price_data = scrapy.Field()
    title = scrapy.Field()
    assets = scrapy.Field()
    stock = scrapy.Field()
    metadata = scrapy.Field()
    RPC = scrapy.Field()
    timestamp = scrapy.Field()
    brand = scrapy.Field()
    marketing_tags = scrapy.Field()
    section = scrapy.Field()
    variants = scrapy.Field()

    pass

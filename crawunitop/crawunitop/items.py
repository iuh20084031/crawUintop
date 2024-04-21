# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawunitopItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    coursename = scrapy.Field()
    lecturer = scrapy.Field()
    intro = scrapy.Field()
    describe = scrapy.Field()
    courseUrl = scrapy.Field()
    votenumber = scrapy.Field()
    rating = scrapy.Field()
    newfee = scrapy.Field()
    oldfee = scrapy.Field()
    lessonnum = scrapy.Field()

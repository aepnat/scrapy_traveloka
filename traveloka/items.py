# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class HotelReview(scrapy.Item):
    hotelName = scrapy.Field()
    hotelStar = scrapy.Field()
    hotelAddress = scrapy.Field()
    hotelRating = scrapy.Field()
    reviewRating = scrapy.Field()
    reviewDate = scrapy.Field()
    reviewName = scrapy.Field()
    reviewTheme = scrapy.Field()
    reviewText = scrapy.Field() 

class Hotel(scrapy.Item):
    id = scrapy.Field()
    hotelName = scrapy.Field()
    hotelStar = scrapy.Field()
    hotelArea = scrapy.Field()
    hotelCity = scrapy.Field()
    hotelAddress = scrapy.Field()
    hotelHasRestaurant = scrapy.Field()
    hotelHasMeetingRoom = scrapy.Field()

class TravelokaItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()

# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

class TravelokaSpider(scrapy.Spider):
    name = 'traveloka'
    allowed_domains = ['traveloka.com']
    start_urls = ['traveloka.com']
    chromedriver_path = 'app/chromedriver'

    def __init__(self, chromedriver_path='', **kwargs):
        super(TravelokaSpider, self).__init__(**kwargs)
        if isinstance(self.start_urls, str):
            self.start_urls = self.start_urls.split(',')
        if (chromedriver_path != ''):
            self.chromedriver_path = chromedriver_path

    def parse(self, response):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--lang=id')
        options.add_argument('--disable-gpu')
        if (self.chromedriver_path == 'path'):
            dv = webdriver.Chrome(chrome_options=options)
        else:
            dv = webdriver.Chrome(self.chromedriver_path, chrome_options=options)

        dv.get(response.url)
        wait = WebDriverWait(dv, 20)
        dv.implicitly_wait(7)
        counterPage = 0
        counterHotel = 0

        wait.until(lambda dv: dv.find_elements_by_xpath("//div[@class='mMmI2 CZtP0 tvat-searchListItem']"))
        nextPage = True
        while nextPage:
            # ngambil semua element hotel 1
            hotels = dv.find_elements_by_xpath("//div[@class='mMmI2 CZtP0 tvat-searchListItem']")
            try:
                for hotel in hotels:
                    try:
                        hotelName = hotel.find_element_by_xpath(".//div[@class='_1z5je _10ZQX tvat-hotelName']").text
                    except NoSuchElementException:
                        hotelName = '-'

                    try:
                        hotelStar = hotel.find_element_by_xpath(".//meta[@itemprop='ratingValue']").get_attribute('content')
                    except NoSuchElementException:
                        hotelStar = 0

                    try:
                        hotelTipe = hotel.find_element_by_xpath(".//div[@class='_3ohst Jewfo _2Vswb']").text
                    except NoSuchElementException:
                        hotelTipe = '-'

                    hotel.click()
                    mainwindow = dv.window_handles[0] #tab bawaan browser
                    hotelwindow = dv.window_handles[1] #new tab
                    dv.switch_to_window(hotelwindow)
                    wait.until(lambda dv: dv.find_elements_by_xpath("//link[@rel='canonical']"))
                    wait.until(lambda dv: dv.find_elements_by_xpath("//img[@class='y9Bbb']"))

                    try:
                        hotelFullAddress = dv.find_element_by_xpath("//span[@itemprop='streetAddress']").text
                        # split string address with comma to get area and city
                        hotelSplit = hotelFullAddress.split(', ')
                        AddressExplode = list(reversed(hotelSplit))
                        hotelArea = AddressExplode[4]
                        hotelCity = AddressExplode[2]
                    except NoSuchElementException:
                        hotelFullAddress = '-'

                    try:
                        img_restaurant = 'https://s3-ap-southeast-1.amazonaws.com/traveloka/imageResource/2017/06/07/1496833794378-eb51eee62d46110b712e327108299ea6.png'
                        facilities = dv.find_elements_by_xpath("//img[@class='y9Bbb']")
                        for facility in facilities:
                            img_facility = facility.get_attribute('src')
                            if (img_restaurant == img_facility):
                                has_restaurant = 'yes'
                                break
                    except NoSuchElementException:
                        has_restaurant = 'no'
                    
                    try:
                        hotelLink = dv.find_element_by_xpath("//link[@rel='canonical']").get_attribute('href')
                        hotelLink = list(reversed(hotelLink.split('/')))
                        hotelId = hotelLink[0]
                    except NoSuchElementException:
                        hotelId = 0

                    item = {}
                    item['id'] = hotelId
                    item['name'] = hotelName
                    item['start'] = hotelStar
                    item['address'] = hotelFullAddress
                    item['area'] = hotelArea
                    item['city'] = hotelCity
                    item['tipe'] = hotelTipe
                    item['has_restaurant'] = has_restaurant
                    item['has_meeting_room'] = 'no'
                    yield item
                    counterHotel += 1

                    dv.close()
                    dv.switch_to_window(mainwindow)

                counterPage += 1
                nextButton = dv.find_element_by_xpath("//div[@id='next-button']")
                dv.execute_script('arguments[0].click();', nextButton)
                wait.until(lambda dv: dv.find_elements_by_xpath("//div[@class='mMmI2 CZtP0 tvat-searchListItem']"))

            except Exception as e:
                print("Page ", counterPage)
                print("Hotel ", counterHotel)
                print("Error next button", e)
                nextPage = False
        dv.quit()
        del dv
        
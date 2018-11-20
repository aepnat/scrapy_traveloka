import scrapy
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from traveloka.items import Hotel
from traveloka.items import TravelokaItem

class TravelokaHotelSpider(scrapy.Spider):
    name = 'traveloka_hotel'
    allowed_domains = ['traveloka.com']
    start_urls = ['https://www.traveloka.com/id-id/hotel/search?spec=20-11-2018.21-11-2018.1.1.HOTEL_GEO.102813.Jakarta.2']

    def parse(self, response):
        print('===================================== start get hotel list data ======================================') 
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--lang=id')
        options.add_argument('--disable-gpu')
        dv = webdriver.Chrome(chrome_options=options)
        dv.get(response.url)
        wait = WebDriverWait(dv, 20)
        dv.implicitly_wait(7)
        hotels = []
        counter = 0

        wait.until(lambda dv: dv.find_elements_by_xpath("//div[@class='mMmI2 CZtP0 tvat-searchListItem']"))
        nextPage = True
        while nextPage:
            #ngambil semua element hotel 1
            hotels = dv.find_elements_by_xpath("//div[@class='mMmI2 CZtP0 tvat-searchListItem']")
            try:
                for hotel in hotels:
                    hotel.click()
                    mainwindow = dv.window_handles[0] #tab bawaan browser
                    hotelwindow = dv.window_handles[1] #new tab
                    dv.switch_to_window(hotelwindow)
                    wait.until(lambda dv: dv.find_elements_by_xpath("//link[@rel='canonical']"))
                    wait.until(lambda dv: dv.find_elements_by_xpath("//meta[@itemprop='ratingValue']"))
                    wait.until(lambda dv: dv.find_elements_by_xpath("//img[@class='y9Bbb']"))

                    print('===================================== start hotel ======================================') 
                    print('========================')
                    print(counter)
                    hotelName = dv.find_element_by_xpath("//h1[@itemprop='name']").text

                    hotelStarElemen = dv.find_elements_by_xpath("//meta[@itemprop='ratingValue']")
                    if (len(hotelStarElemen) > 0):
                        hotelStar = float(hotelStarElemen[0].get_attribute('content'))
                    else:
                        hotelStar = 0

                    hotelAddress = dv.find_element_by_xpath("//span[@itemprop='streetAddress']").text

                    # # split string address with comma to get area and city
                    hotelSplit = hotelAddress.split(', ')
                    AddressExplode = list(reversed(hotelSplit))

                    img_restaurant = 'https://s3-ap-southeast-1.amazonaws.com/traveloka/imageResource/2017/06/07/1496833794378-eb51eee62d46110b712e327108299ea6.png'
                    facilities = dv.find_elements_by_xpath("//img[@class='y9Bbb']")
                    has_restaurant = 'no'
                    for facility in facilities:
                        img_facility = facility.get_attribute('src')
                        if (img_restaurant == img_facility):
                            has_restaurant = 'yes'
                            break
                    
                    hotelLink = dv.find_element_by_xpath("//link[@rel='canonical']").get_attribute('href')
                    hotelLink = list(reversed(hotelLink.split('/')));

                    hotel = Hotel()
                    hotel['id'] = hotelLink
                    hotel['hotelName'] = hotelName
                    hotel['hotelStar'] = hotelStar
                    hotel['hotelAddress'] = hotelAddress
                    hotel['hotelArea'] = AddressExplode[4]
                    hotel['hotelCity'] = AddressExplode[2]
                    hotel['hotelHasRestaurant'] = has_restaurant
                    hotel['hotelHasMeetingRoom'] = '-'
                    hotels.append(hotel)

                    print('===================================== end hotel ======================================') 
                    dv.close()
                    dv.switch_to_window(mainwindow)

                nextButton = dv.find_element_by_xpath("//div[@id='next-button']")
                dv.execute_script('arguments[0].click();', nextButton)
                wait.until(lambda dv: dv.find_elements_by_xpath("//div[@class='mMmI2 CZtP0 tvat-searchListItem']"))

            except Exception as e:
                print(e)
                nextPage = False
        print('============================== finish get data LIST HOTEL ==========================')
        dv.quit()
        del dv
        
        return hotels
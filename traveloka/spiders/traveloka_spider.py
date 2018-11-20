import scrapy
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from traveloka.items import HotelReview
from traveloka.items import TravelokaItem

class TravelokaSpider(scrapy.Spider):
    name = 'traveloka'
    allowed_domains = ['traveloka.com']
    start_urls = ['https://www.traveloka.com/id-id/hotel/search?spec=20-11-2018.21-11-2018.1.1.HOTEL_GEO.102813.Jakarta.2']

    # def parse(self):
    #     urls = [
    #         'https://www.traveloka.com/id-id/hotel/search?spec=15-08-2018.16-08-2018.1.1.HOTEL_GEO.100154.Lampung%20Selatan.1'
    #     ]
    #     for url in urls:
    #         yield scrapy.Request(url, self.parse_hotelList)

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
        listURL = []
        # items = []
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
                    hotelLink = dv.find_element_by_xpath("//link[@rel='canonical']").get_attribute('href')
                    print('===================================== hotel link ======================================') 
                    print('No.',  counter)
                    print(hotelLink)
                    print('===================================== hotel link ======================================') 
                    listURL.append(hotelLink)
                    dv.close()
                    dv.switch_to_window(mainwindow)
                    counter += 1
                    if counter == 5:
                        break

                nextButton = dv.find_element_by_xpath("//div[@id='next-button']")
                dv.execute_script('arguments[0].click();', nextButton)
                wait.until(lambda dv: dv.find_elements_by_xpath("//div[@class='mMmI2 CZtP0 tvat-searchListItem']"))

                # for development
                nextPage = False
            except Exception as e:
                print(e)
                nextPage = False
        print('============================== finish get data LIST HOTEL ==========================')
        dv.quit()
        del dv
        
        # return items
        for url in listURL:
            yield scrapy.Request(url, self.parse_hotelPage)
        del listURL
    
    def parse_hotelPage(self, response):
        print(('========= start hotel page ============'))
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--lang=id')
        options.add_argument('--disable-gpu')
        page = webdriver.Chrome(chrome_options=options)
        page.get(response.url)
        wait = WebDriverWait(page, 20)
        page.implicitly_wait(7)

        hotelName = page.find_element_by_xpath("//h1[@itemprop='name']").text
        hotelRatingElemen = page.find_elements_by_xpath("//div[@class='_3TWbq']")
        if (len(hotelRatingElemen) > 0):
            hotelRating = float(hotelRatingElemen[0].text.replace(',','.'))
        else:
            hotelRating = 0

        hotelStarElemen = page.find_elements_by_xpath("//meta[@itemprop='ratingValue']")
        if (len(hotelStarElemen) > 0):
            hotelStar = float(hotelStarElemen[0].get_attribute('content'))
        else:
            hotelStar = 0
        
        hotelAddress = page.find_element_by_xpath("//span[@itemprop='streetAddress']").text

        try:
            wait.until(lambda page: page.find_elements_by_xpath("//div[@itemprop='review']"))
            getReview = True
        except:
            getReview = False
        
        counter = 0
        nextPage = True
        while nextPage and getReview:
            reviews = page.find_elements_by_xpath("//div[@itemprop='review']")
            hotelReviews = []
            for review in reviews:
                counter += 1
                reviewContent = review.text.split("\n")
                dtContent = reviewContent[2].split(' - ')
                hotelReview = HotelReview()
                hotelReview['hotelName'] = hotelName
                hotelReview['hotelStar'] = hotelStar
                hotelReview['hotelAddress'] = hotelAddress
                hotelReview['hotelRating'] = hotelRating
                hotelReview['reviewRating'] = reviewContent[0]
                hotelReview['reviewName'] = reviewContent[1]
                hotelReview['reviewDate'] = self.getReviewDate(dtContent[0])
                if (len(dtContent) > 1):
                    hotelReview['reviewTheme'] = dtContent[1]
                
                hotelReview['reviewText'] = reviewContent[3]
                hotelReviews.append(hotelReview)
            
            for hotelReview in hotelReviews:
                yield hotelReview
                
            nextButtonElement = page.find_elements_by_xpath("//div[@id='next-button']")
            if (len(nextButtonElement) > 0):
                page.execute_script('arguments[0].click();', nextButtonElement[0])
                page.implicitly_wait(5)
                wait.until(lambda page: page.find_elements_by_xpath("//div[@itemprop='review']"))
            else:
                nextPage = False
                del hotelReviews

        print(('========= end hotel page ============'))
        page.quit()
        del page
    
    def getReviewDate(self, dt):
        tanggal = dt.split(" ")

        if(tanggal[1] == "Jan"):
            bl = 1
        elif(tanggal[1] == "Feb"):
            bl = 2
        elif(tanggal[1] == "Mar"):
            bl = 3
        elif(tanggal[1] == "Apr"):
            bl = 4
        elif(tanggal[1] == "May"):
            bl = 5
        elif(tanggal[1] == "Jun"):
            bl = 6
        elif(tanggal[1] == "Jul"):
            bl = 7
        elif(tanggal[1] == "Agu"):
            bl = 8
        elif(tanggal[1] == "Sep"):
            bl = 9
        elif(tanggal[1] == "Okt"):
            bl = 10
        elif(tanggal[1] == "Nov"):
            bl = 11
        elif(tanggal[1] == "Des"):
            bl = 12
        
        tgl = tanggal[0] + " " + str(bl) + " " + tanggal[2]
        # hasil = time.strptime(tgl, '%d %m %Y').strftime('%Y-%m-%dT%H:%M:%S%z')
        hasil = tgl
        return hasil
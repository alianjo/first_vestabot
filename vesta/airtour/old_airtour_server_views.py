from django.shortcuts import render
from django.conf import settings
from datetime import datetime
from django.http import request, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
import requests, json, uuid, os, threading, redis

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

# @api_view(['GET', 'POST', 'PUT', 'DELETE'])


def open_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=chrome_options)
    return driver

class AutoLogin(APIView):
    def get(self, request):
        global redis_instance

        username = "0651907810"
        password = "09159197502"
        worker = open_driver()
        worker.get('http://iranairtour.ir')
        # login ----------------------------------------------------- login
        if logged_in:
            WebDriverWait(worker, 1).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="headerMenu"]/div[1]/div/div/div[1]/ul/li[3]'))).click()
            WebDriverWait(worker, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, r'//*[@id="loginModal"]/div/div/div[2]/form/div/div[1]/span[2]'))).click()
            WebDriverWait(worker, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, r'//*[@id="loginModal"]/div/div/div[2]/form/div/div[2]/input'))).send_keys(username)
            WebDriverWait(worker, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, r'//*[@id="loginModal"]/div/div/div[2]/form/div/div[3]/input'))).send_keys(password)
            WebDriverWait(worker, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, r'//*[@id="loginModal"]/div/div/div[2]/form/div/div[7]/label/input'))).click()
            WebDriverWait(worker, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, r'//*[@id="loginModal"]/div/div/div[2]/form/div/div[5]/button'))).send_keys(Keys.ENTER)
        # login ----------------------------------------------------- login
        sleep(1.5)
        cookies = worker.get_cookies()
        info_driver = {
            'cookies': cookies,
            'address': worker.current_url
        }
        redis_instance.set(worker.current_url, json.dumps(info_driver))
        driver.quit()

class Index(APIView):
    def __init__(self):
        self.worker = 0
    def selenium_task(self, worker, request):
        global redis_instance
        req = request.data
        worker.get("https://google.com")
        Origin = req['Origin']
        Destination = req['Destination']
        DateText = req['DateText']
        aseats = req['aseats']
        cseats = req['cseats']
        iseats = req['iseats']
        j_DateText = DateText.replace('/', '')
        try:
            info_driver = redis_instance.get('http://iranairtour.ir')
            info_driver = json.loads(info_driver)
            worker.delete_all_cookies()
            cookies = info_driver['cookies']
            for cookie in cookies:
                worker.add_cookie(cookie)
            url = "http://iranairtour.ir/Flight/Search/Domestic/Economy/%s/%s/%s/%s/%s/%s/" % (
                aseats, cseats, iseats, Origin, Destination, j_DateText)
            worker.get(url)
            self.worker = worker
        except:
            self.worker = 0

    def operation(self, request):
        req = request.data
        driver = self.worker

        mobile = req['Mobile']
        email = req['email']
        flight_ID = req['flight_ID']
        count_passengers = int(aseats) + int(cseats) + int(iseats)
        js_string = '''
            document.querySelector("div#flightsListWrapper > div:nth-child(1) > div > div#DepartureFlight%s > div > div > div > div > div.col-md-2.col-xs-12.submit-detail > div.flight-submit-wrapper.hidden-xs > button.custom-button.second-type-button.card-1.card-hover.select-result-button.animate-fade").click();
            window.scrollTo(0, 350);
        ''' % flight_ID
        driver.execute_script(js_string)
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
            By.XPATH,r'//*[@id="sticky-container"]/section[2]/section[2]/div/div/form/div[1]/div[1]/input'))).send_keys(mobile)
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="Email"]'))).clear()
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="Email"]'))).send_keys(email)

        for count in range(count_passengers):
            passengers = req['passengers']
            Name = passengers[count]['Name']
            LastName = passengers[count]['LastName']
            Gender = int(passengers[count]['Gender']) + 1
            Gender = "number:%s" % Gender
            NationalID = passengers[count]['NationalID']
            PersianName = passengers[count]['PersianName']
            PersianLastName = passengers[count]['PersianLastName']
            passengers_type = passengers[count]['passengers_type']

            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="Name%s"]' % count))).send_keys(Name)
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="LastName%s"]' % count))).send_keys(LastName)
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, r'//*[@id="Gender%s"]/option[@value="%s"]' % (count, Gender)))).click()
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="PersianName%s"]' % count))).send_keys(PersianName)
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="PersianLastName%s"]' % count))).send_keys(
                PersianLastName)
            if passengers_type == "1":
                WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, r'//*[@id="NationalID%s"]' % count))).send_keys(NationalID)
            elif passengers_type == "2":
                IssuingBirth = passengers[count]['IssuingBirth']
                IssuingPassports = passengers[count]['IssuingPassports']
                PassportNumber = passengers[count]['PassportNumber']
                BirthDay = passengers[count]['BirthDay']
                BirthYear = passengers[count]['BirthYear']
                BirthMonth = passengers[count]['BirthMonth']
                ExpiryDay = passengers[count]['ExpiryDay']
                ExpiryMonth = passengers[count]['ExpiryMonth']
                ExpiryYear = passengers[count]['ExpiryYear']
                # BirthMonth = num_to_month(BirthMonth)
                # ExpiryMonth = num_to_month(ExpiryMonth)
                # '//*[@id="sticky-container"]/section[2]/section[2]/div/div/form/div[3]/div[3]/div[1]/div/span[2]'
                # '//*[@id="sticky-container"]/section[2]/section[2]/div/div/form/div[4]/div[3]/div[1]/div/span[2]'
                cnt = int(count) + 3
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, '#sticky-container > section.main-wrapper.col-md-9.col-sm-12.col-xs-12.float-left >'
                                     ' section.passenegrs-info.card-1.card-wrapper.animate-fade > div > div > form > '
                                     'div:nth-child(%s) > div:nth-child(3) > div.col-md-12.ng-scope > div > '
                                     'span:nth-child(2)' % cnt))).click()
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="BirthDate%s"]/div[1]/select/option[@value="%s"]' % (count, BirthDay)))).click()
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH,r'//*[@id="BirthDate%s"]/div[2]/select/option[@value="%s"]' % (count, BirthMonth)))).click()
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="BirthDate%s"]/div[3]/select/option[@value="%s"]' % (count, BirthYear)))).click()
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="IssuingBirth%s"]' % count))).send_keys(IssuingBirth)
                sleep(0.8)
                # WebDriverWait(driver, 1).until(
                #     EC.element_to_be_clickable((By.XPATH, r'//*[@id="FlightScopeWrapper"]/div/div[5]/div[2]/ul/li[4]'))).click()
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="IssuingPassports%s"]' % count))).send_keys(IssuingPassports)
                # WebDriverWait(driver, 1).until(
                #     EC.element_to_be_clickable((By.XPATH, r'//*[@id="FlightScopeWrapper"]/div/div[5]/div[1]/ul/li[4]'))).click()
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="PassportNumber%s"]' % count))).send_keys(PassportNumber)
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="PassportExpiry%s"]/div[1]/select/option[@value="%s"]' % (count, ExpiryDay)))).click()
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="PassportExpiry%s"]/div[2]/select/option[@value="%s"]' % (count, ExpiryMonth)))).click()
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="PassportExpiry%s"]/div[3]/select/option[@value="%s"]' % (count, ExpiryYear)))).click()

        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, '#sticky-container > section.main-wrapper.col-md-9.col-sm-12.col-xs-12.float-left > '
                             'section.passenegrs-info.card-1.card-wrapper.animate-fade > div > div > form > '
                             'div.passengers-info.submit > div:nth-child(1) > div.col-md-3.col-xs-12.submit-wrapper > '
                             'button'))).click()

        # js_string = '''
        #     document.querySelector("#sticky-container > section.main-wrapper.col-md-9.col-sm-12.col-xs-12.float-left > section.reserve-info-wrapper.card-1.card-wrapper.animate-fade > div.reserve-info.submit-wrapper > div > div > div.reserve-inner > div > div.col-md-12.flight-purchase-rules > div.col-md-6.flight-purchase-rules > label > input#InfoAccuracyAccept").click();
        # '''
        # driver.execute_script(js_string)

        # WebDriverWait(driver, 1).until(
        #     EC.element_to_be_clickable((By.XPATH, r'/html/body/div[4]/div/div/div[3]/section/section[2]/section[3]/div[4]/div/div/div[2]/div/div[1]/div[2]/label/input'))).click()

        data = {
            'status': True,
            'value': "specification"
        }
        driver.quit()
        return data

        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="sticky-container"]/section[2]/section[3]/div[6]/div[2]/button'))).click()
        specification = []
        for i in range(count_passengers):
            Ticket_number = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="FlightIssueScopeWrapper"]/div[%s]/div/div/div/div[2]/table[1]/tbody/tr[3]/td[1]' % i))).text
            Booking_ref = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="FlightIssueScopeWrapper"]/div[%s]/div/div/div/div[2]/table[1]/tbody/tr[3]/td[4]' % i))).text
            data = {
                "Ticket_number": Ticket_number,
                "Booking_ref": Booking_ref
            }
            specification.append(data)
        data = {
            'status': True,
            'value': specification
        }
        return data

        # WebDriverWait(driver, 1).until(
        #     EC.element_to_be_clickable((By.XPATH, r'//*[@id="domOrigin"]'))).send_keys(Origin)
        # WebDriverWait(driver, 1).until(
        #     EC.element_to_be_clickable((By.XPATH, r'//*[@id="domDestionation"]'))).send_keys(Destination)
        # WebDriverWait(driver, 1).until(
        #     EC.element_to_be_clickable((By.XPATH, r'//*[@id="domDepartureDate"]"]'))).send_keys(DateText)
        # WebDriverWait(driver, 1).until(
        #     EC.element_to_be_clickable((By.XPATH, r'//*[@id="domFlight"]/div[2]/form/div/div[5]/div/button'))).send_keys(Keys.ENTER)

        # js_string = '''
        #     location.replace("http://iranairtour.ir/Flight/Search/Domestic/Economy/%s/%s/%s/%s/%s/%s/");
        # '''% (aseats, cseats, iseats, Origin, Destination, j_DateText)
        # driver.execute_script(js_string)

        # org = driver.find_elements_by_xpath("//*[text()='Login or register']")
        # print(org)
        # login = driver.find_elements_by_xpath("//ul[@class='header-tools']")#.

        # log = driver.find_element_by_class_name("header-tools")
        # link = driver.find_element_by_xpath(".//*[@class='header-tools']/li[3]/a")
        # link.click()

        # link = driver.find_element_by_xpath("//body/div[5]/div/div/div[2]/form/div/div[1]/span[2]")
        # link = driver.find_element_by_xpath(".//*[@id='loginModal']/div/div/div[2]/form/div/div[1]/span[2]")
        # link = driver.find_element_by_id("loginModal")

        # link = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/form/div/div[1]/span[2]")
        # link = driver.find_element_by_tag_name("body")
        # link = driver.find_element_by_id('loginModal')
        # link = link.find_element_by_name('loginForm')
        # link = driver.find_element_by_xpath("/form[@name='loginForm']")
        # link = driver.find_element_by_xpath(".//*[@name='loginForm']/div/div[@class='field-wrapper'][1]/input")
        # link.send_keys(username)
        # link = driver.find_element_by_xpath(".//*[@name='loginForm']/div/div[@class='field-wrapper'][2]/input")
        # link.send_keys(password)
        # log = log.find_elements_by_class_name("header-items").send_keys(Keys.ENTER)
        # lll = log[2].find_element_by_tag_name("a").text
        # print("--------"+ lll +"--------")

        # login = driver.find_element_by_xpath("/*[@id='loginModel']")#driver.find_element_by_id('loginModel')
        # login = login.find_element_by_name("loginForm")
        # login = login.find_element_by_class_name("custom-login")
        # login = login.find_element_by_xpath("/span[1]")
        # login.send_keys(Keys.ENTER)

        # login = login.find_elements_by_class_name('header-items')[2]
        # login[0].send_keys(Keys.ENTER)

        # driver.find_elements_by_xpath('//ul[@class="header-tools"]/li[2]/a[0]').send_keys(Keys.ENTER)
        # log = driver.find_elements_by_xpath("//li[@class='header-items']")[2]
        # print(log)
        # log.click()
        # login = driver.find_element_by_class_name('header-tools')
        # login = login.find_element_by_class_name('header-items[3]')
        # js_string = '''refrence = document.getElementsByClassName("header-tools");refrence[0].children[2].children[0].click();
        #     login_colleague = document.getElementsByClassName("custom-login");login_colleague[0].children[1].click();
        #     login_colleague[0].nextElementSibling.children[2].focus();
        #     login_colleague[0].nextElementSibling.children[2].value="%s";
        #     login_colleague[0].nextElementSibling.children[2].blur();
        #     login_colleague[0].nextElementSibling.nextElementSibling.children[2].focus();
        #     login_colleague[0].nextElementSibling.nextElementSibling.children[2].value="%s";
        #     login_colleague[0].nextElementSibling.nextElementSibling.children[2].blur();
        #     document.getElementsByClassName("checkbox-label")[0].children[0].click();
        #     login_colleague[0].nextElementSibling.nextElementSibling.nextElementSibling.nextElementSibling.children[0].click();'''% (username, password)
        # driver.execute_script(js_string)
        # sleep(1)
        # driver.save_screenshot('D:\\screenie005.png')

    def post(self, request):
        worker = open_driver()
        t = threading.Thread(target=self.selenium_task, args=(worker, request))
        t.start()   # Start threads
        t.join()    # Wait on threads to finish
        if self.worker == 0:
            data = {
                'status': False,
                'message': 'بارگذاری صفحه شکست خورد'
            }
            return Response(data=data, status=status.HTTP_200_OK)
        data = self.operation(request)
        return Response(data=data, status=status.HTTP_200_OK)

class SearchFlight(APIView):
    def __init__(self):
        self.worker = 0
    def selenium_task(self, worker, request):
        req = request.data
        Origin = req['Origin']
        Destination = req['Destination']
        DateText = req['DateText']
        aseats = req['aseats']
        cseats = req['cseats']
        iseats = req['iseats']
        j_DateText = DateText.replace('/', '')
        try:
            url = "http://iranairtour.ir/Flight/Search/Domestic/Economy/%s/%s/%s/%s/%s/%s/" % (
                aseats, cseats, iseats, Origin, Destination, j_DateText)
            worker.get(url)
            self.worker = worker
        except:
            self.worker = 0

    def operation(self):
        driver = self.worker
        count_trying = 0
        while True:
            if count_trying >= 2:
                data = {
                    'status': False,
                    'message': 'کدهای جاوااسکریپت سمت سرور مشکل دارد'
                }
                return data
            try:
                js_string = '''
                    function initdata(){
                        list_flights = [];
                        lenFly = list.length;
                        for(i=0;i<lenFly;i++){
                            data = {}
                            if (list[i]['FlightGroups'][0]['FlightDetails'][0]['Status'] != 0){
                                Day = list[i]['FlightGroups'][0]['DepartureFullDate']['Day_shamsi']
                                Week = list[i]['FlightGroups'][0]['DepartureFullDate']['WeekDay_persian']
                                Month = list[i]['FlightGroups'][0]['DepartureFullDate']['Month_persian']
                                shamsiDepartureDate = Month + ' ' + Day + ' , ' + Week
                                data = {
                                    price: list[i]['Total'],
                                    supplierLogoUrl: 'http://iranairtour.ir/Content/Images/logo/airtour.svg',
                                    cabinType: list[i]['FlightGroups'][0]['ClassTypeForView'],
                                    originAirportIataCode: list[i]['FlightGroups'][0]['Origin'],
                                    cleanFlightNumber: list[i]['FlightGroups'][0]['FlightDetails'][0]['FlightNumber'],
                                    "operatorName": "iranairtour",
                                    "gregorianDepartureDate": list[i]['FlightGroups'][0]['FlightDetails'][0]['DepartureDay'],
                                    "airlineName": "ایران ایرتور",
                                    "seatCount": list[i]['FlightGroups'][0]['FlightDetails'][0]['Status'],
                                    "supplierNameFa": "ایران ایرتور",
                                    "description": " ",
                                    "formattedInfantPrice": list[i]["Pricing"][2]['TotalForView'],
                                    "originAirportName": list[i]['FlightGroups'][0]['OriginForViewFa'],
                                    "arrivalDateTime": list[i]['FlightGroups'][0]['ArrivalFullDate']['DateTimeString'].replace(' ', 'T'),
                                    "shamsiDepartureDate": shamsiDepartureDate,
                                    "airlineLogoUrl": 'http://iranairtour.ir/Content/Images/logo/airtour.svg',
                                    "destinationAirportIataCode": list[i]['FlightGroups'][0]['Destination'],
                                    "airplaneName": list[i]['FlightGroups'][0]['FlightDetails'][0]['Aircraft'],
                                    "supplierCity": list[i]['FlightGroups'][0]['OriginForViewFa'],
                                    "departureTime": list[i]['FlightGroups'][0]['DepartureTime'] + ":00",
                                    "airlineIataCode": "B9",
                                    "formattedAdultPrice": list[i]["Pricing"][0]['TotalForView'],
                                    "departureDateTime": list[i]['FlightGroups'][0]['DepartureFullDate']['DateTimeString'].replace(' ', 'T'),
                                    "destinationAirportName": list[i]['FlightGroups'][0]['DestinationForViewFa'],
                                    "cleanDepartureTime": "13:40",
                                    "formattedChildPrice": list[i]["Pricing"][1]['TotalForView'],
                                }
                                list_flights.push(data)
                            }
                        }
                    }
                    var flights = list;
                    initdata();
    
                    return list_flights;
                '''
                sleep(1)
                list_flights = driver.execute_script(js_string)
                data = {
                    'status': True,
                    'value': list_flights
                }
                break
            except:
                count_trying = count_trying + 1
                continue
        driver.quit()
        return data

    def post(self, request):
        worker = open_driver()
        t = threading.Thread(target=self.selenium_task, args=(worker, request))
        t.start()   # Start threads
        t.join()    # Wait on threads to finish
        if self.worker == 0:
            data = {
                'status': False,
                'message': 'بارگذاری صفحه شکست خورد'
            }
            return Response(data=data, status=status.HTTP_200_OK)
        data = self.operation()
        return Response(data=data, status=status.HTTP_200_OK)




# import pandas as pd
# df = pd.DataFrame(list_flights)
# df.to_csv('data.csv')
# df = pd.read_csv('data.csv', index_col=0)
# df.to_excel('data.xlsx')
# df = pd.read_excel('data.xlsx', index_col=0)
# .to_json()  read_json()
# .to_html()  read_html()
# .to_sql()  read_sql()
# .to_pickle()  read_pickle()

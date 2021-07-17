from uuid import uuid4
from urllib.parse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings
# from django.http import JsonResponse
from sepehr.models import Supplier
from .serializers import first_validation, private_search_validation
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.core.cache import cache
from bs4 import BeautifulSoup
from time import sleep
from PIL import Image
from io import BytesIO
from persiantools.jdatetime import JalaliDate
import logging, logger, threading, os, json, urllib3, redis, requests, datetime

'''
logger.info("just for information")
logger.debug("Harmless debug Message!!!")
logger.warning("Its a Warning")
logger.error("Did you try to divide by zero")
logger.critical("Internet is down")
'''
'''cookies = driver.get_cookies()
cache.set('cookies', cookies, 100) # 100 seconds
cookies = cache.get('greeting')'''

logger = logging.getLogger(__name__)
path_captcha = r'/home/vesta/projects/vestabot/vesta/static/admin/captcha'
REDIS_TIMEOUT = 172800 # 2 days
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)
def open_driver():
    """
    openning webdriver with option: --headless > open browser without window
    :return: driver Type: object Webdriver
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=chrome_options)
    return driver

def default_argument(string = 'default'):
    """
    for manage params *args and **kwargs , manage error and set 'default' , if args or kwargs is empty
    :param string:
    :return: 'default' if args or kwargs is empty else value param
    """
    return string

class operation(object):
    def __init__(self, *args, **kwargs):
        self.lists = default_argument(args)
        self.dict = default_argument(kwargs)

    def readcredit(self):
        """
        read the credit account in supplier
        :param worker Type: object webdriver
        :return: 'logout' if error in code else credit account
        """
        driver = self.dict['worker']
        try:
            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            link = soup.find_all("a", class_="UserLink")[0]
            credit = link.select("b")[0].text
            return credit
        except:
            return 'logout'

    def req_captcha(self):
        global path_captcha, selenium_worker
        driver = self.dict['worker']
        status_arrive = self.dict['status_arrive']
        sup_obj = self.dict['sup_obj']
        url = 'https://' + sup_obj.address
        name_tab = str(uuid4())
        loop_check = 0
        while True:
            if loop_check >= 4:
                driver.quit()
                data = {
                    'status': False,
                    'message': "Faild In Connect"
                }
                return data
            try:
                driver.get(url)
                WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, r'//*[@id="dplLoginMode"]')))
                break
            except:
                loop_check += 1
                continue

        # -----------------------------LOGIN----------------------------------
        # PublicLogin
        # AgentLogin
        loop_check = 0
        while True:
            if loop_check >= 4:
                driver.quit()
                data = {
                    'status': False,
                    'message': "بارگذاری صفحه شکست خورد"
                }
                return data
            try:
                if status_arrive == 'AgentLogin':
                    ####################
                    inputElement = Select(driver.find_element_by_id("dplLoginMode"))
                    inputElement.select_by_value('AgentLogin')
                    sleep(0.8)
                    _txtUsername = sup_obj.username
                    _txtPassword = sup_obj.password
                    inputElement = driver.find_element_by_id("txtUsername")
                    inputElement.send_keys(_txtUsername)
                    inputElement = driver.find_element_by_id("txtPassword")
                    inputElement.send_keys(_txtPassword)
                break
            except:
                loop_check += 1
                continue
        # -----------------------------LOGIN----------------------------------

        try:
            element = driver.find_element_by_id('imgCaptcha')
            location = element.location
            size = element.size
            png = driver.get_screenshot_as_png()
            img = Image.open(BytesIO(png))
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            img = img.crop((left, top, right, bottom))
            name_pic = "{}.png".format(name_tab)
            path = '%s/%s' % (path_captcha, name_pic)
            img.save(path)
            selenium_worker = driver
        except:
            data = {
                'status': False,
                'message': 'مشکل در فرایند جداسازی و ذخیره فایل کپچا'
            }
            return data
        data = {
            'status': True,
            'session_web': driver.window_handles[-1],
            'url_pic': name_pic
        }
        return data

    def private_search(self):
        # search only in site flight.mdsafar.ir
        worker = self.dict['worker']

        date_fa = self.dict['date'].split("/")
        date_en = JalaliDate(int(date_fa[0]), int(date_fa[1]), int(date_fa[2])).to_gregorian()
        date_en_dash = date_en.strftime("%Y-%m-%d")
        date_en = date_en.strftime("%m/%d/%Y")
        js_string = '''
            function search(){
                let list_flight = [];
                let js_tbody = document.getElementsByClassName("tblSR")[0].querySelector("tbody");
                let count_row = js_tbody.rows.length;
                let dplFrom = document.querySelector("#dplFrom").value.toLowerCase();
                let dplTo = document.querySelector("#dplTo").value.toLowerCase();
                var date_en = "%s";
                var date_en_dash = "%s";
                var supplierNameFa = "معین درباری";
                var airlines = {"زاگــــرس": "ZV", "کاسپین": "IV", "آتـــــــــــا": "I3", "آسمان": "EP", "ايران اير": "IR", "ايران ايــــرتـور": "B9", "تابان": "HH", "قشم اير": "QB", "کارون ایر": "NV", "مــاهــان": "W5", "معراج": "JI", "کیش ایر": "Y9", "سپهران": "IS", "وارش": "VR", "ســـــاها": "IRZ", "اترک": "AK", "ترکيش": "TK"}
                for (let r = 2; r <= count_row; r++) {
                    let status = document.querySelectorAll(`#tdMain > table.tblSR >
                     tbody > tr:nth-child(${r}) > td:nth-child(8)`)[0].textContent.trim();
                    if (status === 'OnTime') {
                        let move = document.querySelectorAll(`#tdMain > table.tblSR >
                         tbody > tr:nth-child(${r}) > td:nth-child(2)`)[0].textContent.trim();
                        move = move.split("به")
                        let origin = move[0];
                        let destination = move[1];
                        let sel = document.getElementById("dplFrom");
                        let IataOrigon = sel.options[sel.selectedIndex].value;
                        sel = document.getElementById("dplTo");
                        let IataDestination = sel.options[sel.selectedIndex].value;
                        let cleanDepartureTime = document.querySelectorAll(`#tdMain > table.tblSR >
                         tbody > tr:nth-child(${r}) > td:nth-child(4)`)[0].textContent.trim();
                        let arrivalTime = document.querySelectorAll(`#tdMain > table.tblSR >
                         tbody > tr:nth-child(${r}) > td:nth-child(5)`)[0].textContent.trim();
                        let flyInfo = document.querySelectorAll(`#tdMain > table.tblSR >
                         tbody > tr:nth-child(${r}) > td:nth-child(6)`)[0].textContent.trim();
                        let cleanFlightNumber = document.querySelectorAll(`#tdMain > table.tblSR >
                         tbody > tr:nth-child(${r}) > td:nth-child(7)`)[0].textContent.trim();
                        let airplaneName = flyInfo.split(`\n`)[0];
                        let airlineName = flyInfo.split(`\n`)[1].trim();
                        let tr_counts = document.querySelectorAll(`#tdMain > table.tblSR >
                         tbody > tr:nth-child(${r}) > td:nth-child(1) > table.tblNB > tbody > tr`).length;
                        if(tr_counts === 1) {
                            let adultInfo = document.querySelector(`#tdMain > table.tblSR > tbody >
                             tr:nth-child(${r}) > td:nth-child(1) > table.tblNB > tbody > tr:nth-child(1) >
                              td:nth-child(2) > span > label`)[0].textContent;
                            adultInfo = adultInfo.trim();
                            let adultPrice = adultInfo.split(" ")[1];
                            let iAdultPrice = parseInt(adultPrice.replace(/,/g, ''))
                            let sAdultPrice = iAdultPrice / 10;
                            sAdultPrice = sAdultPrice.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                            let iSeatCount = parseInt(adultInfo.split(" ")[2]);
                            let object = {
                                "rph": "317" + dplFrom + dplTo + cleanFlightNumber + date_en + "23economy",
                                "airlineIataCode": airlines[airlineName],
                                "airlineLogoUrl": null,
                                "airlineName": airlineName,
                                "airplaneName": airplaneName,
                                "arrivalDateTime": date_en_dash + "T" + arrivalTime + ":00",
                                "cabinType": "economy",
                                "cleanDepartureTime": cleanDepartureTime,
                                "cleanFlightNumber": cleanFlightNumber,
                                "departureDateTime": date_en_dash + "T" + cleanDepartureTime + ":00",
                                "departureTime": cleanDepartureTime + ":00",
                                "description": " ",
                                "destinationAirportIataCode": IataDestination,
                                "destinationAirportName": destination,
                                "flightType": 0,
                                "formattedAdultPrice": sAdultPrice,
                                "formattedChildPrice": "233,000",
                                "formattedInfantPrice": "31,000",
                                "gregorianDepartureDate": "29 Sep",
                                "isTazminGheymat": false,
                                "operatorColor": "#eb7700",
                                "operatorName": "سپهر",
                                "originAirportIataCode": IataOrigon,
                                "originAirportName": origin,
                                "price": iAdultPrice,
                                "seatCount": iSeatCount,
                                "shamsiDepartureDate": "دوشنبه، 31 شهریور",
                                "supplierAddress": null,
                                "supplierCity": "تهران",
                                "supplierLogoUrl": "/Content/Image/Availability/Supplier/Common/Logo//214.svg?ts=33021045229363",
                                "supplierNameFa": "معین درباری",
                                "supplierRanking": 3,
                                "serviceQuality": {
                                    "isCancelAvail": true,
                                    "isOnlineSupport": true,
                                    "isGuarantyToNotCancel": true,
                                    "isReturnMoney": true,
                                    "hasTicketPurchaseNotification": true
                                },
                                "jarimeCanceli": {
                                    "isGhabeleEsterdad": 1,
                                    "jarime": ""
                                }
                            }
                            list_flight.push(object);
                        }
                        else {
                            for(let j = 1; j <= tr_counts; j++){
                                let adultInfo = document.querySelectorAll(`#tdMain > table.tblSR > tbody >
                                 tr:nth-child(${r}) > td:nth-child(1) > table.tblNB > tbody > tr:nth-child(${j}) >
                                  td:nth-child(2) > span > label`)[0].textContent;
                                adultInfo = adultInfo.trim();
                                let adultPrice = adultInfo.split(" ")[1];
                                let iAdultPrice = parseInt(adultPrice.replace(/,/g, ''))
                                let sAdultPrice = iAdultPrice / 10;
                                sAdultPrice = sAdultPrice.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                                let iSeatCount = parseInt(adultInfo.split(" ")[2]);
                                let object = {
                                    "rph": "317" + dplFrom + dplTo + cleanFlightNumber + date_en + "economy",
                                    "airlineIataCode": airlines[airlineName],
                                    "airlineLogoUrl": null,
                                    "airlineName": airlineName,
                                    "airplaneName": airplaneName,
                                    "arrivalDateTime": date_en_dash + "T" + arrivalTime + ":00",
                                    "cabinType": "economy",
                                    "cleanDepartureTime": cleanDepartureTime,
                                    "cleanFlightNumber": cleanFlightNumber,
                                    "departureDateTime": date_en_dash + "T" + cleanDepartureTime + ":00",
                                    "departureTime": cleanDepartureTime + ":00",
                                    "description": " ",
                                    "destinationAirportIataCode": IataDestination,
                                    "destinationAirportName": destination,
                                    "flightType": 0,
                                    "formattedAdultPrice": sAdultPrice,
                                    "formattedChildPrice": "233,000",
                                    "formattedInfantPrice": "31,000",
                                    "gregorianDepartureDate": "29 Sep",
                                    "isTazminGheymat": false,
                                    "operatorColor": "#eb7700",
                                    "operatorName": "سپهر",
                                    "originAirportIataCode": IataOrigon,
                                    "originAirportName": origin,
                                    "price": iAdultPrice,
                                    "seatCount": iSeatCount,
                                    "shamsiDepartureDate": "دوشنبه، 31 شهریور",
                                    "supplierAddress": null,
                                    "supplierCity": "تهران",
                                    "supplierLogoUrl": "/Content/Image/Availability/Supplier/Common/Logo//214.svg?ts=33021045229363",
                                    "supplierNameFa": supplierNameFa,
                                    "supplierRanking": 3,
                                    "serviceQuality": {
                                        "isCancelAvail": true,
                                        "isOnlineSupport": true,
                                        "isGuarantyToNotCancel": true,
                                        "isReturnMoney": true,
                                        "hasTicketPurchaseNotification": true
                                    },
                                    "jarimeCanceli": {
                                        "isGhabeleEsterdad": 1,
                                        "jarime": ""
                                    }
                                }
                                list_flight.push(object);
                            }
                        }
                    }
                }
                return list_flight;
            }
            listflight = search();
            return listflight;
        '''% (date_en, date_en_dash)
        sleep(1.3) # sleep nabayad pak shavad. chon bayad code python sabr kone ta tamame page, load beshe
        data = WebDriverWait(worker, 15).until(
            lambda driver: worker.execute_script(js_string)
        )
        return data


# Search only [ site: private company ]
class PrivateSearch(APIView):
    def selenium_task(self, worker, url):
        global redis_instance
        worker.get("https://google.com")
        try:
            info_driver = redis_instance.get(url)
            info_driver = json.loads(info_driver)
            worker.delete_all_cookies()
            cookies = info_driver['cookies']
            for cookie in cookies:
                worker.add_cookie(cookie)
            worker.get(info_driver['address'])
            self.worker = worker
            # redis_instance.set("driver", self.worker.session_id)
            # .window_handles[0]
        except:
            worker.quit()
            worker = 0
    def search(self, request):
        worker = open_driver()
        address = request.data['url']
        t = threading.Thread(target=self.selenium_task, args=(worker, address))
        t.start()  # Start threads
        t.join()  # Wait on threads to finish
        if self.worker == 0:
            data = {
                'status': False,
                'message': 'بارگذاری صفحه شکست خورد'
            }
            return data

        self.data = request.data
        Path = 'OneWay'
        From = self.data['source']
        To = self.data['destination']
        date_fa = self.data['date']
        sleep(1.8)
        try:
            inputElement = Select(WebDriverWait(self.worker, 10).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="dplFrom"]'))))
            inputElement.select_by_value(From)
            inputElement = Select(WebDriverWait(self.worker, 10).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="dplReservationRouteType"]'))))
            inputElement.select_by_value(Path)
            sleep(1.5)  # TODO This line should not be deleted (Low speed of internet)
            WebDriverWait(self.worker, 10).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="txtDepartureDate"]'))).clear()
            WebDriverWait(self.worker, 10).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="txtDepartureDate"]'))).send_keys(date_fa)
            inputElement = Select(WebDriverWait(self.worker, 10).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="dplTo"]'))))
            inputElement.select_by_value(To)
            WebDriverWait(self.worker, 10).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="btnSubmit"]'))).send_keys(Keys.ENTER)
        except:
            data = {
                'status': False,
                'message': 'مشکل در اتصال'
            }
            return data
        _dict = {'worker': self.worker, 'date': date_fa}
        obj = operation(**_dict)
        result = obj.private_search()
        data = {
            'status': True,
            'result': result
        }
        self.worker.quit()
        return data
        # return Response(data=data, status=status.HTTP_200_OK)
    def post(self, request):
        ## datas['date'] = "1399/02/24"
        # datas['date'] = "2020-09-23" > "year-month-day"
        data = []
        try:
            validation = private_search_validation(data=request.data)
            if validation.is_valid():
                pass
            else:
                obj = {
                    'status': False,
                    'message': validation.errors
                }
                return Response(data=obj, status=status.HTTP_200_OK)
            obj = self.search(request)
            if obj["status"]:
                data = {
                    "value": obj["result"]
                }
        except:
            # Error
            pass
        return Response(data=data, status=status.HTTP_200_OK)
# Search only [ site: private company ]


# Search only [ site: sepehr360.ir ]
class SearchSepehr(APIView):
    def get(self, request):
        return Response(data={"data": "Hello world"}, status=status.HTTP_200_OK)
    def post(self, request):
        ## datas['date'] = "1399/02/24"
        # datas['date'] = "2020-09-23" > "year-day-month"
        # datas['seatCount'] =>> integer
        try:
            url = 'https://api.sepehr360.ir/fa/FlightAvailability/Api/B2bOnewayFlightApi/Search'
            datas = request.data
            # date_en = datas['date'].split("-")
            # date = JalaliDate.to_jalali(int(date_en[0]), int(date_en[1]), int(date_en[2]))
            # date = date.year + '/' + date.month + '/' + date+day
            res = []
            date = datas['date']
            source = datas['source']
            destination = datas['destination']
            # seat_count = datas['seatCount']
            http = urllib3.PoolManager()
            count = 0
            while True:
                data = json.dumps({
                    "commonClientServerData": "",
                    "deviceToken": "",
                    "sessionId": "",
                    "commonClientServerDataVersion": "",
                    "intervalDays": 0, "curencyType": "IRR",
                    "flightNumber": "", "cabinFilterList": [],
                    "dayPartsFilterList": [], "airLinesFilterList": [],
                    "daysFilterList": [], "sortOrder": 1, "pageSize": 200,
                    "pageNumber": count, "isMobileWeb": False, "originAirportIataCode": source,
                    "destinationAirportIataCode": destination, "departureDate": date
                })
                r = http.request('POST', url, body=data, headers={'Content-Type': 'application/json'})
                pastebin_url = json.loads(r.data.decode('utf-8'))
                for fly in pastebin_url['flightHeaderList']:
                    res.append(fly)
                    # if 'listTaminKonandeganSahmiyeShenavar' not in fly and fly['supplierNameFa'] in sup_name and fly['seatCount'] >= seat_count:
                    #     res.append(fly)
                count += 1
                if pastebin_url['flightHeaderList'] == [] or count > 7:
                    break
            list_flight = {
                "value": res,
                "airlinesMinPriceList": pastebin_url['airlinesMinPriceList']
            }
        except:
            list_flight = []
        return Response(data=list_flight, status=status.HTTP_200_OK)
        # return Response({'value': res}, status=status.HTTP_200_OK)
        # return Response(res, status=status.HTTP_200_OK)
        # return Response(data=json.dumps(res), status=status.HTTP_200_OK)
# Search only [ site: sepehr360.ir ]

class AdminTemplate(object):
    def __init__(self, queryset):
        self.queryset = queryset
    def disableSup(self):
        global redis_instance
        objects = self.queryset.filter(status=True)
        for obj in list(objects):
            try:
                # TODO: agar lazem be logout dar suppliers bod , ghesmat haye command shode ro barmidarim.
                ###############################
                # worker = open_driver()
                # worker.get("https://google.com")
                # info_driver = redis_instance.get(obj.address)
                # info_driver = json.loads(info_driver)
                # worker.delete_all_cookies()
                # cookies = info_driver['cookies']
                # for cookie in cookies:
                #     worker.add_cookie(cookie)
                # worker.get(info_driver['address'])
                # js_string = '''document.querySelector(
                #     "#Form1 > table > tbody > tr:nth-child(5) > td > center > div > table > tbody > tr:nth-child(6)
                #      session_id> td > center > table > tbody > tr > td:nth-child(1) > a").click();'''
                # worker.execute_script(js_string)
                # worker.quit()
                ################################
                redis_instance.delete(obj.address)
            except:
                self.queryset.filter(address=obj.address).update(status=False, credit='0.0')
                # worker.quit()
                continue
        objects.update(status=False, credit='0.0')
        return True

    def reloadCreditSup(self):
        global redis_instance
        objects = self.queryset.filter(status=True)
        for obj in list(objects):
            try:
                worker = open_driver()
                worker.get("https://google.com")
                info_driver = redis_instance.get(obj.address)
                info_driver = json.loads(info_driver)
                worker.delete_all_cookies()
                cookies = info_driver['cookies']
                for cookie in cookies:
                    worker.add_cookie(cookie)
                worker.get(info_driver['address'])
            except:
                self.queryset.filter(address=obj.address).update(status=False, credit='0.0')
                continue
            worker.execute_script("location.reload();")
            _dict = {'worker': worker}
            obj = operation(**_dict)
            credit = obj.readcredit()
            objects.filter(alias_name=obj.alias_name).update(credit=credit)
        return True


class GetCaptcha(APIView):
    def get(self, request):
        # Crop Captcha And Sending To Response
        try:
            # breakpoint()
            sup_obj = Supplier.objects.get(name_rnd=request.GET['rnd_name_sup'])
            worker = open_driver()
            worker.get('https://' + sup_obj.address)
            _dict = {'sup_obj': sup_obj, 'status_arrive': 'AgentLogin', 'worker': worker}
            obj = operation(**_dict)
            data = obj.req_captcha()
        except Supplier.DoesNotExist:
            data = {
                'status': False,
                'text': 'This supplier is incorrect'
            }
        return Response(data=data, status=status.HTTP_200_OK)
class SetCaptcha(APIView):
    def get(self, request):
        global selenium_worker, redis_instance
        driver = selenium_worker
        # And now output all the available cookies for the current URL

        url_pic = request.GET['url_pic']
        if request.GET['url_pic'] != '':
            path = path_captcha + '/' + url_pic
            try:
                os.remove(path)
            except:
                del path
        try:
            session_id = request.GET['session_web']
            driver.switch_to.window(session_id)
            sup_obj = Supplier.objects.get(name_rnd=request.GET['rnd_name_sup'])
        except:
            driver.quit()
            data = {
                'status': False,
                'type': 'supplier',
                'text': "supplier not found, Please reload this page",
            }
            return Response(data=data, status=status.HTTP_200_OK)
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="txtCaptchaNumber"]'))).send_keys(request.GET['txtCaptchaNumber'])
            driver.find_element_by_xpath('//*[@id="btnLogin"]').click()
            sleep(0.5)
            driver.find_element_by_id("Header1_Tr1")
        except:
            text_error = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
                By.ID, 'Module_Error1__tdError'))).text
            # text_error = driver.find_element_by_id("Module_Error1__tdError").text
            driver.get('https://' + sup_obj.address)
            _dict = {'sup_obj': sup_obj, 'status_arrive': 'AgentLogin', 'worker': driver}
            obj = operation(**_dict)
            datas = obj.req_captcha()
            data = {
                'status': False,
                'type': 'Bad Request',
                'text': text_error,
                'session_web': datas['session_web'],
                'url_pic': datas['url_pic']
            }
            return Response(data=data, status=status.HTTP_200_OK)
        try:
            credit_validation = 0
            _dict = {'worker': driver}
            obj = operation(**_dict)
            credit = obj.readcredit()
            if credit == 'logout':
                credit_validation = 1
            else:
                sup_obj.status = True
                sup_obj.credit = credit
                sup_obj.save()
                cookies = driver.get_cookies()
                info_driver = {
                    'cookies': cookies,
                    'address': driver.current_url
                }
                redis_instance.set(sup_obj.address, json.dumps(info_driver))
                data = {'status': True, 'name_sup': sup_obj.alias_name, 'credit': credit}
        except:
            credit_validation = 1
        if credit_validation:
            sup_obj.status = False
            sup_obj.credit = '0.0'
            sup_obj.save()
            data = {
                'status': False,
                'type': 'credit',
                'text': "غير اعتباري",
                'name_sup': sup_obj.alias_name
            }
        driver.quit()
        return Response(data=data, status=status.HTTP_200_OK)


class Index(APIView):
    def __init__(self):
        self.worker = 0
    def selenium_task(self, worker, url):
        global redis_instance
        worker.get("https://google.com")
        try:
            info_driver = redis_instance.get(url)
            info_driver = json.loads(info_driver)
            worker.delete_all_cookies()
            cookies = info_driver['cookies']
            for cookie in cookies:
                worker.add_cookie(cookie)
            worker.get(info_driver['address'])
            self.worker = worker
        except:
            self.worker.quit()
            self.worker = 0
    def post(self, request):
        # rnd_name_drv = str(uuid4())
        form = first_validation(data=request.data)
        if form.is_valid():
            pass
        else:
            data = {
                'status': False,
                'message': form.errors
            }
            return Response(data=data, status=status.HTTP_200_OK)
        try:
            sup_object = Supplier.objects.get(name=request.data['url'])
            if sup_object.status == False:
                sup_object.credit = '0.0'
                sup_object.save()
                data = {
                    'status': False,
                    'message': 'عبور از کپچا انجام نشده است'
                }
                return Response(data=data, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Supplier Not Found!'}, status=status.HTTP_200_OK)

        worker = open_driver()
        t = threading.Thread(target=self.selenium_task, args=(worker, request.data['url']))
        t.start()   # Start threads
        t.join()    # Wait on threads to finish
        if self.worker == 0:
            data = {
                'status': False,
                'message': 'بارگذاری صفحه شکست خورد'
            }
            return Response(data=data, status=status.HTTP_200_OK)
        flySearch = Flights_Search(request.data, self.worker, sup_object)
        data = flySearch.Flight_Search()
        return Response(data=data, status=status.HTTP_200_OK)
class Flights_Search:
    def __init__(self, data, worker, sup_object):
        self.data = data
        self.worker = worker
        self.sup_object = sup_object
    def Flight_Search(self):
        driver = self.worker
        try:
            _dict = {'worker': driver}
            obj = operation(**_dict)
            credit = obj.readcredit()
            if credit == 'logout':
                create_error = 3 + 'e'
            price_credit = int(credit.replace(',', ''))
        except:
            driver.quit()
            data = {
                'status': False,
                'message': "اعتبار حساب و یا تاریخ اعتبار کش تمام شده است"
            }
            return data
        try:
            totalPrice = self.data['AdultPrice']
            priceChild = int(self.data['dplFlightChilds']) * self.data['ChildPrice']
            priceInfant = int(self.data['dplFlightInfants']) * self.data['InfantPrice']
            totalPrice = totalPrice + priceChild + priceInfant
        except:
            driver.quit()
            data = {
                'status': False,
                'message': "فرمت قیمت ها درست وارد نشده است"
            }
            return data
        #############
        if price_credit <= totalPrice:
            try:
                self.sup_object.credit = credit
                self.sup_object.save()
            except:
                pass
            driver.quit()
            data = {
                'status': False,
                'message': "اعتبار کافی نیست"
            }
            return data
        ################

        Path = 'OneWay'
        From = self.data['dplFrom']
        To = self.data['dplTo']
        fromdate = self.data['txtDepartureDate']
        loop_check = 0
        while True:
            if loop_check >= 4:
                driver.quit()
                data = {
                    'status': False,
                    'message': "مشکل در اتصال"
                }
                return data
            try:
                inputElement = Select(WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, r'//*[@id="dplFrom"]'))))
                inputElement.select_by_value(From)

                inputElement = Select(WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, r'//*[@id="dplReservationRouteType"]'))))
                inputElement.select_by_value(Path)
                sleep(1.5)      # TODO This line must be cleared (Low speed of internet)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, r'//*[@id="txtDepartureDate"]'))).clear()
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, r'//*[@id="txtDepartureDate"]'))).send_keys(fromdate)
                inputElement = Select(WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, r'//*[@id="dplTo"]'))))
                inputElement.select_by_value(To)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, r'//*[@id="btnSubmit"]'))).send_keys(Keys.ENTER)
                driver.find_element_by_id("btnSubmit")
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, r'//*[@id="btnReserve_Flight"]')))
                break
            except:
                loop_check += 1
                continue
        newReserve = FlightNewReserve(self.data, self.worker, self.sup_object)
        return newReserve.NewReserve()
class FlightNewReserve:
    def __init__(self, data, worker, sup_object):
        self.data = data
        self.worker = worker
        self.sup_object = sup_object
    def NewReserve(self):
        driver = self.worker
        NumberFlight = self.data["DepartureFlight"]
        sleep(2)
        try:
            AdultPrice = '{:2,.0f}'.format(self.data['AdultPrice'])
            js_string = '''
                checked = 'False';
                AdultPrice = "%s";
                function checking(){
                    var js_tbody = document.getElementsByClassName("tblSR")[0].querySelector("tbody");
                    var count_row = js_tbody.rows.length;
                    for (var r = 2; r < count_row; r++) {
                        var number_flight = document.querySelectorAll(`#tdMain > table.tblSR >
                         tbody > tr:nth-child(${r}) > td:nth-child(7)`)[0].textContent;
                        var status = document.querySelectorAll(`#tdMain > table.tblSR >
                         tbody > tr:nth-child(${r}) > td:nth-child(8)`)[0].textContent;
                        var departureTime = document.querySelectorAll(`#tdMain > table.tblSR >
                         tbody > tr:nth-child(${r}) > td:nth-child(4)`)[0].textContent;
                        number_flight = number_flight.trim()
                        status = status.trim()
                        departureTime = departureTime.trim()
                        if(number_flight.search("%s") != -1 && status == 'OnTime' && departureTime == "%s"){
                            var tr_counts = document.querySelectorAll(`#tdMain > table.tblSR >
                             tbody > tr:nth-child(${r}) > td:nth-child(1) > table.tblNB > tbody > tr`).length;
                            txt_adultprice = document.querySelectorAll(`#tdMain > table.tblSR > tbody >
                             tr:nth-child(${r}) > td:nth-child(1) > table.tblNB > tbody > tr:nth-child(1) >
                              td:nth-child(2) > span > label`)[0].textContent;
                            txt_adultprice = txt_adultprice.split(" ")[1];
                            if(tr_counts == 1 && txt_adultprice == AdultPrice) {
                                document.querySelectorAll(`#tdMain > table.tblSR >
                                 tbody > tr:nth-child(${r}) > td:nth-child(1) > table.tblNB > tbody > tr:nth-child(1) >
                                  td:nth-child(2) > span > input[type=radio]`)[0].checked = true;
                                checked = 'True';
                                return true;
                            }else {
                                for(var j = 1; j <= tr_counts; j++){
                                    var txt_adultprice = document.querySelectorAll(`#tdMain > table.tblSR > tbody >
                                     tr:nth-child(${r}) > td:nth-child(1) > table.tblNB > tbody > tr:nth-child(${j}) >
                                      td:nth-child(2) > span > label`)[0].textContent;
                                    txt_adultprice = txt_adultprice.split(" ")[1];
                                    if(txt_adultprice == AdultPrice){
                                        document.querySelectorAll(`#tdMain > table.tblSR > tbody > tr:nth-child(${r}) >
                                         td:nth-child(1) > table.tblNB >tbody > tr:nth-child(${j}) > td:nth-child(2) >
                                          span > input[type=radio]`)[0].checked = true;
                                        checked = 'True'
                                        return true;
                                    }
                                }
                            }
                        }
                    }
                }
                checking();
                scrollTo(0, 1600)
                return checked;
            '''% (AdultPrice, NumberFlight, self.data['cleanDepartureTime'])

            confirm = WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script(js_string)
            )
            if confirm == 'False':
                driver.quit()
                data = {
                    'status': False,
                    'message': "پرواز انتخابی یافت نشد"
                }
                return data
        except:
            driver.quit()
            data = {
                'status': False,
                'message': "کدهای جاوااسکریپت سمت سرور درست عمل نکرد"
            }
            return data
        dplFlightAdults = str(self.data['dplFlightAdults'])
        inputElement = Select(driver.find_element_by_id("dplFlightAdults"))
        inputElement.select_by_value(dplFlightAdults)
        dplFlightChilds = str(self.data['dplFlightChilds'])
        inputElement = Select(driver.find_element_by_id("dplFlightChilds"))
        inputElement.select_by_value(dplFlightChilds)
        dplFlightInfants = str(self.data['dplFlightInfants'])
        inputElement = Select(driver.find_element_by_id("dplFlightInfants"))
        inputElement.select_by_value(dplFlightInfants)
        preReserve = FlightPreReserve(self.data, self.worker)
        return preReserve.PreReserve()
class FlightPreReserve:
    def __init__(self, data, worker):
        self.data = data
        self.worker = worker
    def PreReserve(self):
        driver = self.worker
        try:
            driver.find_element_by_id("btnReserve_Flight").send_keys(Keys.ENTER)
            sleep(0.3)
            text_error = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
                By.ID, 'Module_Error1__tdError'))).text
            # text_error = driver.find_element_by_id("Module_Error1__tdError").text
            driver.quit()
            data = {
                'status': False,
                'message': text_error
            }
            return data
        except:
            i = 0
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl00_txtPassengerFirstName"]'))).clear()
        except:
            driver.quit()
            data = {
                'status': False,
                'message': "مشکل در اتصال 2"
            }
            return data
        passengers = self.data['passengers']
        len_passengers = int(self.data['dplFlightAdults']) + int(self.data['dplFlightChilds']) + int(self.data['dplFlightInfants'])
        try:
            for passenger in range(len_passengers):
                j = str("%02d"% i)
                if passengers[passenger]['dplGender_ctl'] == 0:
                    dplGender_ctl = "1"
                else:
                    dplGender_ctl = "2"

                inputElement = Select(WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_dplGender"]'%j))))
                inputElement.select_by_value(dplGender_ctl)
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_txtPassengerFirstName"]'% j))
                ).send_keys(passengers[passenger]['txtPassengerFirstName'])
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_txtPassengerLastName"]'% j))
                ).send_keys(passengers[passenger]['txtPassengerLastName'])
                try:
                    inputElement = Select(WebDriverWait(driver, 1).until(EC.element_to_be_clickable(
                        (By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_dplTravelDocumentType"]'% j))))
                    inputElement.select_by_value(passengers[passenger]['dplTravelDocumentType'])
                    sleep(0.5)
                    inputElement = Select(WebDriverWait(driver, 1).until(EC.element_to_be_clickable(
                        (By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_dplNationality_ID"]'% j))))
                    inputElement.select_by_value(passengers[passenger]['dplNationality_ID'])
                    WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                        By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_txtPassenger_PassportNo"]'% j))
                    ).send_keys(passengers[passenger]['txtPassenger_PassportNo'])
                    inputElement = Select(WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                        By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_dplPassenger_BirthDay_Day"]'% j))))
                    inputElement.select_by_value(passengers[passenger]['BirthDay_Day'])
                    inputElement = Select(WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                        By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_dplPassenger_BirthDay_Month"]'% j))))
                    inputElement.select_by_value(passengers[passenger]['BirthDay_Month'])
                    inputElement = Select(WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                        By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_dplPassenger_BirthDay_Year"]'% j))))
                    inputElement.select_by_value(passengers[passenger]['BirthDay_Year'])
                except:
                    pass
                if passengers[passenger]['dplTravelDocumentType'] == "11":
                    try:
                        inputElement = Select(WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                            By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_dplPassenger_PassportExpiryDate_"]'% j))))
                        inputElement.select_by_value(passengers[passenger]['PassportExpiryDate_Day'])
                        inputElement = Select(WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                            By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_dplPassenger_PassportExpiryDate_Month"]'% j))))
                        inputElement.select_by_value(passengers[passenger]['PassportExpiryDate_Month'])
                        inputElement = Select(WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                            By.XPATH, r'//*[@id="_Module_PassengerInformation_rptPassengers_ctl%s_dplPassenger_PassportExpiryDate_Year"]'% j))))
                        inputElement.select_by_value(passengers[passenger]['PassportExpiryDate_Year'])
                    except:
                        pass
                i = i + 1

            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="txtPhone"]'))).send_keys(self.data['txtPhone'])
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="txtReservation_Email"]'))).send_keys(self.data['txtReservation_Email'])
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="txtAddress"]'))).send_keys(self.data['txtAddress'])
            WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="txtRemark"]'))).send_keys(self.data['txtRemark'])
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="dplMobileCountry"]'))).send_keys(self.data['dplMobileCountry'])
        except:
            driver.quit()
            data = {
                'status': False,
                'message': "درخواست اشتباه است"
            }
            return data

        resv = Flight_Reserve(self.data, self.worker)
        return resv.Reserve()
class Flight_Reserve:
    def __init__(self, data, worker):
        self.data = data
        self.worker = worker
    def Reserve(self):
        driver = self.worker
        # for Test ~~~~~~~~~~~~~~~~~~~
        # global path_captcha
        # driver.save_screenshot(path_captcha + "/select_flight.png")
        # sleep(1)
        # driver.quit()
        # data = {
        #     'status': True,
        #     'message': 'last step'
        # }
        # return data
        # for Test ^^^^^^^^^^^^^^^^^^^
        try:
            # driver.find_element_by_id("btnReserve").send_keys(Keys.ENTER)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, r'//*[@id="btnReserve"]'))).send_keys(Keys.ENTER)
            refrence = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="Form1"]/center/table[1]/tbody/tr/td/input[1]'))).get_attribute("value")
            voucher = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="Form1"]/center/table[1]/tbody/tr/td/input[2]'))).get_attribute("value")
            data = {
                'status': True,
                'refrence': refrence,
                'voucher': voucher
            }
        except:
            data = {
                'status': False,
                'message': "رزرو با شکست روبرو شد"
            }
        driver.quit()
        return data


class CheapFlight(APIView):
    def get(self, request):
        try:
            page = requests.get("https://flight.mdsafar.ir/")
            soup = BeautifulSoup(page.content, 'html.parser')
            # soup.prettify()
            table = soup.find(id="dtlOrigin")
            rows = table.findAll('tr')
            del rows[0]
            list_pids = []
            for row in rows:
                cols = row.findAll('td')
                for col in cols:
                    if len(col.contents) > 0:
                        to = []
                        divPid = col.select('div')[0]
                        divPid = divPid.select('div')[1]
                        rows_PID = divPid.select('div')
                        for rp in rows_PID:
                            Pid = {}
                            Link = rp.select('.cheapPriceLink')[0]
                            data = Link["href"].split("?")[1]
                            data = data.split("&")
                            Origin = data[0].split("=")[1]
                            Destination = data[1].split("=")[1]
                            # Destination = Link.select('span')[0].text
                            # Destination = " ".join(Destination.split())
                            Price = Link.select('span')[1].text
                            Price = " ".join(Price.split())
                            Pid = {
                                "Link": Link["href"],
                                "Destination" : Destination,
                                "Price": Price
                            }
                            to.append(Pid)
                        list_fly = {'from': Origin, 'to': to}
                        list_pids.append(list_fly)
            data = {'status': True,'value': list_pids}
        except:
            data = {'status': False,'value': 'Error Server'}
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request):
        clr_green = "#079c17" #color cheap price
        loop_check = 0
        while True:
            if loop_check >= 4:
                data = {'status': False,'value': 'Faild in Connect'}
                return Response(data=data, status=status.HTTP_200_OK)
            try:
                req = request.data
                url_fly = req['url_flight']
                url_fly = "https://flight.mdsafar.ir/Systems/%s"% url_fly
                page = requests.get(url_fly)
                soup = BeautifulSoup(page.content, 'html.parser')
                rows = soup.findAll(class_="cheapPriceLink")
                list_fly = []
                for row in rows:
                    stylespan = row.select('span')[1]["style"]
                    object = {
                        "day": row.select('span')[0].text,
                        "price": row.select('span')[1].text,
                        'date': row['href'].split("|")[2],
                        'cheap': False
                    }
                    if stylespan.find(clr_green) != -1:
                        object.update({"cheap": True})
                    list_fly.append(object)
                data = {'status': True, 'value': list_fly}
                # return Response(list_fly, status=status.HTTP_200_OK)
            except:
                loop_check += 1
                continue
            return Response(data=data, status=status.HTTP_200_OK)
        # return Response(data=json.dumps(data), status=status.HTTP_200_OK)


# Search only [ site: sepehr360.ir ]
class auto_search_sepehr:
    def __init__(self):
        self.res = []
        self.list_flight = ''
        print("start")
    def thread_task(self, partline, res, list_flight):
        ## datas['date'] = "1399/02/24"
        # datas['date'] = "2020-09-23" > "year-day-month"
        # datas['seatCount'] =>> integer
        try:
            url = 'https://api.sepehr360.ir/fa/FlightAvailability/Api/B2bOnewayFlightApi/Search'
            date = '1399/08/06'
            sup_name = list(Supplier.objects.filter(status=False).values_list('name', flat=True))
            seat_count = "9"
            http = urllib3.PoolManager()
            count = 0
            while True:
                data = json.dumps({
                    "commonClientServerData": "",
                    "deviceToken": "",
                    "sessionId": "",
                    "commonClientServerDataVersion": "",
                    "intervalDays": 0, "curencyType": "IRR",
                    "flightNumber": "", "cabinFilterList": [],
                    "dayPartsFilterList": [], "airLinesFilterList": [],
                    "daysFilterList": [], "sortOrder": 1, "pageSize": 200,
                    "pageNumber": count, "isMobileWeb": False, "originAirportIataCode": partline[0],
                    "destinationAirportIataCode": partline[1], "departureDate": date
                })
                r = http.request('POST', url, body=data, headers={'Content-Type': 'application/json', 'User-Agent': 'API'})
                pastebin_url = json.loads(r.data.decode('utf-8'))
                for fly in pastebin_url['flightHeaderList']:
                    # if 'listTaminKonandeganSahmiyeShenavar' not in fly and fly['supplierNameFa'] in sup_name and fly['seatCount'] >= seat_count:
                    if 'listTaminKonandeganSahmiyeShenavar' not in fly:
                        res.append(fly)
                count += 1
                if pastebin_url['flightHeaderList'] == [] or count > 7:
                    break
            self.res = res
            self.list_flight = {
                "value": self.res,
                "airlinesMinPriceList": pastebin_url['airlinesMinPriceList']
            }
        except:
            self.list_flight = []
        return self.list_flight
        # return Response({'value': res}, status=status.HTTP_200_OK)
        # return Response(res, status=status.HTTP_200_OK)
        # return Response(data=json.dumps(res), status=status.HTTP_200_OK)
    def autoSearch(self):
        with open('sepehr/routes.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                partline = line.strip().split(",")
                print(partline)
                t1 = threading.Thread(target=self.thread_task, args=(partline, self.res, self.list_flight))
                t1.start()
            t1.join()
        return self.list_flight
# Search only [ site: sepehr360.ir ]
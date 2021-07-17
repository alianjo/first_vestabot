from urllib.parse import urlparse
from django.core.validators import URLValidator
# from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from ravis.models import Supplier
from ravis.serializers import first_validation
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
from PIL import Image
from io import BytesIO
from time import sleep
from uuid import uuid4
import threading, os, json, redis


path_captcha = r'/home/vesta/projects/vestabot/.venv/lib/python3.8/site-packages/django/contrib/admin/static/admin/captcha'
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)

def open_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=chrome_options)
    driver.set_window_size(1920, 1080)
    return driver

def default_argument(string = 'default'):
    return string

def threaded(fn):
    def wrapper(*args, **kwargs):
        lists = default_argument(args)
        dict = default_argument(kwargs)
        thread = threading.Thread(target=fn, args=lists, kwargs=dict)
        thread.start()
        return thread
    return wrapper

class operation(object):
    def __init__(self, *args, **kwargs):
        self.lists = default_argument(args)
        self.dict = default_argument(kwargs)

    def readcredit(self):
        driver = self.dict['worker']
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="btnShopping"]'))).click()
            credit = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="shopping-article"]/div[3]/table/thead/tr/th[3]//span[@class="badge"]'))).text
            return credit
        except:
            return 'logout'

    def req_captcha(self):
        global path_captcha, selenium_worker
        driver = self.dict['worker']
        status_arrive = self.dict['status_arrive']
        sup_obj = self.dict['sup_obj']
        loop_check = 0
        while True:
            if loop_check >= 4:
                driver.quit()
                data = {
                    'status': False,
                    'message': "شکست در اتصال"
                }
                return data
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, r'//*[@id="cboVorod"]')))
                break
            except:
                driver.get('https://' + sup_obj.address)
                loop_check += 1
                continue
        # -----------------------------LOGIN----------------------------------
        # AgentLogin # PublicLogin
        _txtUsername = sup_obj.username
        _txtPassword = sup_obj.password
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
                    inputElement = Select(WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, r'//*[@id="cboVorod"]'))))
                    inputElement.select_by_value('2')
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                        By.XPATH, r'//*[@id="txtUserName"]'))).send_keys(_txtUsername)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                        By.XPATH, r'//*[@id="txtPassword"]'))).send_keys(_txtPassword)
                break
            except:
                loop_check += 1
                continue
        # -----------------------------LOGIN----------------------------------
        # driver.execute_script('scroll(0, 5000);')
        name_tab = str(uuid4())
        try:
            driver.execute_script('document.querySelector("#imgChange").remove();'
                                  'document.getElementById("imgCaptcha").style.border="none";')
            element = driver.find_element_by_xpath('//*[@id="imgCaptcha"]')
            location = element.location
            size = element.size
            print("size: %s ----- location: %s"% (size, location))
            png = driver.get_screenshot_as_png()
            img = Image.open(BytesIO(png))
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            img = img.crop((left, top, right, bottom))
            print("size: %s ----- location: %s ----- img: %s "% (size, location, img))
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

    def reports_ticket(self):
        driver = self.dict['worker']
        req = self.dict['request']

        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="li-emk"]/a'))).click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="li-emk"]/ul/li[4]/a'))).click()
            sleep(2)

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, r'//*[@id="ContentArticle_txtDate1"]'))).clear()
        except:
            data = {
                'status': False,
                'message': 'مشکل در بارگذاری صفحه'
            }
            driver.quit()
            return data
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, r'//*[@id="ContentArticle_txtDate1"]'))).send_keys(req['txtDepartureDate'])
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, r'//*[@id="ContentArticle_txtDate2"]'))).clear()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, r'//*[@id="ContentArticle_txtDate2"]'))).send_keys(req['txtDepartureDate'])

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_cmdView"]'))).click()

        return data



class Index(APIView):
    worker = 0
    refrence = '0'

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
            worker.get('https://' + info_driver['address'])
            self.worker = worker
        except:
            self.worker = 0

    def operation(self, request):
        global path_captcha
        req = request.data
        driver = self.worker

        time_flight = req['cleanDepartureTime']
        num_flight = req['DepartureFlight']
        price = req['AdultPrice']
        ChildPrice = req['ChildPrice']
        InfantPrice = req['InfantPrice']
        total_price = price + ChildPrice + InfantPrice
        price_flight = '{:2,.0f}'.format(price)
        total_price = '{:2,.0f}'.format(total_price)
        count_passengers = int(ADL) + int(CHL) + int(INF)
        passengers = req['passengers']

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="li_flight"]/a'))).click()

        inputElement = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_cboSrc"]'))))
        inputElement.select_by_value(req['dplFrom'])
        inputElement = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ccbboo"]'))))
        inputElement.select_by_value(req['dplTo'])
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_txtDate1"]'))).clear()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_txtDate1"]'))).send_keys(req['txtDepartureDate'])
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_txtDate2"]'))).clear()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_txtDate2"]'))).send_keys(req['txtDepartureDate'])
        inputElement = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_ddlRouteType"]'))))
        inputElement.select_by_value('1')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_cmdViewFlight"]'))).click()

        sleep(1)
        if driver.title == 'بروز خطا سیستمی':
            data = {
                'status': False,
                'message': 'بروز خطا سیستمی'
            }
            driver.quit()
            return data
        _dict = {'worker': driver}
        obj = operation(**_dict)
        credit = obj.readcredit()
        if total_price != credit:
            data = {
                'status': False,
                'message': 'اعتبار کافی نیست'
            }
            driver.quit()
            return data


        inputElement = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_cboNumADL"]'))))
        inputElement.select_by_value(str(req['dplFlightAdults']))
        inputElement = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_cboNumCHD"]'))))
        inputElement.select_by_value(str(req['dplFlightChilds']))
        inputElement = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_cboNumINF"]'))))
        inputElement.select_by_value(str(req['dplFlightInfants']))

        count_flight = len(driver.find_elements_by_xpath('//*[@id="flight"]/div/div/table/tbody')) + 1

        for count in range(1, count_flight):
            time_fly = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="flight"]/div/div/table/tbody[%s]/tr/td[3]' % count))).text
            number_fly = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="flight"]/div/div/table/tbody[%s]/tr/td[4]/div[3]' % count))).text
            price_fly = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="flight"]/div/div/table/tbody[%s]/tr/td[5]//span[@class="price"]' % count))).text
            capacity = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="flight"]/div/div/table/tbody[%s]/tr/td[6]/span[2]/span[last()]' % count))).text
            capacity = int(capacity)
            if time_fly == time_flight and number_fly.find(num_flight) != -1 and price_fly == price_flight and capacity >= count_passengers:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                    By.XPATH,
                    r'//*[@id="flight"]/div/div/table/tbody[%s]/tr/td[6]//input[@class="radio-inline"]' % count))).click()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                    By.XPATH, r'//*[@id="cmdReserve"]'))).click()
                sleep(0.8)
                break

        count = 1
        for passenger in passengers:
            if passenger['dplGender_ctl'] == '0':
                gender = '2'
            else:
                gender = '1'
            inputElement = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="tblListNamFr"]/tbody/tr[%s]/td[2]//select[@id="cboSex"]' % count))))
            inputElement.select_by_value(gender)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="tblListNamFr"]/tbody/tr[%s]/td[3]/input' % count))).send_keys(
                passenger['txtPassengerFirstName'])
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="tblListNamFr"]/tbody/tr[%s]/td[4]/input' % count))).send_keys(
                passenger['txtPassengerLastName'])
            js_string = '''
                count = %s;
                passenger_type = %s;
                document.querySelector(`#tblListNamFr > tbody > tr:nth-child(${count}) > td.td-group > div > div > button`).click();
                if(passenger_type == '1'){
                    document.querySelector(`#tblListNamFr > tbody > tr:nth-child(${count}) > td.td-group > div > div > ul > li.li_melicod > a`).click();
                }
                else{
                    document.querySelector(`#tblListNamFr > tbody > tr:nth-child(${count}) > td.td-group > div > div > ul > li.li_pass > a`).click();
                }
            ''' % (count, passenger['dplTravelDocumentType'])
            driver.execute_script(js_string)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.XPATH, r'//*[@id="tblListNamFr"]/tbody/tr[%s]/td[5]/div/input[1]' % count))).send_keys(
                passenger['dplNationality_ID'])
            count += 1

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_txtMoblie"]'))).send_keys(req['txtPhone'])
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, r'//*[@id="ContentArticle_txtTelNo"]'))).send_keys(req['txtReservation_Email'])
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
        #     By.XPATH, r'//*[@id="ContentArticle_btnFinalSave"]'))).click()

        _dict = {'request': req, 'worker': worker}
        obj = operation(**_dict)
        data = obj.reports_ticket()
        driver.quit()
        return data

    def post(self, request):

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
            sup_object = Supplier.objects.get(name=request.data['name_company'])
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
        t = threading.Thread(target=self.selenium_task, args=(worker, sup_object.address))
        t.start()   # Start threads
        t.join()    # Wait on threads to finish
        if self.worker == 0:
            data = {
                'status': False,
                'message': 'بارگذاری صفحه شکست خورد'
            }
            worker.quit()
            return Response(data=data, status=status.HTTP_200_OK)
        data = self.operation(request)
        return Response(data=data, status=status.HTTP_200_OK)


class AdminTemplate(object):
    def __init__(self, queryset):
        self.queryset = queryset
    def disableSup(self):
        global redis_instance
        list_error = []
        try:
            objects = self.queryset.filter(status=True)
        except ObjectDoesNotExist:
            data = {
                'status': False,
                'message': 'مشکل در دیتابیس'
            }
            return data
        try:
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
                    worker.get('https://' + info_driver['address'])
                    WebDriverWait(worker, 20).until(EC.element_to_be_clickable((
                        By.XPATH, r'//*[@id="btnExit"]'))).click()
                    worker.quit()
                    self.queryset.filter(address=obj.address).update(status=False, credit='0.0')
                except:
                    list_error.append(obj.name)
                    # self.queryset.filter(address=obj.address).update(status=False, credit='Error')
                    if len(list_error) > 5:
                        data = {
                            'status': False,
                            'message': ' افزایش مشکل در ارتباط با تامین کننده ها' + '(' + list_error + ')'
                        }
                        return data
        except:
            data = {
                'status': False,
                'message': 'خطای غیرفعال کردن, درصورت تکرار با ادمین تماس برقرار شود'
            }
            return data
        data = {
            'status': True,
            'message': 'عملیات کامل شد'
        }
        return data

    def reloadCreditSup(self):
        global redis_instance
        list_error = []
        try:
            objects = self.queryset.filter(status=True)
        except ObjectDoesNotExist:
            data = {
                'status': False,
                'message': 'مشکل در دیتابیس'
            }
            return data
        try:
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
                    worker.get('https://' + info_driver['address'])
                    _dict = {'worker': worker}
                    object = operation(**_dict)
                    credit = object.readcredit()
                    objects.filter(address=obj.address).update(credit=credit)
                except:
                    list_error.append(obj.name)
                    # self.queryset.filter(address=obj.address).update(status=False, credit='Error')
                    if len(list_error) > 5:
                        data = {
                            'status': False,
                            'message': ' افزایش مشکل در ارتباط با تامین کننده ها' + '(' + list_error + ')'
                        }
                        return data
        except:
            data = {
                'status': False,
                'message': 'خطای خواندن اعتبار, درصورت تکرار با ادمین تماس برقرار شود'
            }
            return data
        data = {
            'status': True,
            'message': 'عملیات کامل شد'
        }
        return data



class GetCaptcha(APIView):
    worker = 0
    refrence = '0'

    def get(self, request):
        # Crop Captcha And Sending To Response
        try:
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
                By.XPATH, r'//*[@id="txtCaptcha"]'))).send_keys(request.GET['txtCaptchaNumber'])
            driver.find_element_by_xpath('//*[@id="cmdAzhansLogin"]').click()
            sleep(0.5)
            driver.find_element_by_id("ContentArticle_PanelMessage")
        except:
            text_error = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
                By.ID, 'lblMessage1'))).text
            driver.get(sup_obj.address)
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
            _dict = {'worker': driver}
            obj = operation(**_dict)
            credit = obj.readcredit()
            sup_obj.status = True
            sup_obj.credit = credit
            sup_obj.save()
            cookies = driver.get_cookies()
            info_driver = {
                'cookies': cookies,
                'address': sup_obj.address
            }
            driver.quit()
            redis_instance.set(sup_obj.address, json.dumps(info_driver))
            data = {'status': True, 'name_sup': sup_obj.alias_name, 'credit': credit}
        except:
            driver.quit()
            sup_obj.status = False
            sup_obj.credit = '0.0'
            sup_obj.save()
            data = {
                'status': False,
                'type': 'credit',
                'text': "غير اعتباري",
                'name_sup': sup_obj.alias_name
            }
        return Response(data=data, status=status.HTTP_200_OK)

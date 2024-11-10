import pause as pause
import datetime
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import wait
from selenium.webdriver.support.wait import WebDriverWait
from playsound import playsound
from selenium import webdriver
import time
import configparser
import threading
import CODE
import function

class Macro():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')

        self.__start_year = int(self.config['program']['year'])
        self.__start_month = int(self.config['program']['month'])
        self.__start_day = int(self.config['program']['day'])
        self.__start_hour = int(self.config['program']['hour'])
        self.__start_minute = int(self.config['program']['minute'])

        print(self.__start_year, self.__start_month, self.__start_day, self.__start_hour, self.__start_minute)

        self.__id = self.config['loginInfo']['id']
        self.__pw = self.config['loginInfo']['pw']
        self.__bookDate = self.config['bookInfo']['bookDate']
        self.__bookTime = self.config['bookInfo']['bookTime']
        self.__goodsCode = self.config['bookInfo']['goodsCode']

        self.__seatOrder = self.config['bookInfo']['order']  # Row or Area
        self.__colOrder = self.config['bookInfo']['colOrder']  # Start Column, End Column
        self.__auto_certification = self.config['function']['auto_certification']
        self.__special_area = self.config['function']['special_area']
        self.__sound = self.config['function']['sound']
        self.__seat_jump = self.config['function']['seat_jump']
        self.__seat_jump_count = int(self.config['function']['seat_jump_count'])
        self.__seat_jump_special_repeat = self.config['function']['seat_jump_special_repeat']
        self.__seat_jump_special_repeat_count = int(self.config['function']['seat_jump_special_repeat_count'])

        # self.driver = webdriver.Chrome("./chromedriver_win32/chromedriver")
        # self.driver = webdriver.Chrome("./chromedriver_win32_v112/chromedriver")
        self.driver = webdriver.Chrome()

        self.wait = WebDriverWait(self.driver, 600)

        self.end = False
        self.stop = False
        self.part = "login"
        self.main_thread = threading.Thread(target=self.run)
        self.main_thread.start()

        self.key_reading = threading.Thread(target=self.key_interrupt)
        self.key_reading.start()

    def key_interrupt(self):
        while not self.end:
            self.key = input()
            if self.key == 'stop' or self.key == 's':
                self.stop = True
                print(f'self.part:{self.part} stop')
            elif self.key == 'go':
                print(f'self.part:{self.part} go')
                self.stop = False
            elif self.key == 'end':
                self.part = ""
                self.stop = False
                self.end = True
                break
            elif self.key == 'setup':
                print(f'please enter the part you want:')
                setup_part = input()
                self.part = setup_part
                print(f'setup success, current part:{self.part}\nplease enter go.')
            elif self.key == 'order':
                print(f'please enter order ex)A,B,C :')
                change_order = input()
                self.__seatOrder = change_order
                self.__special_area = 'Y'
                print(f'config order change success. {self.__seatOrder}')
            elif self.key == 'colorder':
                print(f'please enter col order ex)11,29 :')
                change_col_order = input()
                self.__colOrder = change_col_order
                self.__special_area = 'Y'
                print(f'config order change success. {self.__colOrder}')
            elif self.key == 'order_cancel':
                self.__seatOrder = ''
                self.__colOrder = ''
                self.__special_area = 'N'

        print("key_interrupt exit.")

    def jump_count_update(self):
        if function.seat_jump_special_repeat == 'Y' and function.seat_jump_special_repeat_count > 0:
            function.seat_jump_special_repeat_count -= 1
            print(f'function.seat_jump_special_repeat_count: {function.seat_jump_special_repeat_count}')
            if function.seat_jump_special_repeat_count < 1:
                function.seat_jump_special_repeat = 'N'
                function.seat_jump = 'N'
                function.seat_jump_count = 0
                print('점프 끝')

    def run(self):
        while True:
            if self.stop == True:
                continue
            try:
                if self.stop == False and self.part == "login":
                    # 로그인
                    function.login(self.driver, self.__id, self.__pw)
                    self.part = "time_wait"

                if self.stop == False and self.part == "time_wait":
                    # 예매시간까지 대기
                    pause.until(datetime.datetime(self.__start_year, self.__start_month, self.__start_day, self.__start_hour, self.__start_minute, 00))
                    self.part = "show_booksite"

                if self.stop == False and self.part == "show_booksite":
                    # 예매사이트 띄우기
                    self.driver.get(f"https://tickets.interpark.com/goods/{self.__goodsCode}")
                    self.wait.until(EC.url_to_be(f"https://tickets.interpark.com/goods/{self.__goodsCode}"))
                    self.part = "wait_clickable_book"

                if self.stop == False and self.part == "wait_clickable_book":
                    # self.driver.implicitly_wait(10)
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="productSide"]/div/div[2]/a[2]')))
                    self.wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '#productSide > div > div.sideBtnWrap > a.sideBtn.is-primary[data-check="false"]')))
                    self.part = "popup_check"

                if self.stop == False and self.part == "popup_check":
                    # 팝업 체크
                    function.first_popup_check(self.driver)
                    self.part = "click_book"

                if self.stop == False and self.part == "click_book":
                    # 원하는 날짜로 선택 후 예매하기 버튼 클릭
                    function.click_book(self.driver, self.__bookDate, self.__bookTime)
                    self.part = "wait_book_popup"

                if self.stop == False and self.part == "wait_book_popup":
                    # 예매창 뜰 때까지 대기
                    WebDriverWait(self.driver, 600).until(EC.number_of_windows_to_be(2))
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    self.part = "seat_frame_move"

                if self.stop == False and self.part == "seat_frame_move":
                    WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.ID, 'ifrmSeat')))
                    # 예매창으로 프레임 전환
                    iframe = self.driver.find_element_by_id('ifrmSeat')
                    self.driver.switch_to.frame(iframe)
                    self.part = "certification"

                if self.stop == False and self.part == "certification":
                    # 보안문자인증
                    if self.__auto_certification == "N":
                        self.wait.until(EC.invisibility_of_element_located((By.ID, "divRecaptcha")))
                    else:
                        function.certification(self.driver)
                    self.part = "set_seat_jump"

                # 좌석 점프 셋팅
                if self.stop == False and self.part == "set_seat_jump":
                    if self.__seat_jump == 'Y' and self.__seat_jump_count > 0:
                        function.seat_jump = 'Y'
                        function.seat_jump_count = self.__seat_jump_count
                        if self.__seat_jump_special_repeat == 'Y' and self.__seat_jump_special_repeat_count > 0:
                            function.seat_jump_special_repeat = 'Y'
                            function.seat_jump_special_repeat_count = self.__seat_jump_special_repeat_count
                        print("점프셋")

                    self.part = "booking"

                # 예매
                while self.stop == False and self.part == "booking":
                    config_special_area = []
                    col_special_area = []
                    if self.__seatOrder != "" and self.__special_area == "Y":
                        config_special_area = self.__seatOrder.split(",")
                    function.print_debug(config_special_area)
                    if self.__colOrder != "" and self.__special_area == "Y":
                        col_special_area = self.__colOrder.split(",")
                    function.print_debug(col_special_area)
                    res = function.booking(self.driver, config_special_area, self.__seatOrder, col_special_area)
                    function.print_debug(f"res: {res}")
                    if res == CODE.SUCCESS:
                        self.part = "catch"
                        self.jump_count_update()
                        break
                    elif res == CODE.CONFLICT:
                        self.jump_count_update()
                    elif res == CODE.ERROR:
                        self.part = "certification"
                        break

                    self.driver.switch_to.default_content()
                    iframe = self.driver.find_element_by_id('ifrmSeat')
                    self.driver.switch_to.frame(iframe)
                    self.driver.find_element_by_css_selector('a[onclick="fnRefresh();"]').click()
                    time.sleep(0)

                if self.stop == False and self.part == "catch":
                    print("끝!!!")
                    try:
                        if self.__sound == "Y":
                            playsound("catch.mp3")
                    except:
                        pass

            except Exception as e:
                print(f'current part : {self.part}\n{traceback.format_exc()}')
                print('If you continue program, please enter go:')
                self.stop = True

            if self.part == 'catch':
                print('current part is catch. If you want to continue booking,\n'
                      'please click back button and enter setup and part(booking),\n'
                      'then enter go.')
                self.stop = True
                self.part = ""

            if self.end == True:
                break

        print("The End")

if __name__ == "__main__":
    import Macro
    app = Macro.Macro()
import datetime

from selenium import webdriver
import time
import threading
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from playsound import playsound
import CODE
import function
import configparser
import pause
import traceback
import os

class Macro():
    def __init__(self):
        # self.driver = webdriver.Chrome("./chromedriver_win32/chromedriver") #v110
        self.driver = webdriver.Chrome()

        self.wait = WebDriverWait(self.driver, 180)
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')

        self.__id = self.config['loginInfo']['id']
        self.__pw = self.config['loginInfo']['pw']
        self.__prodId = self.config['bookInfo']['prodId']
        self.__seatOrder = self.config['bookInfo']['order']
        self.__seatGrade = self.config['bookInfo']['grade']
        self.__start_year = int(self.config['program']['year'])
        self.__start_month = int(self.config['program']['month'])
        self.__start_day = int(self.config['program']['day'])
        self.__start_hour = int(self.config['program']['hour'])
        self.__start_minute = int(self.config['program']['minute'])
        self.__auto_certification = self.config['function']['auto_certification']
        self.__special_area = self.config['function']['special_area']
        self.__sound = self.config['function']['sound']
        self.__seat_jump = self.config['function']['seat_jump']
        self.__seat_jump_count = int(self.config['function']['seat_jump_count'])
        self.__seat_jump_special_repeat = self.config['function']['seat_jump_special_repeat']
        self.__seat_jump_special_repeat_count = int(self.config['function']['seat_jump_special_repeat_count'])
        self.__skip_date_click = self.config['function']['skip_date_click']

        self.end = False
        self.stop = False
        self.part = "login"
        self.skip_select_date = False

        self.img_folder_path = './images'
        self.make_image_save_folder()

        self.main_thread = threading.Thread(target=self.run)
        self.main_thread.start()

        self.key_reading = threading.Thread(target=self.key_interrupt)
        self.key_reading.start()

    def make_image_save_folder(self):
        if not os.path.exists(self.img_folder_path):
            os.makedirs(self.img_folder_path)

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
            elif self.key == 'order_cancel':
                self.__seatOrder = ''
                # self.__special_area = 'N'
            elif self.key == 'grade':
                print(f'please enter grade ex)S석,A석,B석 :')
                change_grade = input()
                self.__seatGrade = change_grade
                self.__special_area = 'Y'
                print(f'config grade change success. {self.__seatGrade}')
            elif self.key == 'grade_cancel':
                self.__seatGrade = ''
                # self.__special_area = 'N'
                print(f'grade cancel!!')
            elif self.key == 'skip_select_date':
                self.__skip_date_click = True
                print('skip_select_date set ok.')
            elif self.key == 'skip_select_date_cancel':
                self.__skip_date_click = False
                print('skip_select_date cancel set ok.')

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
                    # 예매 사이트 접근
                    self.driver.get(f'https://ticket.melon.com/performance/index.htm?prodId={self.__prodId}')
                    self.part = "time_wait"

                if self.stop == False and self.part == "time_wait":
                    # 예매 시간까지 대기
                    if self.__skip_date_click == 'Y':
                        WebDriverWait(self.driver, 600).until(EC.new_window_is_opened(self.driver.window_handles))
                        self.part = "change_window"
                    else:
                        # 예매 시간까지 대기
                        pause.until(datetime.datetime(self.__start_year, self.__start_month, self.__start_day, self.__start_hour, self.__start_minute, 00))
                        self.part = "popup_check"

                if self.stop == False and self.part == "popup_check":
                    function.check_alert(self.driver)
                    WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.ID, 'list_date')))
                    self.part = "click_book"

                if self.stop == False and self.part == "click_book":
                    if self.__skip_date_click == 'N':
                        # 날짜선택후 티켓창 오픈
                        cnt = 0
                        ret = function.select_date(self.driver, self.config)
                        if ret == False:
                            while cnt < 3:
                                cnt += 1
                                ret = function.select_date(self.driver, self.config)
                                if ret == True:
                                    break
                    WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
                    self.part = "change_window"

                if self.stop == False and self.part == "change_window":
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    self.part = "certification"

                if self.stop == False and self.part == "certification":
                    # 보안문자인증
                    if self.__auto_certification == "N":
                        try:
                            label = self.driver.find_element_by_id('label-for-captcha')
                            self.driver.execute_script("arguments[0].focus();", label)
                        except Exception as e:
                            # 인증이 없는케이스 고려해서 반복안하고 바로 넘어감
                            print(f"certification box focus error:{e}")
                                
                        self.wait.until(EC.invisibility_of_element_located((By.ID, "certification")))
                    else:
                        function.certification(self.driver, self.img_folder_path)
                    self.part = "seat_frame_move"

                if self.stop == False and self.part == "seat_frame_move":
                    # 좌석 선택
                    iframe = self.driver.find_element(By.TAG_NAME, 'iframe')
                    self.driver.switch_to.frame(iframe)
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

                while self.stop == False and self.part == "booking":
                    config_special_area = []
                    config_grade_area = []
                    if self.__seatOrder != "" and self.__special_area == "Y":
                        config_special_area = self.__seatOrder.split(",")
                    function.print_debug(f'config_special_area setting:{config_special_area}')
                    if self.__seatGrade != "" and self.__special_area == "Y":
                        config_grade_area = self.__seatGrade.split(",")
                    function.print_debug(f'config_grade_area setting:{config_grade_area}')

                    res = function.select_seat(self.driver, config_grade_area, config_special_area, self.__special_area)
                    function.print_debug(f'Macro booking return value:{res}')
                    if res == CODE.SUCCESS:
                        self.part = "catch"
                        self.jump_count_update()
                        break
                    elif res == CODE.CONFLICT:
                        self.jump_count_update()
                    elif res == CODE.AREA_ERROR:
                        self.__special_area = "N"

                    self.driver.find_element(By.ID, 'btnReloadSchedule').click()
                    self.wait.until(EC.presence_of_element_located((By.ID, "ez_canvas")))

                if self.stop == False and self.part == "catch":
                    print("끝!!!!!!!!!")
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
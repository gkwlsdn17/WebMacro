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
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')

        # 설정 값들 로드
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

        # 재시작 관련 변수 추가
        # 10분을 초과하면 예매정보 오류가 떠서 예매 불가
        self.restart_interval = 10 * 60  # 10분 (초 단위)
        self.last_restart_time = time.time()
        self.restart_enabled = True  # 재시작 기능 활성화 플래그
        
        # 기존 변수들
        self.driver = None
        self.wait = None
        self.end = False
        self.stop = False
        self.part = "login"
        self.skip_select_date = False

        self.img_folder_path = './images'
        self.make_image_save_folder()

        # 초기 드라이버 생성
        self.init_driver()

        self.main_thread = threading.Thread(target=self.run)
        self.main_thread.start()

        self.key_reading = threading.Thread(target=self.key_interrupt)
        self.key_reading.start()

    def init_driver(self):
        """드라이버 초기화"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 180)
        time.sleep(5)
        print("새로운 Chrome 드라이버가 시작되었습니다.")

    def restart_process(self):
        """프로세스 재시작"""
        print("10분이 경과하여 프로세스를 재시작합니다...")
        
        # 현재 드라이버 종료
        try:
            self.driver.quit()
        except:
            pass
        
        # 새 드라이버 생성
        self.init_driver()
        
        # 상태 초기화
        self.part = "login"
        self.stop = False
        self.last_restart_time = time.time()
        
        print("프로세스 재시작 완료. 로그인부터 다시 시작합니다.")

    def should_restart(self):
        """재시작이 필요한지 확인"""
        if not self.restart_enabled:
            return False
        
        current_time = time.time()
        return (current_time - self.last_restart_time) >= self.restart_interval

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
            elif self.key == 'grade':
                print(f'please enter grade ex)S석,A석,B석 :')
                change_grade = input()
                self.__seatGrade = change_grade
                self.__special_area = 'Y'
                print(f'config grade change success. {self.__seatGrade}')
            elif self.key == 'grade_cancel':
                self.__seatGrade = ''
                print(f'grade cancel!!')
            elif self.key == 'skip_select_date':
                self.__skip_date_click = True
                print('skip_select_date set ok.')
            elif self.key == 'skip_select_date_cancel':
                self.__skip_date_click = False
                print('skip_select_date cancel set ok.')
            # 재시작 관련 명령어 추가
            elif self.key == 'restart':
                print('수동으로 재시작을 실행합니다...')
                self.restart_process()
            elif self.key == 'restart_on':
                self.restart_enabled = True
                print('10분 주기 자동 재시작이 활성화되었습니다.')
            elif self.key == 'restart_off':
                self.restart_enabled = False
                print('10분 주기 자동 재시작이 비활성화되었습니다.')
            elif self.key == 'restart_status':
                status = "활성화" if self.restart_enabled else "비활성화"
                elapsed = int(time.time() - self.last_restart_time)
                remaining = max(0, self.restart_interval - elapsed)
                print(f'자동 재시작: {status}')
                print(f'마지막 재시작 후 경과 시간: {elapsed}초')
                print(f'다음 재시작까지: {remaining}초')

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
            # 재시작 체크 - 각 단계에서 확인
            if self.should_restart() and self.part != "catch" and self.stop == False:
                self.restart_process()
                continue
            
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
                        auth_success = function.certification(self.driver, self.img_folder_path)
                        if auth_success == False:
                            print("인증이 실패하여 재시작합니다.")
                            self.restart_process()
                            self.stop = True
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
                    # booking 단계에서도 재시작 체크
                    if self.should_restart():
                        self.restart_process()
                        break
                    
                    config_special_area = []
                    config_grade_area = []
                    if self.__seatOrder != "" and self.__special_area == "Y":
                        config_special_area = [item.strip() for item in self.__seatOrder.split(",")]
                    function.print_debug(f'config_special_area setting:{config_special_area}')
                    if self.__seatGrade != "" and self.__special_area == "Y":
                        config_grade_area = [item.strip() for item in self.__seatGrade.split(",")]
                    function.print_debug(f'config_grade_area setting:{config_grade_area}')

                    res = function.select_seat(self.driver, config_grade_area, config_special_area, self.__special_area)
                    function.print_debug(f'Macro booking return value:{res}')
                    if res == CODE.SUCCESS:
                        self.part = "catch"
                        self.jump_count_update()
                        break
                    elif res == CODE.CONFLICT:
                        self.jump_count_update()
                        try:
                            if self.__sound == "Y":
                                playsound("conflict.mp3")
                        except:
                            pass
                        time.sleep(1)
                    elif res == CODE.AREA_ERROR:
                        self.__special_area = "N"
                    
                    button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "btnReloadSchedule"))
                    )
                    print("새로고침 클릭")
                    button.click()
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
        # 프로그램 종료 시 드라이버 정리
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass

if __name__ == "__main__":
    import Macro
    app = Macro.Macro()
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
    def __init__(self, bridge=None):
        self.bridge = bridge  # UI 브리지 참조
        
        # 기존 설정들
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 180)
        
        # 브리지에서 설정 가져오기 (우선순위)
        if self.bridge:
            print("브리지에서 가져오기")
            self.load_config_from_bridge()
        else:
            print("기존방식")
            # 기존 방식으로 설정 로드
            self.load_config_from_file()

        self.end = False
        self.stop = False
        self.part = "login"
        self.skip_select_date = False
        self.booking_success = False  # 예매 성공 플래그 추가

        self.img_folder_path = './images'
        self.make_image_save_folder()

        # UI 모드에서는 키 인터럽트 스레드 시작하지 않음
        if not self.bridge:
            self.key_reading = threading.Thread(target=self.key_interrupt)
            self.key_reading.start()

    def load_config_from_bridge(self):
        """브리지에서 설정 로드 - 웹 UI의 최신 설정 사용"""
        config = self.bridge.config
        
        self.__id = config['loginInfo']['id']
        self.__pw = config['loginInfo']['pw']
        self.__prod_id = config['bookInfo']['prod_id']
        self.__seatOrder = config['bookInfo']['order']
        self.__seatGrade = config['bookInfo']['grade']
        self.__start_year = int(config['program']['year'])
        self.__start_month = int(config['program']['month'])
        self.__start_day = int(config['program']['day'])
        self.__start_hour = int(config['program']['hour'])
        self.__start_minute = int(config['program']['minute'])
        self.__auto_certification = config['function']['auto_certification']
        self.__special_area = config['function']['special_area']
        self.__sound = config['function']['sound']
        self.__seat_jump = config['function']['seat_jump']
        self.__seat_jump_count = int(config['function']['seat_jump_count'])
        self.__seat_jump_special_repeat = config['function']['seat_jump_special_repeat']
        self.__seat_jump_special_repeat_count = int(config['function']['seat_jump_special_repeat_count'])
        self.__skip_date_click = config['function']['skip_date_click']
        self.__phone = config['payment']['phone']
        
        self.emit_log(f"웹 UI 설정을 로드했습니다:", "info")
        self.emit_log(f"  - 아이디: {self.__id}", "info")
        self.emit_log(f"  - 상품ID: {self.__prod_id}", "info")
        self.emit_log(f"  - 예매시간: {self.__start_year}-{self.__start_month:02d}-{self.__start_day:02d} {self.__start_hour:02d}:{self.__start_minute:02d}", "info")
        self.emit_log(f"  - 좌석순서: {self.__seatOrder}", "info")
        self.emit_log(f"  - 좌석등급: {self.__seatGrade}", "info")

    def sync_config_from_bridge(self):
        """실행 중에 브리지에서 설정을 다시 동기화"""
        if self.bridge:
            old_id = self.__id
            old_prod_id = self.__prod_id
            
            self.load_config_from_bridge()
            
            # 중요 설정이 변경된 경우 알림
            if old_id != self.__id:
                self.emit_log(f"아이디가 {old_id} → {self.__id}로 변경되었습니다.", "warning")
            if old_prod_id != self.__prod_id:
                self.emit_log(f"상품ID가 {old_prod_id} → {self.__prod_id}로 변경되었습니다.", "warning")

    def load_config_from_file(self):
        """파일에서 설정 로드 (기존 방식 - 콘솔 모드용)"""
        self.config = configparser.ConfigParser()
        
        if not os.path.exists('config.ini'):
            self.emit_log("config.ini 파일이 없습니다. 기본 설정을 생성합니다.", "warning")
            self.create_default_config()
            
        self.config.read('config.ini', encoding='utf-8')

        self.__id = self.config['loginInfo']['id']
        self.__pw = self.config['loginInfo']['pw']
        self.__prod_id = self.config['bookInfo']['prod_id']
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

    def create_default_config(self):
        """기본 config.ini 파일 생성"""
        config = configparser.ConfigParser()
        
        config['loginInfo'] = {
            'id': '',
            'pw': ''
        }
        
        config['bookInfo'] = {
            'prod_id': '',
            'book_date': '',
            'book_time': '',
            'order': '',
            'grade': ''
        }
        
        config['program'] = {
            'year': str(datetime.datetime.now().year),
            'month': str(datetime.datetime.now().month),
            'day': str(datetime.datetime.now().day),
            'hour': '14',
            'minute': '0'
        }
        
        config['function'] = {
            'auto_certification': 'Y',
            'special_area': 'N',
            'sound': 'Y',
            'seat_jump': 'N',
            'seat_jump_count': '0',
            'seat_jump_special_repeat': 'N',
            'seat_jump_special_repeat_count': '0',
            'skip_date_click': 'N'
        }
        
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def emit_log(self, message, log_type="info"):
        """로그 메시지 전송"""
        if self.bridge:
            self.bridge.emit_log(message, log_type)
        else:
            print(message)

    def update_status(self):
        """상태 업데이트"""
        if self.bridge:
            self.bridge.current_part = self.part
            self.bridge.emit_status()

    def make_image_save_folder(self):
        if not os.path.exists(self.img_folder_path):
            os.makedirs(self.img_folder_path)

    def key_interrupt(self):
        """기존 키 인터럽트 (콘솔 모드용)"""
        while not self.end:
            try:
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
                elif self.key == 'login':
                    self.part = "login"
                    self.stop = False
                elif self.key == 'time_wait':
                    self.part = "time_wait"
                    self.stop = False
                elif self.key == 'popup_check':
                    self.part = "popup_check"
                    self.stop = False
                elif self.key == 'click_book':
                    self.part = "click_book"
                    self.stop = False
                elif self.key == 'change_window':
                    self.part = "change_window"
                    self.stop = False
                elif self.key == 'certification':
                    self.part = "certification"
                    self.stop = False
                elif self.key == 'seat_frame_move':
                    self.part = "seat_frame_move"
                    self.stop = False
                elif self.key == 'set_seat_jump':
                    self.part = "set_seat_jump"
                    self.stop = False
                elif self.key == 'booking':
                    self.part = "booking"
                    self.stop = False
                elif self.key == 'catch':
                    self.part = "catch"
                    self.stop = False
            except EOFError:
                break

    def jump_count_update(self):
        if function.seat_jump_special_repeat == 'Y' and function.seat_jump_special_repeat_count > 0:
            function.seat_jump_special_repeat_count -= 1
            self.emit_log(f'function.seat_jump_special_repeat_count: {function.seat_jump_special_repeat_count}')
            if function.seat_jump_special_repeat_count < 1:
                function.seat_jump_special_repeat = 'N'
                function.seat_jump = 'N'
                function.seat_jump_count = 0
                self.emit_log('점프 끝')

    def check_booking_page_elements(self):
        """예매 완료 페이지 요소들 확인"""
        try:
            # 일반적인 예매 완료 페이지 요소들 확인
            success_indicators = [
                "예매가 완료되었습니다",
                "예매완료",
                "booking complete",
                "예약이 완료되었습니다"
            ]
            
            page_source = self.driver.page_source.lower()
            
            for indicator in success_indicators:
                if indicator.lower() in page_source:
                    self.emit_log(f"예매 완료 확인: '{indicator}' 텍스트 발견", "success")
                    return True
            
            # URL 변화 확인 (예매 완료 후 URL이 변하는 경우)
            current_url = self.driver.current_url.lower()
            completion_url_patterns = [
                "complete",
                "success",
                "finish",
                "done"
            ]
            
            for pattern in completion_url_patterns:
                if pattern in current_url:
                    self.emit_log(f"예매 완료 확인: URL에 '{pattern}' 패턴 발견", "success")
                    return True
                    
            return False
            
        except Exception as e:
            self.emit_log(f"예매 완료 확인 중 오류: {e}", "warning")
            return False
        
    def check_current_window(self):
        """현재 어느 창에 있는지 확인"""
        print("현재 어느 창에 있는지 확인")
        try:
            current_handle = self.driver.current_window_handle
            if len(self.driver.window_handles) > 1:
                if current_handle == self.driver.window_handles[0]:
                    return "main_window"
                else:
                    return "new_window"
            else:
                return "single_window"
        except:
            return "error"
        
    def switch_to_main_window(self):
        """메인 창으로 전환하는 함수"""
        try:
            if len(self.driver.window_handles) > 0:
                main_window = self.driver.window_handles[0]
                if self.driver.current_window_handle != main_window:
                    self.driver.switch_to.window(main_window)
                    self.emit_log("메인 창으로 전환됨", "info")
                    return True
                else:
                    self.emit_log("이미 메인 창에 있음", "info")
                    return True
        except Exception as e:
            self.emit_log(f"메인 창 전환 실패: {str(e)}", "error")
            return False

    def run(self):
        """메인 실행 루프"""
        while True:
            # UI 모드에서는 브리지의 stop 상태 및 설정 변경 확인
            if self.bridge:
                self.stop = self.bridge.is_paused
                
                # 예매 성공 후에는 브리지에서 part 변경을 무시
                if not self.booking_success and self.bridge.current_part != self.part:
                    self.part = self.bridge.current_part
                    self.emit_log(f"단계가 {self.part}로 변경되었습니다.")
            
            if self.stop == True:
                continue

            try:
                if self.stop == False and self.part == "login":
                    self.emit_log("로그인을 시작합니다.", "info")
                    self.update_status()
                    
                    # 브리지에서 최신 설정 다시 로드
                    if self.bridge:
                        self.sync_config_from_bridge()
                    
                    # 필수값 검증
                    if not self.__id or not self.__pw:
                        self.emit_log("아이디 또는 비밀번호가 설정되지 않았습니다.", "error")
                        self.stop = True
                        continue
                    
                    if not self.__prod_id:
                        self.emit_log("상품 ID가 설정되지 않았습니다.", "error")
                        self.stop = True
                        continue
                    
                    function.login(self.driver, self.__id, self.__pw)
                    self.driver.get(f'https://ticket.melon.com/performance/index.htm?prodId={self.__prod_id}')
                    self.part = "time_wait"
                    self.emit_log("로그인 완료, 시간 대기 단계로 이동", "success")

                if self.stop == False and self.part == "time_wait":
                    self.emit_log("예매 시간까지 대기 중...", "info")
                    self.update_status()
                    
                    if self.__skip_date_click == 'Y':
                        self.emit_log("날짜 선택 건너뛰기 모드", "info")
                        WebDriverWait(self.driver, 600).until(EC.new_window_is_opened(self.driver.window_handles))
                        self.part = "change_window"
                    else:
                        target_time = datetime.datetime(
                            self.__start_year, self.__start_month, self.__start_day, 
                            self.__start_hour, self.__start_minute, 0
                        )
                        self.emit_log(f"예매 시작 시간: {target_time.strftime('%Y-%m-%d %H:%M:%S')}", "info")
                        pause.until(target_time)
                        self.part = "popup_check"

                if self.stop == False and self.part == "popup_check":
                    self.emit_log("팝업 확인 중...", "info")
                    self.update_status()
                    function.check_alert(self.driver)
                    WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.ID, 'list_date')))
                    self.part = "click_book"

                if self.stop == False and self.part == "click_book":
                    self.emit_log("예매 버튼 클릭", "info")
                    self.update_status()
                    
                    if self.__skip_date_click == 'N':
                        cnt = 0
                        ret = function.select_date(self.driver, self.bridge.config if self.bridge else self.config)
                        if ret == False:
                            while cnt < 3:
                                cnt += 1
                                ret = function.select_date(self.driver, self.bridge.config if self.bridge else self.config)
                                if ret == True:
                                    break
                    
                    WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
                    self.part = "change_window"

                if self.stop == False and self.part == "change_window":
                    self.emit_log("새 창으로 전환", "info")
                    self.update_status()
                    self.check_current_window()
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    self.part = "certification"

                if self.stop == False and self.part == "certification":

                    window_state = self.check_current_window()
                    if window_state == "main_window":
                        self.emit_log("메인 창에 있음, 새 창으로 전환 필요", "warning")
                        self.part = "change_window"
                        continue
                        
                    self.emit_log("보안문자 인증 중...", "info")
                    self.update_status()
                    
                    if self.__auto_certification == "N":
                        try:
                            label = self.driver.find_element(By.ID, 'label-for-captcha')
                            self.driver.execute_script("arguments[0].focus();", label)
                            self.emit_log("수동 보안문자 입력 대기 중...", "warning")
                        except Exception as e:
                            self.emit_log(f"certification box focus error:{e}")
                                
                        self.wait.until(EC.invisibility_of_element_located((By.ID, "certification")))
                    else:
                        self.emit_log("자동 보안문자 인증 시도", "info")
                        function.certification(self.driver, self.img_folder_path)
                    
                    self.part = "seat_frame_move"

                if self.stop == False and self.part == "seat_frame_move":
                    self.emit_log("좌석 선택 화면으로 이동", "info")
                    self.update_status()
                    iframe = self.driver.find_element(By.TAG_NAME, 'iframe')
                    self.driver.switch_to.frame(iframe)
                    self.part = "set_seat_jump"

                if self.stop == False and self.part == "set_seat_jump":
                    self.emit_log("좌석 점프 설정 중...", "info")
                    self.update_status()
                    
                    if self.__seat_jump == 'Y' and self.__seat_jump_count > 0:
                        function.seat_jump = 'Y'
                        function.seat_jump_count = self.__seat_jump_count
                        if self.__seat_jump_special_repeat == 'Y' and self.__seat_jump_special_repeat_count > 0:
                            function.seat_jump_special_repeat = 'Y'
                            function.seat_jump_special_repeat_count = self.__seat_jump_special_repeat_count
                        self.emit_log(f"좌석 점프 설정 완료 (점프 수: {self.__seat_jump_count})", "success")

                    self.part = "booking"

                # 예매 루프 - 성공할 때까지 반복
                booking_attempt = 0
                while self.stop == False and self.part == "booking" and not self.booking_success:
                    booking_attempt += 1
                    self.emit_log(f"예매 시도 #{booking_attempt}", "info")
                    self.update_status()
                    
                    # 예매 완료 페이지 확인
                    if self.check_booking_page_elements():
                        self.emit_log("이미 예매가 완료된 것으로 확인됩니다!", "success")
                        self.booking_success = True
                        self.part = "catch"
                        break
                    
                    config_special_area = []
                    config_grade_area = []
                    
                    if self.__seatOrder != "" and self.__special_area == "Y":
                        config_special_area = [item.strip() for item in self.__seatOrder.split(",")]

                    if self.__seatGrade != "" and self.__special_area == "Y":
                        config_grade_area = [item.strip() for item in self.__seatGrade.split(",")]
                    
                    self.emit_log(f'좌석 순서: {config_special_area}, 좌석 등급: {config_grade_area}')

                    res = function.select_seat(self.driver, config_grade_area, config_special_area, self.__special_area)
                    
                    if res == CODE.SUCCESS:
                        self.emit_log("좌석 선택 성공!", "success")
                        self.booking_success = True  # 성공 플래그 설정
                        self.part = "catch"
                        self.jump_count_update()
                        break
                    elif res == CODE.CONFLICT:
                        self.emit_log("좌석 충돌, 재시도 중...", "warning")
                        self.jump_count_update()
                    elif res == CODE.AREA_ERROR:
                        self.emit_log("지정된 구역에 좌석이 없어 전체 구역으로 변경", "warning")
                        self.__special_area = "N"

                    # btnReloadSchedule 버튼이 존재하는지 확인 후 클릭
                    try:
                        reload_btn = self.driver.find_element(By.ID, 'btnReloadSchedule')
                        reload_btn.click()
                        self.wait.until(EC.presence_of_element_located((By.ID, "ez_canvas")))
                        self.emit_log("좌석 새로고침 완료", "info")
                    except Exception as e:
                        self.emit_log(f"좌석 새로고침 버튼을 찾을 수 없습니다: {e}", "error")
                        self.emit_log("페이지가 이미 변경되었을 수 있습니다. 예매 완료 확인 중...", "info")
                        
                        # 페이지가 변경되었을 가능성이 있으므로 예매 완료 확인
                        if self.check_booking_page_elements():
                            self.emit_log("좌석 선택이 완료되었습니다!", "success")
                            self.booking_success = True
                            self.part = "catch"
                            break
                        else:
                            # 좌석 선택 페이지로 다시 돌아가야 할 수 있음
                            self.emit_log("좌석 선택 페이지로 복귀 시도", "warning")
                            time.sleep(2)
                            continue

                if self.stop == False and self.part == "catch":
                    self.emit_log("🎉 좌석 선택 완료!", "success")
                    self.update_status()
                    
                    try:
                        if self.__sound == "Y":
                            playsound("catch.mp3")
                    except Exception as e:
                        self.emit_log(f"사운드 재생 오류: {e}", "warning")

                        # 완료 처리
                        self.emit_log('✅ 예매가 성공적으로 완료되었습니다!', "success")
                        self.emit_log('🔄 추가 예매를 원하시면 새로 시작해주세요.', "info")

                        print("멈추자")
                        input()
                        
                        # 완료 상태로 설정
                        self.booking_success = True
                        self.stop = True
                        self.part = "completed"
                        self.update_status()
                    
                        # UI 모드에서는 브리지 상태도 업데이트
                        if self.bridge:
                            self.bridge.is_paused = True
                            self.bridge.current_part = "completed"
                            self.bridge.emit_status()
                            self.bridge.emit_log("🎊 축하합니다! 예매가 완료되었습니다!", "success")

                    # self.part = "payment1"
                    
                # if self.stop == False and self.part == "payment1":
                #     self.emit_log("매수 선택 시작", "info")
                #     self.update_status()

                #     payment1_result = function.payment1(self.driver)
                #     if payment1_result:
                #         self.emit_log("매수 선택 완료", "success")
                #         self.part = "payment2"
                #     else:
                #         raise RuntimeError("매수 선택 오류 발생")

                # if self.stop == False and self.part == "payment2":
                #     self.emit_log("결제 시작!", "info")
                #     self.update_status()
                #     payment2_result = function.payment2(self.driver, self.__phone)
                #     if payment2_result:
                #         self.emit_log("결제 완료", "success")
                #         # 완료 처리
                #         self.emit_log('✅ 예매가 성공적으로 완료되었습니다!', "success")
                #         self.emit_log('🔄 추가 예매를 원하시면 새로 시작해주세요.', "info")
                        
                #         # 완료 상태로 설정
                #         self.booking_success = True
                #         self.stop = True
                #         self.part = "completed"
                #         self.update_status()
                    
                #         # UI 모드에서는 브리지 상태도 업데이트
                #         if self.bridge:
                #             self.bridge.is_paused = True
                #             self.bridge.current_part = "completed"
                #             self.bridge.emit_status()
                #             self.bridge.emit_log("🎊 축하합니다! 예매가 완료되었습니다!", "success")
                    
                #         break  # 루프 탈출
                #     else:
                #         raise RuntimeError("결제2 오류 발생")

            except Exception as e:
                error_msg = f'현재 단계: {self.part}\n오류 내용:\n{traceback.format_exc()}'
                self.emit_log(error_msg, "error")
                self.emit_log('❌ 오류가 발생했습니다. 일시정지됩니다.', "error")
                self.stop = True

                print("멈추자")
                input()
                
                # UI 모드에서는 브리지 상태도 업데이트
                if self.bridge:
                    self.bridge.is_paused = True
                    self.bridge.emit_status()

            # 예매 완료나 오류로 중단된 경우 루프 종료
            if self.booking_success or self.part == 'completed':
                break

            if self.end == True:
                break

        self.emit_log("매크로 종료", "info")
        print("종료하려면 아무 키나 누르고 Enter를 치세요... 1")
        input()
        print("종료하려면 아무 키나 누르고 Enter를 치세요... 2")
        input()

    def start_with_ui(self):
        """UI 모드로 시작"""
        self.main_thread = threading.Thread(target=self.run, daemon=True)
        self.main_thread.start()

# UI 모드로 사용할 때
if __name__ == "__main__":
    # 콘솔 모드 (기존 방식)
    app = Macro()
    main_thread = threading.Thread(target=app.run)
    main_thread.start()
    main_thread.join()
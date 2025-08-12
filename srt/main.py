import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.alert import Alert
from playsound import playsound
import os
import traceback
import hashlib

EXPECTED_HASH = "aa8f2d6c9228b8a52cb6f3f3f3dfe671589905badfd332c08c385b13878b2266"

try:
    with open("secret.run_key") as f:
        key = f.read().strip()
    if hashlib.sha256(key.encode()).hexdigest() != EXPECTED_HASH:
        raise Exception("실행 권한 없음")
except FileNotFoundError:
    print("secret.run_key 파일이 없습니다.")
    exit(1)

class SRTAutoBooking:
    def __init__(self, config_file='config.json'):
        """SRT 자동 로그인 및 예약 조회 클래스 초기화"""
        self.config = self.load_config(config_file)
        self.driver = None
        self.wait = None
        
    def load_config(self, config_file):
        """설정 파일에서 로그인 및 예약 정보 로드"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            required_keys = [
                'phone_number', 'password', 'departure', 'arrival', 
                'date', 'time', 'adults', 'children', 'preferred_departure_time',
                'retry_interval', 'max_retry_count', 'card_number', 'card_expiry', 
                'card_password', 'birth_date', 'auto_payment'  # 결제 정보 추가
            ]
            
            for key in required_keys:
                if key not in config:
                    if key == 'retry_interval':
                        config[key] = 30  # 기본값: 30초마다 재시도
                    elif key == 'max_retry_count':
                        config[key] = 0  # 기본값: 무제한 재시도 (0)
                    elif key == 'auto_payment':
                        config[key] = False  # 기본값: 자동결제 비활성화
                    elif key in ['card_number', 'card_expiry', 'card_password', 'birth_date']:
                        config[key] = ""  # 결제정보 기본값: 빈 문자열
                    else:
                        raise ValueError(f"설정 파일에 '{key}' 정보가 없습니다.")
                    
            return config
        except FileNotFoundError:
            print(f"설정 파일 '{config_file}'을 찾을 수 없습니다.")
            print("config.json 파일을 생성해주세요.")
            print("예시 형식:")
            print("""{
    "phone_number": "01012345678",
    "password": "your_password",
    "departure": "서울",
    "arrival": "부산",
    "date": "2025-08-15",
    "time": "06",
    "adults": 1,
    "children": 0,
    "preferred_departure_time": "08:00",
    "retry_interval": 30,
    "max_retry_count": 0,
    "card_number": "1234567812345678",
    "card_expiry": "1225",
    "card_password": "12",
    "birth_date": "901225",
    "auto_payment": true
}""")
            return None
        except json.JSONDecodeError:
            print("설정 파일의 JSON 형식이 올바르지 않습니다.")
            return None
    
    def setup_driver(self):
        """웹드라이버 설정"""
        chrome_options = Options()
        
        # 필요에 따라 주석 해제
        # chrome_options.add_argument('--headless')  # 브라우저 창 숨김
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent 설정
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            # ChromeDriver 경로를 명시적으로 지정하거나 PATH에 있다면 생략 가능
            # service = Service('path/to/chromedriver')  # 필요시 주석 해제하고 경로 설정
            # self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 대기 객체 생성 (최대 10초 대기)
            self.wait = WebDriverWait(self.driver, 10)
            
            print("웹드라이버 설정 완료")
            return True
            
        except Exception as e:
            print(f"웹드라이버 설정 실패: {e}")
            return False
    
    def navigate_to_login_page(self):
        """SRT 로그인 페이지로 이동"""
        try:
            login_url = "https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000"
            self.driver.get(login_url)
            
            # 페이지 로드 대기
            self.wait.until(EC.presence_of_element_located((By.ID, "login-form")))
            print("로그인 페이지 로드 완료")
            return True
            
        except TimeoutException:
            print("로그인 페이지 로드 시간 초과")
            return False
        except Exception as e:
            print(f"페이지 이동 실패: {e}")
            return False
    
    def select_phone_login_option(self):
        """휴대전화번호 로그인 옵션 선택"""
        try:
            # 휴대전화번호 라디오 버튼 클릭
            phone_radio = self.wait.until(
                EC.element_to_be_clickable((By.ID, "srchDvCd3"))
            )
            phone_radio.click()
            print("휴대전화번호 로그인 옵션 선택됨")
            
            # 휴대전화번호 입력 영역이 활성화될 때까지 대기
            self.wait.until(EC.element_to_be_clickable((By.ID, "srchDvNm03")))
            return True
            
        except TimeoutException:
            print("휴대전화번호 로그인 옵션을 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"로그인 옵션 선택 실패: {e}")
            return False
    
    def enter_login_credentials(self):
        """로그인 정보 입력"""
        try:
            # 휴대전화번호 입력
            phone_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "srchDvNm03"))
            )
            phone_input.clear()
            phone_input.send_keys(self.config['phone_number'])
            print("휴대전화번호 입력 완료")
            
            # 비밀번호 입력
            password_input = self.driver.find_element(By.ID, "hmpgPwdCphd03")
            password_input.clear()
            password_input.send_keys(self.config['password'])
            print("비밀번호 입력 완료")
            
            return True
            
        except NoSuchElementException as e:
            print(f"입력 필드를 찾을 수 없습니다: {e}")
            return False
        except Exception as e:
            print(f"로그인 정보 입력 실패: {e}")
            return False
    
    def click_login_button(self):
        """로그인 버튼 클릭"""
        try:
            # 휴대전화번호 로그인 영역의 확인 버튼 찾기
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".srchDvCd3 .loginSubmit"))
            )
            
            login_button.click()
            print("로그인 버튼 클릭 완료")
            return True
                
        except TimeoutException:
            print("로그인 버튼을 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"로그인 버튼 클릭 실패: {e}")
            return False
    
    def wait_for_login_result(self):
        """로그인 결과 확인"""
        try:
            # 로그인 성공 시 페이지 변경 대기 (URL 변경 또는 특정 요소 나타남)
            try:
                # 로그인 페이지에서 벗어났는지 확인 (최대 5초 대기)
                WebDriverWait(self.driver, 5).until(
                    lambda driver: "selectLoginForm" not in driver.current_url
                )
                print("로그인 성공! 메인 페이지로 이동했습니다.")
                return True
            except TimeoutException:
                # URL이 변경되지 않았다면 에러 메시지 확인
                try:
                    error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
                    if error_elements:
                        print(f"로그인 실패: {error_elements[0].text}")
                    else:
                        print("로그인 실패: 알 수 없는 오류")
                except:
                    print("로그인 실패: 페이지가 변경되지 않았습니다.")
                return False
                
        except Exception as e:
            print(f"로그인 결과 확인 실패: {e}")
            return False
    
    
    def navigate_to_booking_page(self):
        """예약 페이지로 이동 (개선된 버전)"""
        try:
            # 홈페이지로 이동 (로그인 후 자동으로 이동되지만 확실하게 하기 위해)
            home_url = "https://etk.srail.kr/main.do"
            print(f"홈페이지로 이동 중: {home_url}")
            self.driver.get(home_url)
            
            # 여러 가능한 요소들로 페이지 로드 확인
            page_load_indicators = [
                (By.CLASS_NAME, "wrap"),
                (By.TAG_NAME, "body"),
                (By.ID, "container"),
                (By.CLASS_NAME, "container"),
                (By.CLASS_NAME, "content"),
                (By.TAG_NAME, "main")
            ]
            
            page_loaded = False
            for locator_type, locator_value in page_load_indicators:
                try:
                    # 각 요소에 대해 짧은 대기시간으로 시도
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((locator_type, locator_value))
                    )
                    if element:
                        print(f"페이지 로드 확인됨 (요소: {locator_type}='{locator_value}')")
                        page_loaded = True
                        break
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"요소 확인 중 오류: {e}")
                    continue
            
            # 위의 방법들이 모두 실패하면 URL 확인으로 대체
            if not page_loaded:
                current_url = self.driver.current_url
                print(f"요소 기반 확인 실패, 현재 URL 확인: {current_url}")
                
                # SRT 관련 URL인지 확인
                if "srail.kr" in current_url:
                    print("SRT 사이트로 이동 확인됨 (URL 기준)")
                    page_loaded = True
                else:
                    print("❌ SRT 사이트로 이동하지 못했습니다.")
                    return False
            
            # 예약 관련 요소들이 로드되었는지 확인
            booking_elements = [
                (By.ID, "dptRsStnCd"),      # 출발역 선택
                (By.ID, "arvRsStnCd"),      # 도착역 선택  
            ]
            
            booking_ready = False
            for locator_type, locator_value in booking_elements:
                try:
                    element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((locator_type, locator_value))
                    )
                    if element:
                        print(f"예약 요소 확인됨 (요소: {locator_type}='{locator_value}')")
                        booking_ready = True
                        break
                except:
                    continue
            
            if booking_ready:
                print("✅ 예약 페이지 로드 완료 (예약 요소 확인)")
                return True
            elif page_loaded:
                print("⚠️ 페이지는 로드되었으나 예약 요소를 찾을 수 없습니다. 계속 진행...")
                return True  # 페이지는 로드되었으므로 계속 진행
            else:
                print("❌ 페이지 로드 실패")
                return False
                
        except TimeoutException:
            print("⚠️ 페이지 로드 시간 초과, 하지만 URL 확인 시도...")
            try:
                current_url = self.driver.current_url
                if "srail.kr" in current_url:
                    print("URL 기준으로 SRT 사이트 확인됨. 계속 진행...")
                    return True
                else:
                    print("❌ SRT 사이트가 아닙니다.")
                    return False
            except:
                print("❌ URL 확인도 실패했습니다.")
                return False
        except Exception as e:
            print(f"예약 페이지 이동 실패: {e}")
            try:
                # 오류 발생 시에도 현재 상태 확인
                current_url = self.driver.current_url
                print(f"오류 발생, 현재 URL: {current_url}")
                if "srail.kr" in current_url:
                    print("오류에도 불구하고 SRT 사이트에 있음. 계속 진행...")
                    return True
            except:
                pass
            return False

    def wait_for_page_load(self, timeout=10):
        """페이지 로드 완료 대기 (추가 유틸리티 함수)"""
        try:
            # JavaScript로 페이지 로드 상태 확인
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            print("JavaScript 기준 페이지 로드 완료")
            return True
        except:
            print("JavaScript 페이지 로드 확인 실패")
            return False

    def check_login_status(self):
        """로그인 상태 확인"""
        try:
            # 로그인 상태를 나타내는 요소들 확인
            login_indicators = [
                "//a[contains(text(), '로그아웃')]",
                "//span[contains(text(), '님')]",
                "//*[contains(@class, 'user')]",
                "//a[contains(text(), '마이페이지')]"
            ]
            
            for indicator in login_indicators:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, indicator))
                    )
                    if element.is_displayed():
                        print("✅ 로그인 상태 확인됨")
                        return True
                except:
                    continue
            
            print("⚠️ 로그인 상태를 확인할 수 없습니다.")
            return False
            
        except Exception as e:
            print(f"로그인 상태 확인 중 오류: {e}")
            return False
    
    def select_departure_station(self):
        """출발역 선택"""
        try:
            # 출발역 드롭다운 클릭
            departure_select = self.wait.until(
                EC.element_to_be_clickable((By.ID, "dptRsStnCd"))
            )
            departure_select.click()
            
            # 드롭다운 옵션이 활성화될 때까지 대기
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//select[@id='dptRsStnCd']/option[text()='{self.config['departure']}']"))
            )
            
            # 출발역 선택
            departure_option = self.driver.find_element(
                By.XPATH, 
                f"//select[@id='dptRsStnCd']/option[text()='{self.config['departure']}']"
            )
            departure_option.click()
            print(f"출발역 '{self.config['departure']}' 선택 완료")
            return True
            
        except (TimeoutException, NoSuchElementException):
            print(f"출발역 '{self.config['departure']}'을 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"출발역 선택 실패: {e}")
            return False
    
    def select_arrival_station(self):
        """도착역 선택"""
        try:
            # 도착역 드롭다운 클릭
            arrival_select = self.wait.until(
                EC.element_to_be_clickable((By.ID, "arvRsStnCd"))
            )
            arrival_select.click()
            
            # 드롭다운 옵션이 활성화될 때까지 대기
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//select[@id='arvRsStnCd']/option[text()='{self.config['arrival']}']"))
            )
            
            # 도착역 선택
            arrival_option = self.driver.find_element(
                By.XPATH, 
                f"//select[@id='arvRsStnCd']/option[text()='{self.config['arrival']}']"
            )
            arrival_option.click()
            print(f"도착역 '{self.config['arrival']}' 선택 완료")
            return True
            
        except (TimeoutException, NoSuchElementException):
            print(f"도착역 '{self.config['arrival']}'을 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"도착역 선택 실패: {e}")
            return False
    
    def select_departure_date(self):
        """출발 날짜 선택"""
        try:
            # JavaScript로 직접 selectCalendarInfo 함수 호출
            formatted_date = self.config['date'].replace('-', '')
            
            # 먼저 달력 팝업을 열고
            self.driver.execute_script("selectCalendarInfo(document.getElementsByName('dptDt')[0]);")
            
            # 팝업 창이 열릴 때까지 대기
            WebDriverWait(self.driver, 5).until(
                lambda driver: len(driver.window_handles) > 1
            )
            
            # 팝업에서 날짜 선택
            main_window = self.driver.current_window_handle
            popup_windows = self.driver.window_handles
            
            for window in popup_windows:
                if window != main_window:
                    self.driver.switch_to.window(window)
                    # 팝업에서 날짜 선택 JavaScript 실행
                    self.driver.execute_script(f"selectDateInfo('{formatted_date}');")
                    break
            
            # 팝업이 닫힐 때까지 대기
            WebDriverWait(self.driver, 5).until(
                lambda driver: len(driver.window_handles) == 1
            )
            
            # 원래 윈도우로 돌아가기
            self.driver.switch_to.window(main_window)
            
            print(f"출발 날짜 '{self.config['date']}' 선택 완료")
            return True
            
        except Exception as e:
            print(f"출발 날짜 선택 실패: {e}")
            try:
                self.driver.switch_to.window(main_window)
            except:
                pass
            return False
    
    def select_departure_time(self):
        """출발 시간 선택"""
        try:
            # 시간 드롭다운이 존재할 때까지 대기
            time_select_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "dptTm"))
            )
            
            time_select = Select(time_select_element)
            
            # 시간을 정수로 변환
            hour = int(self.config['time'])
            
            # 짝수 시간으로 맞추기 (드롭다운이 2시간 간격)
            if hour % 2 != 0:
                hour = hour - 1  # 홀수면 하나 작은 짝수로
            
            # 범위 체크
            if hour < 0:
                hour = 0
            elif hour > 22:
                hour = 22
            
            # 시간 형식 변환 (HH -> HHMMSS)
            formatted_time = f"{hour:02d}0000"
            
            time_select.select_by_value(formatted_time)
            print(f"출발 시간 '{hour:02d}시 이후' 선택 완료")
            return True
            
        except (TimeoutException, NoSuchElementException):
            print("출발 시간 선택 필드를 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"출발 시간 선택 실패: {e}")
            print(f"시도한 값: {formatted_time if 'formatted_time' in locals() else self.config['time']}")
            return False
    
    def set_passenger_count(self):
        """승객 수 설정"""
        try:
            # 어른 승객 수 설정
            adult_select_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "psgInfoPerPrnb1"))
            )
            adult_select = Select(adult_select_element)
            adult_select.select_by_value(str(self.config['adults']))
            print(f"어른 승객 수 '{self.config['adults']}명' 설정 완료")
            
            # 어린이 승객 수 설정
            child_select_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "psgInfoPerPrnb5"))
            )
            child_select = Select(child_select_element)
            child_select.select_by_value(str(self.config['children']))
            print(f"어린이 승객 수 '{self.config['children']}명' 설정 완료")
            
            return True
            
        except (TimeoutException, NoSuchElementException):
            print("승객 수 설정 필드를 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"승객 수 설정 실패: {e}")
            return False
    
    def click_search_button(self):
        """간편조회하기 버튼 클릭"""
        try:
            # 간편조회하기 버튼 찾기 및 클릭 (span 태그 안의 텍스트로 찾기)
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[.//span[contains(text(), '간편조회하기')]]"))
            )
            search_button.click()
            print("간편조회하기 버튼 클릭 완료")
            
            # 검색 결과 페이지 로드 대기
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
            return True
            
        except TimeoutException:
            print("간편조회하기 버튼을 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"간편조회하기 버튼 클릭 실패: {e}")
            return False
    
    
    def handle_train_composition_popup(self):
        """중련편성 팝업 처리"""
        try:
            # 팝업이 나타날 때까지 대기 (짧은 시간)
            try:
                # 팝업 요소가 나타나는지 확인
                popup_present = WebDriverWait(self.driver, 2).until(
                    lambda driver: any([
                        driver.find_elements(By.CSS_SELECTOR, "div[id*='popup']"),
                        driver.find_elements(By.CSS_SELECTOR, "div[class*='popup']"),
                        driver.find_elements(By.CSS_SELECTOR, "div[class*='modal']"),
                        driver.find_elements(By.CSS_SELECTOR, ".ui-dialog")
                    ])
                )
            except TimeoutException:
                # 팝업이 없으면 그냥 continue
                pass
            
            # 중련편성 관련 팝업 확인 및 처리
            popup_selectors = [
                "div[id*='popup']",
                "div[class*='popup']", 
                "div[class*='modal']",
                ".ui-dialog"
            ]
            
            for selector in popup_selectors:
                try:
                    popup_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for popup in popup_elements:
                        if popup.is_displayed():
                            popup_text = popup.text
                            print(f"팝업 감지: {popup_text[:50]}...")
                            
                            # 확인/닫기 버튼 찾아서 클릭
                            buttons = popup.find_elements(By.TAG_NAME, "button")
                            buttons.extend(popup.find_elements(By.CSS_SELECTOR, "a[onclick*='close']"))
                            buttons.extend(popup.find_elements(By.CSS_SELECTOR, "input[type='button']"))
                            
                            for button in buttons:
                                button_text = button.text.strip()
                                if any(word in button_text for word in ["확인", "닫기", "OK", "Close"]):
                                    self.driver.execute_script("arguments[0].click();", button)
                                    print("팝업 닫기 완료")
                                    # 팝업이 닫힐 때까지 대기
                                    WebDriverWait(self.driver, 3).until(
                                        EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
                                    )
                                    return True
                                    
                except Exception as e:
                    continue
            
            # Alert 창 처리
            try:
                WebDriverWait(self.driver, 1).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                print(f"Alert 창 감지: {alert_text}")
                alert.accept()
                print("Alert 창 확인 완료")
                return True
            except TimeoutException:
                pass
            except Exception as e:
                print(f"Alert 처리 중 오류: {e}")
                
            return False
            
        except Exception as e:
            print(f"팝업 처리 중 오류: {e}")
            return False
    
    def find_and_book_specific_time_train(self):
        """원하는 특정 시간대 열차만 찾아서 예약하기 (매진이어도 계속 시도)"""
        try:
            preferred_time = self.config['preferred_departure_time']
            target_hour = preferred_time.split(':')[0]  # '08:00' -> '08'
            
            print(f"\n정확히 '{preferred_time}' 시간대 열차만 찾는 중...")
            
            # 조회 결과 테이블 로드 대기
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
            # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
            
            # 열차 목록 테이블 찾기
            train_table = self.driver.find_element(By.CLASS_NAME, "tbl_wrap")
            train_rows = train_table.find_elements(By.XPATH, ".//tbody/tr")
            
            print(f"총 {len(train_rows)}개의 열차를 확인합니다.")
            
            # 원하는 시간대의 열차만 찾기
            for idx, row in enumerate(train_rows):
                try:
                    # 열차 정보 추출을 위한 변수들 초기화
                    departure_time = None
                    train_number = None
                    reservation_button = None
                    waitlist_button = None
                    seat_select_button = None
                    is_sold_out = False
                    is_waitlist_available = False
                    
                    # 모든 td 셀들 가져오기
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    # 디버깅을 위해 행 전체 텍스트 출력
                    row_text = row.text.strip()
                    print(f"열차 {idx+1} 행 내용: {row_text[:100]}...")
                    
                    # 1. 출발시간 찾기 - time 클래스를 가진 em 태그에서 시간 추출
                    time_elements = row.find_elements(By.CSS_SELECTOR, "em.time")
                    for time_elem in time_elements:
                        time_text = time_elem.text.strip()
                        # 첫 번째 time 요소가 출발시간 (수서역 시간)
                        if departure_time is None and ':' in time_text:
                            departure_time = time_text
                            print(f"출발시간 발견: {departure_time}")
                            break
                    
                    # 2. 열차번호 찾기
                    train_number_cell = None
                    for cell in cells:
                        if cell.get_attribute("class") == "trnNo":
                            train_number_text = cell.text.strip()
                            # 숫자만 추출
                            import re
                            numbers = re.findall(r'\d+', train_number_text)
                            if numbers:
                                train_number = numbers[0]
                                print(f"열차번호 발견: {train_number}")
                            break
                    
                    # 3. 예약 관련 버튼들 찾기
                    for cell in cells:
                        # 일반실 셀 (6번째 컬럼) 또는 특실 셀 (5번째 컬럼) 확인
                        buttons = cell.find_elements(By.TAG_NAME, "a")
                        for button in buttons:
                            button_text = button.text.strip()
                            button_class = button.get_attribute("class")
                            
                            # 매진 버튼 체크
                            if "매진" in button_text or "btn_silver" in button_class:
                                is_sold_out = True
                                print(f"매진 상태 확인: {button_text}")
                            
                            # 예약하기 버튼 체크 (burgundy_dark 클래스)
                            elif ("예약하기" in button_text or "예약" in button_text) and "btn_burgundy_dark" in button_class:
                                if "대기" not in button_text:
                                    reservation_button = button
                                    print(f"예약하기 버튼 발견: {button_text}")
                            
                            # 좌석선택 버튼 체크 (emerald 클래스)
                            elif "좌석선택" in button_text and "btn_emerald" in button_class:
                                seat_select_button = button
                                print(f"좌석선택 버튼 발견: {button_text}")
                            
                            # 예약대기 버튼 체크
                            elif "신청하기" in button_text:
                                waitlist_button = button
                                is_waitlist_available = True
                                print(f"예약대기(신청하기) 버튼 발견: {button_text}")
                    
                    # 4. 원하는 시간대 매칭 확인
                    if departure_time:
                        departure_hour = departure_time.split(':')[0]
                        
                        # 정확한 시간대 매치 확인
                        if departure_hour == target_hour:
                            print(f"\n🎯 원하는 시간대 열차 발견!")
                            print(f"   열차번호: {train_number}")
                            print(f"   출발시간: {departure_time}")
                            print(f"   매진상태: {is_sold_out}")
                            print(f"   예약대기 가능: {is_waitlist_available}")
                            
                            # 5. 예약 시도
                            if reservation_button and not is_sold_out:
                                print(f"✅ 예약 가능한 열차를 찾았습니다!")
                                
                                try:
                                    # JavaScript로 클릭 (더 안정적)
                                    self.driver.execute_script("arguments[0].click();", reservation_button)
                                    print("예약 버튼 클릭 완료!")
                                    
                                    # 중련편성 팝업 처리
                                    self.handle_train_composition_popup()
                                    
                                    # 예약 페이지 로드 대기
                                    time.sleep(2)

                                    # 결제하기 버튼 찾기 및 클릭
                                    try:
                                        payment_button_selectors = [
                                            "//button[contains(text(), '결제하기')]",
                                            "//input[@value='결제하기']",
                                            "//a[contains(., '결제하기')]",
                                            "//button[contains(@onclick, 'payment') or contains(@onclick, 'pay')]",
                                            "//input[contains(@onclick, 'payment') or contains(@onclick, 'pay')]",
                                            "//a[contains(@onclick, 'settleAmount')]"
                                        ]
                                        
                                        payment_button = None
                                        for selector in payment_button_selectors:
                                            try:
                                                payment_button = WebDriverWait(self.driver, 5).until(
                                                    EC.element_to_be_clickable((By.XPATH, selector))
                                                )
                                                break
                                            except:
                                                continue
                                        
                                        if payment_button:
                                            # 버튼이 보이도록 스크롤
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", payment_button)
                                            time.sleep(1)
                                            
                                            # 결제하기 버튼 클릭
                                            self.driver.execute_script("arguments[0].click();", payment_button)
                                            print("결제하기 버튼 클릭 완료!")
                                            
                                            # 결제 페이지 로드 대기
                                            time.sleep(2)
                                    
                                            # 자동 결제 설정이 활성화되어 있다면 결제 진행
                                            if self.config.get('auto_payment', False):
                                                payment_result = self.process_payment()
                                                if payment_result:
                                                    return "payment_success"
                                                else:
                                                    return "payment_failed"
                                            
                                            return "reservation_success"
                                        else:
                                            print("결제하기 버튼을 찾을 수 없습니다.")
                                            return "payment_button_not_found"
                                          
                                    except Exception as e:
                                        print(f"결제하기 버튼 클릭 중 오류 발생: {e}")
                                        return "payment_button_error"
                                    
                                except Exception as e:
                                    print(f"예약 버튼 클릭 오류: {e}")
                                    return "click_error"
                            
                            elif seat_select_button and not is_sold_out:
                                print(f"🎫 좌석선택을 통한 예약을 시도합니다!")
                                
                                try:
                                    self.driver.execute_script("arguments[0].click();", seat_select_button)
                                    print("좌석선택 버튼 클릭 완료!")
                                    
                                    # 좌석선택 페이지 처리
                                    time.sleep(3)
                                    return "seat_selection_success"
                                    
                                except Exception as e:
                                    print(f"좌석선택 버튼 클릭 오류: {e}")
                                    return "click_error"
                            
                            elif waitlist_button and is_waitlist_available:
                                print(f"⏳ 예약대기 가능한 열차를 찾았습니다!")
                                
                                try:
                                    self.driver.execute_script("arguments[0].click();", waitlist_button)
                                    print("예약대기 버튼 클릭 완료!")
                                    
                                    time.sleep(2)
                                    return "waitlist_success"
                                    
                                except Exception as e:
                                    print(f"예약대기 버튼 클릭 오류: {e}")
                                    return "click_error"
                            
                            elif is_sold_out and not is_waitlist_available:
                                print(f"❌ 해당 열차는 현재 매진 상태입니다. (예약대기 불가)")
                                return "sold_out"
                            
                            else:
                                print(f"❌ 해당 시간대 열차의 예약이 불가능합니다.")
                                print(f"   예약버튼: {'있음' if reservation_button else '없음'}")
                                print(f"   좌석선택: {'있음' if seat_select_button else '없음'}")
                                print(f"   예약대기: {'있음' if waitlist_button else '없음'}")
                                return "unavailable"
                    
                except Exception as e:
                    print(f"열차 {idx+1} 처리 중 오류: {e}")
                    # 디버깅을 위해 해당 행의 HTML 출력
                    try:
                        print(f"문제가 된 행의 HTML: {row.get_attribute('outerHTML')[:200]}...")
                    except:
                        pass
                    continue
            
            print(f"❌ 원하는 시간대 ({preferred_time})의 열차를 찾을 수 없습니다.")
            return "not_found"
            
        except TimeoutException:
            print("열차 조회 결과 로드 시간 초과")
            return "timeout"
        except Exception as e:
            print(f"열차 예약 시도 중 오류 발생: {e}")
            import traceback
            print(f"상세 오류: {traceback.format_exc()}")
            return "error"
    
    def process_payment(self):
        """실제 SRT HTML 구조에 맞는 결제 처리 함수"""
        try:
            print("\n=== 자동 결제 처리 시작 ===")
            
            # 결제 정보가 모두 설정되어 있는지 확인
            required_payment_info = ['card_number', 'card_expiry', 'card_password', 'birth_date']
            for info in required_payment_info:
                if not self.config.get(info):
                    print(f"❌ {info} 정보가 설정되지 않았습니다.")
                    return False
            
            # 결제 페이지 로드 대기
            time.sleep(3)
            
            # 1. 신용카드 탭이 활성화되어 있는지 확인 (기본적으로 활성화되어 있음)
            print("신용카드 결제 탭 확인 중...")
            
            # 2. 개인카드 선택 (기본으로 선택되어 있지만 확실히 하기 위해)
            if not self.select_personal_card():
                return False
            
            # 3. 카드 정보 입력
            if not self.fill_card_info_real():
                return False
            
            # 4. 유효기간 설정
            if not self.set_card_expiry():
                return False
            
            # 5. 할부개월 설정 (일시불)
            if not self.set_installment():
                return False
            
            # 6. 카드 비밀번호 입력
            if not self.enter_card_password():
                return False
            
            # 7. 인증번호(주민등록번호 앞 6자리) 입력
            if not self.enter_identification_number():
                return False
            
            # 8. 최종 결제 버튼 클릭
            if not self.click_final_payment_button_real():
                return False
            
            print("✅ 결제 처리가 완료되었습니다!")
            return True
            
        except Exception as e:
            print(f"결제 처리 중 오류 발생: {e}")
            return False

    def select_personal_card(self):
        """개인카드 선택"""
        try:
            print("개인카드 선택 중...")
            
            # 개인카드 라디오 버튼 클릭 (기본으로 선택되어 있지만 확실히 하기 위해)
            personal_card_radio = self.wait.until(
                EC.element_to_be_clickable((By.ID, "athnDvCd1J"))
            )
            
            if not personal_card_radio.is_selected():
                personal_card_radio.click()
                print("개인카드 선택 완료")
            else:
                print("개인카드 이미 선택됨")
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"개인카드 선택 실패: {e}")
            return False

    def fill_card_info_real(self):
        """실제 HTML 구조에 맞는 카드 정보 입력"""
        try:
            print("카드 정보 입력 중...")
            
            # 카드 번호를 4자리씩 분할
            card_number = self.config['card_number'].replace('-', '').replace(' ', '')
            if len(card_number) != 16:
                print("❌ 카드 번호는 16자리여야 합니다.")
                return False
            
            # 4자리씩 분할
            card_parts = [card_number[i:i+4] for i in range(0, 16, 4)]
            
            # 첫 번째 4자리 입력
            try:
                card_input1 = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "stlCrCrdNo11"))
                )
                card_input1.clear()
                card_input1.send_keys(card_parts[0])
                print("카드 번호 첫 번째 4자리 입력 완료")
            except:
                print("⚠️ 카드 번호 첫 번째 필드를 찾을 수 없습니다.")
            
            # 두 번째 4자리 입력
            try:
                card_input2 = self.driver.find_element(By.ID, "stlCrCrdNo12")
                card_input2.clear()
                card_input2.send_keys(card_parts[1])
                print("카드 번호 두 번째 4자리 입력 완료")
            except:
                print("⚠️ 카드 번호 두 번째 필드를 찾을 수 없습니다.")
            
            # 세 번째 4자리 입력
            try:
                card_input3 = self.driver.find_element(By.ID, "stlCrCrdNo13")
                card_input3.clear()
                card_input3.send_keys(card_parts[2])
                print("카드 번호 세 번째 4자리 입력 완료")
            except:
                print("⚠️ 카드 번호 세 번째 필드를 찾을 수 없습니다.")
            
            # 네 번째 4자리 입력 (보안키패드 필드)
            try:
                # 보안키패드가 아닌 경우를 대비해 일반 입력도 시도
                card_input4 = self.driver.find_element(By.ID, "stlCrCrdNo14")
                
                # 보안키패드 필드인지 확인
                if card_input4.get_attribute('readonly'):
                    print("⚠️ 네 번째 카드 번호 필드는 보안키패드입니다. 수동 입력이 필요할 수 있습니다.")
                    # 보안키패드 클릭 시도
                    try:
                        card_input4.click()
                        time.sleep(1)
                        # JavaScript로 값 설정 시도
                        self.driver.execute_script(f"arguments[0].value = '{card_parts[3]}';", card_input4)
                        print("카드 번호 네 번째 4자리 입력 시도")
                    except:
                        print("⚠️ 보안키패드 자동 입력 실패. 수동 입력이 필요합니다.")
                else:
                    card_input4.clear()
                    card_input4.send_keys(card_parts[3])
                    print("카드 번호 네 번째 4자리 입력 완료")
                    
            except:
                print("⚠️ 카드 번호 네 번째 필드를 찾을 수 없습니다.")
            
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"카드 정보 입력 실패: {e}")
            return False

    def set_card_expiry(self):
        """유효기간 설정 (실제 HTML select 태그 사용)"""
        try:
            print("유효기간 설정 중...")
            
            # config에서 유효기간 파싱 (MMYY 형식에서 MM, YY 분리)
            expiry = self.config['card_expiry']
            if len(expiry) == 4:
                month = expiry[:2]  # MM
                year = expiry[2:]   # YY
            else:
                print("❌ 유효기간 형식이 올바르지 않습니다. (MMYY 형식이어야 함)")
                return False
            
            # 월 선택
            try:
                month_select = Select(self.driver.find_element(By.ID, "crdVlidTrm1M"))
                month_select.select_by_value(month)
                print(f"유효기간(월) '{month}' 선택 완료")
            except:
                print(f"⚠️ 유효기간(월) '{month}' 선택 실패")
            
            # 년 선택
            try:
                year_select = Select(self.driver.find_element(By.ID, "crdVlidTrm1Y"))
                year_select.select_by_value(year)
                print(f"유효기간(년) '{year}' 선택 완료")
            except:
                print(f"⚠️ 유효기간(년) '{year}' 선택 실패")
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"유효기간 설정 실패: {e}")
            return False

    def set_installment(self):
        """할부개월 설정 (기본: 일시불)"""
        try:
            print("할부개월 설정 중...")
            
            # 일시불 선택 (기본값이지만 확실히 하기 위해)
            installment_select = Select(self.driver.find_element(By.ID, "ismtMnthNum1"))
            installment_select.select_by_value("0")  # 일시불
            print("할부개월 '일시불' 선택 완료")
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"할부개월 설정 실패: {e}")
            return False

    def enter_card_password(self):
        """카드 비밀번호 입력 (앞 2자리)"""
        try:
            print("카드 비밀번호 입력 중...")
            
            # 카드 비밀번호 입력 필드 (보안키패드)
            password_input = self.driver.find_element(By.ID, "vanPwd1")
            
            # 보안키패드 필드인지 확인
            if password_input.get_attribute('readonly'):
                print("⚠️ 비밀번호 필드는 보안키패드입니다.")
                try:
                    password_input.click()
                    time.sleep(1)
                    # JavaScript로 값 설정 시도
                    self.driver.execute_script(f"arguments[0].value = '{self.config['card_password']}';", password_input)
                    print("카드 비밀번호 입력 시도")
                except:
                    print("⚠️ 보안키패드 자동 입력 실패. 수동 입력이 필요합니다.")
            else:
                password_input.clear()
                password_input.send_keys(self.config['card_password'])
                print("카드 비밀번호 입력 완료")
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"카드 비밀번호 입력 실패: {e}")
            return False

    def enter_identification_number(self):
        """인증번호(주민등록번호 앞 6자리) 입력"""
        try:
            print("인증번호(주민등록번호 앞 6자리) 입력 중...")
            
            # 생년월일에서 주민등록번호 앞 6자리 생성
            # config의 birth_date가 YYMMDD 형식이라고 가정
            birth_date = self.config['birth_date']
            
            if len(birth_date) == 6:
                identification = birth_date  # 그대로 사용
            else:
                print("❌ 생년월일 형식이 올바르지 않습니다. (YYMMDD 형식이어야 함)")
                return False
            
            # 인증번호 입력 필드
            auth_input = self.driver.find_element(By.ID, "athnVal1")
            auth_input.clear()
            auth_input.send_keys(identification)
            print("인증번호 입력 완료")
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"인증번호 입력 실패: {e}")
            return False

    def click_final_payment_button_real(self):
        """실제 결제 페이지에서 최종 결제 버튼 클릭"""
        try:
            print("최종 결제 버튼 클릭 중...")
            
            # 결제하기 버튼 찾기 (form 제출 버튼이거나 특정 JavaScript 함수 호출)
            payment_button_selectors = [
                "//input[@type='submit']",
                "//button[contains(text(), '발권')]",
                "//button[contains(text(), '결제')]",
                "//a[contains(text(), '발권')]",
                "//a[contains(text(), '결제')]",
                "//input[contains(@value, '발권')]",
                "//input[contains(@value, '결제')]",
                "//input[contains(@onclick, 'requestIssueInfo')]"
            ]
            
            payment_button = None
            for selector in payment_button_selectors:
                try:
                    payment_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if payment_button.is_displayed():
                        break
                except:
                    continue
            
            if payment_button:
                # 버튼 클릭 전 잠시 대기
                time.sleep(2)
                
                # 스크롤하여 버튼을 보이게 함
                self.driver.execute_script("arguments[0].scrollIntoView();", payment_button)
                time.sleep(1)
                
                # 버튼 클릭
                self.driver.execute_script("arguments[0].click();", payment_button)
                print("결제 버튼 클릭 완료")
                
                # 결제 완료 대기 (결제 처리 시간)
                time.sleep(5)
                
                # 결제 완료 확인
                try:
                    success_indicators = [
                        "//*[contains(text(), '결제완료')]",
                        "//*[contains(text(), '발권완료')]", 
                        "//*[contains(text(), '예약완료')]",
                        "//*[contains(text(), '구매완료')]",
                        "//*[contains(text(), '승차권이 발권')]"
                    ]
                    
                    for indicator in success_indicators:
                        try:
                            success_element = self.driver.find_element(By.XPATH, indicator)
                            if success_element.is_displayed():
                                print("💳 결제가 완료되었습니다!")
                                return True
                        except:
                            continue
                            
                    print("⚠️ 결제 완료를 확인할 수 없습니다. 수동으로 확인해주세요.")
                    return True  # 일단 성공으로 처리
                    
                except:
                    print("⚠️ 결제 결과 확인 중 오류가 발생했습니다.")
                    return True
            else:
                print("❌ 결제 버튼을 찾을 수 없습니다.")
                return False
                
        except TimeoutException:
            print("❌ 결제 버튼을 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"결제 버튼 클릭 실패: {e}")
            return False
    
    def fill_passenger_info(self):
        """승객 정보 입력 - SRT는 로그인 정보로 자동 채워짐"""
        try:
            print("승객 정보 확인 중...")
            # SRT는 로그인한 사용자 정보가 자동으로 채워지므로 별도 작업 불필요
            time.sleep(1)
            print("승객 정보 확인 완료")
            return True
            
        except Exception as e:
            print(f"승객 정보 확인 실패: {e}")
            return False
    
    # 기존의 불필요한 함수들 제거 및 대체
    def select_payment_method(self):
        """결제 수단 선택 - 실제로는 기본적으로 신용카드 탭이 활성화되어 있음"""
        try:
            print("결제 수단 확인 중...")
            
            # 신용카드 탭이 활성화되어 있는지 확인
            card_tab = self.driver.find_element(By.ID, "chTab1")
            if "on" in card_tab.get_attribute("class"):
                print("신용카드 탭이 이미 선택되어 있습니다.")
            else:
                card_tab.click()
                print("신용카드 탭 선택 완료")
            
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"결제 수단 선택 실패: {e}")
            return False
    
    def fill_card_info(self):
        """카드 정보 입력"""
        try:
            print("카드 정보 입력 중...")
            
            # 카드 번호 입력
            try:
                card_number_input = self.wait.until(
                    EC.element_to_be_clickable((By.NAME, "cardNo"))
                )
                card_number_input.clear()
                card_number_input.send_keys(self.config['card_number'])
                print("카드 번호 입력 완료")
            except:
                print("⚠️ 카드 번호 입력 필드를 찾을 수 없습니다.")
            
            # 유효기간 입력
            try:
                expiry_input = self.driver.find_element(By.NAME, "validTerm")
                expiry_input.clear()
                expiry_input.send_keys(self.config['card_expiry'])
                print("유효기간 입력 완료")
            except:
                print("⚠️ 유효기간 입력 필드를 찾을 수 없습니다.")
            
            # 카드 비밀번호 입력 (앞 2자리)
            try:
                password_input = self.driver.find_element(By.NAME, "cardPwd")
                password_input.clear()
                password_input.send_keys(self.config['card_password'])
                print("카드 비밀번호 입력 완료")
            except:
                print("⚠️ 카드 비밀번호 입력 필드를 찾을 수 없습니다.")
            
            # 생년월일 입력
            try:
                birth_input = self.driver.find_element(By.NAME, "birthDay")
                birth_input.clear()
                birth_input.send_keys(self.config['birth_date'])
                print("생년월일 입력 완료")
            except:
                print("⚠️ 생년월일 입력 필드를 찾을 수 없습니다.")
            
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"카드 정보 입력 실패: {e}")
            return False
    
    def click_final_payment_button(self):
        """최종 결제 버튼 클릭"""
        try:
            print("최종 결제 버튼 클릭 중...")
            
            # 결제하기 버튼 찾기 및 클릭
            payment_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '결제하기') or contains(text(), '결제') or contains(text(), '구매하기')]"))
            )
            
            # 버튼 클릭 전 잠시 대기
            time.sleep(2)
            payment_button.click()
            print("결제 버튼 클릭 완료")
            
            # 결제 완료 대기 (결제 처리 시간)
            time.sleep(5)
            
            # 결제 완료 확인
            try:
                # 결제 완료 페이지 또는 메시지 확인
                success_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '결제완료') or contains(text(), '예약완료') or contains(text(), '구매완료')]")
                if success_elements:
                    print("💳 결제가 완료되었습니다!")
                    return True
                else:
                    print("⚠️ 결제 완료를 확인할 수 없습니다. 수동으로 확인해주세요.")
                    return True  # 일단 성공으로 처리
            except:
                print("⚠️ 결제 결과 확인 중 오류가 발생했습니다.")
                return True
            
        except TimeoutException:
            print("❌ 결제 버튼을 찾을 수 없습니다.")
            return False
        except Exception as e:
            print(f"결제 버튼 클릭 실패: {e}")
            return False
    
    # search_trains 함수도 함께 개선
    def search_trains(self):
        """열차 조회 과정 실행 (개선된 버전)"""
        print("\n=== 열차 조회 시작 ===")
        
        try:
            # 0. 로그인 상태 확인
            if not self.check_login_status():
                print("⚠️ 로그인 상태가 불확실합니다.")
            
            # 1. 예약 페이지로 이동
            if not self.navigate_to_booking_page():
                print("❌ 예약 페이지 이동 실패")
                return False
            
            # 페이지 안정화 대기
            time.sleep(1)
            
            # 2. 출발역 선택
            print("출발역 선택 시도...")
            retry_count = 0
            while retry_count < 3:
                if self.select_departure_station():
                    break
                retry_count += 1
                print(f"출발역 선택 재시도 {retry_count}/3")
                time.sleep(1)
            else:
                print("❌ 출발역 선택 최종 실패")
                return False
            
            # 3. 도착역 선택
            if not self.select_arrival_station():
                print("❌ 도착역 선택 실패")
                return False
            
            # 4. 출발 날짜 선택
            if not self.select_departure_date():
                print("❌ 출발 날짜 선택 실패")
                return False
            
            # 5. 출발 시간 선택
            if not self.select_departure_time():
                print("❌ 출발 시간 선택 실패")
                return False
            
            # 6. 승객 수 설정
            if not self.set_passenger_count():
                print("❌ 승객 수 설정 실패")
                return False
            
            # 7. 간편조회하기 버튼 클릭
            if not self.click_search_button():
                print("❌ 간편조회하기 버튼 클릭 실패")
                return False
            
            print("✅ 열차 조회 완료")
            return True
            
        except Exception as e:
            print(f"열차 조회 과정에서 오류 발생: {e}")
            # 현재 페이지 정보 출력 (디버깅용)
            try:
                current_url = self.driver.current_url
                page_title = self.driver.title
                print(f"오류 발생 시 현재 URL: {current_url}")
                print(f"오류 발생 시 페이지 제목: {page_title}")
            except:
                pass
            return False
    
    def login(self):
        """전체 로그인 프로세스 실행"""
        if not self.config:
            return False
            
        print("=== SRT 자동 로그인 시작 ===")
        
        # 1. 웹드라이버 설정
        if not self.setup_driver():
            return False
        
        try:
            # 2. 로그인 페이지로 이동
            if not self.navigate_to_login_page():
                return False
            
            # 3. 휴대전화번호 로그인 옵션 선택
            if not self.select_phone_login_option():
                return False
            
            # 4. 로그인 정보 입력
            if not self.enter_login_credentials():
                return False
            
            # 5. 로그인 버튼 클릭
            if not self.click_login_button():
                return False
            
            # 6. 로그인 결과 확인
            if self.wait_for_login_result():
                print("=== 로그인 성공 ===")
                return True
            else:
                print("=== 로그인 실패 ===")
                return False
                
        except Exception as e:
            print(f"로그인 과정에서 오류 발생: {e}")
            return False
    
    def run_continuous_booking_attempt(self):
        """특정 시간대 열차를 계속해서 예약 시도하는 메인 함수"""
        final_result = False
        try:
            # 1. 로그인 수행
            if not self.login():
                print("로그인에 실패했습니다. 프로그램을 종료합니다.")
                return False
            
            # 2. 최초 열차 조회
            if not self.search_trains():
                print("열차 조회에 실패했습니다. 프로그램을 종료합니다.")
                return False
            
            retry_count = 0
            max_retries = self.config['max_retry_count']
            retry_interval = self.config['retry_interval']
            
            print(f"\n=== 특정 시간대 예약 시도 시작 ===")
            print(f"목표 시간: {self.config['preferred_departure_time']}")
            print(f"재시도 간격: {retry_interval}초")
            if max_retries > 0:
                print(f"최대 재시도 횟수: {max_retries}회")
            else:
                print("최대 재시도 횟수: 무제한")
            print("=" * 50)
            
            while True:
                retry_count += 1
                print(f"\n[{retry_count}번째 시도] {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 특정 시간대 열차 예약 시도
                result = self.find_and_book_specific_time_train()
                
                if result in ["reservation_success", "payment_success"]:
                    if result == "payment_success":
                        print("\n🎉 예약 및 결제에 성공했습니다!")
                        print("결제가 완료되었습니다. 예약 내역을 확인해주세요.")
                    else:
                        print("\n🎉 예약에 성공했습니다!")
                        print("예약 절차를 계속 진행해주세요.")

                    self.catch_sound()
                    final_result = True
                    return True
                elif result == "waitlist_success":
                    print("\n⏳ 예약 신청 버튼 클릭!")
                    wait_result = self.book_wait()
                    if wait_result:
                        print("\n⏳ 예약대기 신청이 완료되었습니다!")
                        print("예약대기 절차를 계속 진행해주세요.")
                        self.catch_sound()
                        final_result = True
                        return True
                    else:
                        print("\n❌ 예약대기 신청이 실패하였습니다")
                        return False
                    
                elif result == "sold_out":
                    print(f"😔 원하는 시간대 열차가 매진입니다. {retry_interval}초 후 재시도...")
                elif result == "unavailable":
                    print(f"❌ 해당 시간대 열차 예약이 불가능합니다. {retry_interval}초 후 재시도...")
                elif result == "not_found":
                    print(f"🔍 해당 시간대 열차를 찾을 수 없습니다. {retry_interval}초 후 재시도...")
                elif result == "payment_failed":
                    print(f"💳 예약은 성공했으나 결제에 실패했습니다. 수동으로 결제를 완료해주세요.")
                    self.catch_sound()
                    final_result = True
                    return True
                else:  # timeout or error
                    print(f"⚠️ 오류가 발생했습니다. {retry_interval}초 후 재시도...")
                
                # 최대 재시도 횟수 체크 (0이면 무제한)
                if max_retries > 0 and retry_count >= max_retries:
                    print(f"\n최대 재시도 횟수 ({max_retries}회)에 도달했습니다.")
                    print("프로그램을 종료합니다.")
                    return False
                
                # 대기 시간 (사용자가 중단할 수 있도록 초씩 카운트다운)
                self.wait_count(retry_interval)
                
                # 현재 페이지에서 새로고침 또는 재조회
                if not self.refresh_current_search():
                    print("조회 새로고침에 실패했습니다. 계속 시도...")
                    continue
            
        except KeyboardInterrupt:
            print("\n\n사용자에 의해 중단되었습니다.")
            return False
        except Exception as e:
            traceback.print_exc()
            print(f"예상치 못한 오류 발생: {e}")
            return False
        finally:
            # 브라우저 종료
            if final_result == True:
                self.close()
            

    def wait_count(self, retry_interval):
        remaining = float(retry_interval)

        if remaining.is_integer():
            # 정수 초 → 1초 단위로 카운트
            for i in range(int(remaining), 0, -1):
                print(f"\r다음 시도까지 {i}초 대기 중... (Ctrl+C로 중단)", end="", flush=True)
                time.sleep(1)
        else:
            if remaining > 1:
                # 1보다 큰 실수 → 정수 부분은 1초씩, 마지막 소수 부분만큼 sleep
                int_part = int(remaining)
                frac_part = remaining - int_part

                for i in range(int_part, 0, -1):
                    print(f"\r다음 시도까지 {i}초 대기 중... (Ctrl+C로 중단)", end="", flush=True)
                    time.sleep(1)

                if frac_part > 0:
                    print(f"\r다음 시도까지 {frac_part:.1f}초 대기 중... (Ctrl+C로 중단)", end="", flush=True)
                    time.sleep(frac_part)

            else:
                # 1 이하 실수 → 바로 해당 시간만 sleep
                print(f"\r다음 시도까지 {remaining:.1f}초 대기 중... (Ctrl+C로 중단)", end="", flush=True)
                time.sleep(remaining)

        print()

    def catch_sound(self):
        try:
            # mp3 파일 경로 (현재 파일과 동일한 폴더)
            mp3_path = os.path.join(os.path.dirname(__file__), "catch.mp3")

            # 파일이 존재하면 재생
            if os.path.exists(mp3_path):
                playsound(mp3_path)
            else:
                print("⚠️ 사운드 파일이 없습니다:", mp3_path)
        except Exception as e:
            traceback.print_exc()
            print("sound error")
            print(e)

    def refresh_current_search(self):
        """현재 검색 결과 페이지에서 새로고침하는 함수"""
        try:
            print("검색 결과 새로고침 중...")
            
            # 방법 1: 페이지 새로고침 (가장 간단)
            try:
                self.driver.refresh()
                # time.sleep(0.5)
                # 테이블이 로드되었는지 확인
                # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
                print("✅ 페이지 새로고침 완료")
                return True
                
                
                
            except Exception as e:
                print(f"페이지 새로고침 실패: {e}")
            
            # 방법 2: 조회 버튼이 있다면 클릭
            try:
                # 조회 버튼 찾기 (다양한 셀렉터 시도)
                search_button_selectors = [
                    "input[value='조회']",
                    "button:contains('조회')",
                    "input[type='submit'][value*='조회']",
                    ".btn_search",
                    "#search-btn",
                    "input.btn_midium[value='조회']"
                ]
                
                for selector in search_button_selectors:
                    try:
                        if selector.startswith("button:contains"):
                            # contains는 직접 지원되지 않으므로 XPath 사용
                            buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '조회')]")
                            if buttons:
                                button = buttons[0]
                        else:
                            button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if button and button.is_displayed() and button.is_enabled():
                            print(f"조회 버튼 클릭: {selector}")
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(0.5)
                            
                            # 테이블이 로드되었는지 확인
                            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
                            # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
                            print("✅ 조회 버튼 클릭으로 새로고침 완료")
                            return True
                            
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"조회 버튼 클릭 실패: {e}")
            
            # 방법 3: F5 키 입력으로 새로고침
            try:
                from selenium.webdriver.common.keys import Keys
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.F5)
                time.sleep(3)
                
                # 테이블이 로드되었는지 확인
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
                print("✅ F5 키로 새로고침 완료")
                return True
                
            except Exception as e:
                print(f"F5 키 새로고침 실패: {e}")
            
            # 방법 4: JavaScript로 form 재제출
            try:
                # result-form이 있다면 재제출
                form = self.driver.find_element(By.ID, "result-form")
                if form:
                    self.driver.execute_script("document.getElementById('result-form').submit();")
                    time.sleep(3)
                    
                    # 테이블이 로드되었는지 확인
                    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
                    print("✅ form 재제출로 새로고침 완료")
                    return True
                    
            except Exception as e:
                print(f"form 재제출 실패: {e}")
            
            # 방법 5: 현재 URL 다시 로드
            try:
                current_url = self.driver.current_url
                self.driver.get(current_url)
                time.sleep(3)
                
                # 테이블이 로드되었는지 확인
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
                print("✅ URL 재로드로 새로고침 완료")
                return True
                
            except Exception as e:
                print(f"URL 재로드 실패: {e}")
            
            print("❌ 모든 새로고침 방법이 실패했습니다.")
            return False
            
        except Exception as e:
            print(f"새로고침 중 예상치 못한 오류: {e}")
            return False

    def refresh_search_with_ajax(self):
        """AJAX를 이용한 부분 새로고침 (SRT 사이트가 AJAX를 사용하는 경우)"""
        try:
            # SRT 웹사이트의 AJAX 패턴에 맞춰 구현
            # 실제 네트워크 탭에서 확인한 AJAX 요청을 재현
            
            print("AJAX 요청으로 검색 결과 갱신 중...")
            
            # JavaScript로 AJAX 요청 실행
            ajax_script = """
            // SRT 사이트의 실제 AJAX 함수 호출
            if (typeof selectScheduleList === 'function') {
                selectScheduleList();
            } else if (typeof searchTrain === 'function') {
                searchTrain();
            } else {
                // 일반적인 form 재제출
                var form = document.getElementById('result-form');
                if (form) {
                    form.submit();
                }
            }
            """
            
            self.driver.execute_script(ajax_script)
            time.sleep(3)
            
            # 테이블 업데이트 확인
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_wrap")))
            print("✅ AJAX로 검색 결과 갱신 완료")
            return True
            
        except Exception as e:
            print(f"AJAX 갱신 실패: {e}")
            return False
        
    def book_wait(self):
        phone_number = self.config['phone_number']
        phone_parts = [phone_number[:3], phone_number[3:7], phone_number[7:]]

        try:
            
            
            # SMS 알림서비스 신청 '예' 라디오 버튼 클릭
            sms_yes_radio = self.driver.find_element(
                By.XPATH, "//input[@type='radio' and @name='smsSndFlg' and @value='Y']"
            )
            sms_yes_radio.click()
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = Alert(self.driver)
            alert.accept()
            
            # 1) UI selectmenu 버튼 클릭
            dropdown_btn = self.driver.find_element(By.CSS_SELECTOR, "a.ui-selectmenu-button")
            dropdown_btn.click()

            # 2) 옵션 리스트가 뜰 때까지 최대 5초 대기
            # 옵션 XPath (텍스트로 선택)
            option_text = phone_parts[0]  # 예: '010'
            option_xpath = f"//ul[@id='ui-id-1-menu']//a[normalize-space(text())='{option_text}']"

            # 옵션이 클릭 가능할 때까지 대기
            wait = WebDriverWait(self.driver, 5)
            wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))

            # 옵션 클릭
            option = self.driver.find_element(By.XPATH, option_xpath)
            option.click()

            # 3) 중간 번호 입력
            mid_input = self.driver.find_element(By.ID, "phoneNum1")
            mid_input.clear()
            mid_input.send_keys(phone_parts[1])

            # 4) 마지막 번호 입력
            last_input = self.driver.find_element(By.ID, "phoneNum2")
            last_input.clear()
            last_input.send_keys(phone_parts[2])
            
            # 차실 변경 관련 선택 '예' 라디오 버튼 클릭
            change_car_yes_radio = self.driver.find_element(
                By.XPATH, "//input[@type='radio' and @name='psrmClChgFlg' and @value='Y']"
            )
            change_car_yes_radio.click()

            btn_confirm = self.driver.find_element(By.ID, "moveTicketList")
            btn_confirm.click()

            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = Alert(self.driver)
            alert_text = alert.text
            print("Alert 메시지:", alert_text)
            alert.accept()  # 확인 누르기

            return True
        except Exception as e:
            traceback.print_exc()
            print(f"예약 대기 신청 오류 발생: {e}")
            return False

    def close(self):
        """브라우저 종료"""
        """성공했을때만 바로 끔"""
        if self.driver:
            self.driver.quit()
            print("브라우저 종료됨")


def main():
    """메인 실행 함수"""
    # SRT 예약 객체 생성
    srt_booking = SRTAutoBooking()
    
    try:
        # 특정 시간대 연속 예약 시도 실행
        success = srt_booking.run_continuous_booking_attempt()
        
        if success:
            print("\n🎉 예약 프로세스가 완료되었습니다!")
            print("브라우저에서 예약을 완료해주세요.")
            input("계속하려면 Enter를 누르세요...")
        else:
            print("\n❌ 예약 프로세스가 실패했습니다.")
            input("프로그램을 종료하려면 Enter를 누르세요...")
            srt_booking.close()
            
            
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
        input("프로그램을 종료하려면 Enter를 누르세요...")
        srt_booking.close()
        return False
    except Exception as e:
        print(f"예약 시도 과정에서 오류 발생: {e}")
        input("프로그램을 종료하려면 Enter를 누르세요...")
        srt_booking.close()
        return False


if __name__ == "__main__":
    main()
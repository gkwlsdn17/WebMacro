import datetime
import urllib.request
from urllib.request import urlretrieve
from PIL import Image
import easyocr
import cv2
from selenium import webdriver
import time
import CODE
import copy
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import traceback

seat_jump = ""
seat_jump_count = 0
seat_jump_special_repeat = ""
seat_jump_special_repeat_count = 0

def login(driver,id, pw):

    driver.get("https://member.melon.com/muid/family/ticket/login/web/login_informM.htm")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'id')))
    driver.find_element(By.ID,'id').send_keys(id)
    driver.find_element(By.ID,'pwd').send_keys(pw)
    time.sleep(0.5)
    driver.find_element(By.ID,'btnLogin').click()

    time.sleep(0.3)

def check_alert(driver):
    try:
        if driver.find_element(By.ID,'noticeAlert').is_displayed() == 1:
            driver.find_element(By.ID,'noticeAlert_layerpopup_close').click()
    except Exception as e:
        print(e)

    try:
        alert = Alert(driver)
        # 이미 Alert이 떠 있는 경우, accept() 메서드를 사용하여 Alert을 수락하거나 dismiss() 메서드를 사용하여 Alert을 취소할 수 있습니다.
        # 예시: alert.accept()
        alert.accept()
        print("Alert is present")
    except:
        print("Alert is not present")

def select_date(driver, config):
    success = True
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'list_date')))
    date_list = driver.find_elements(By.XPATH,'//*[@id="list_date"]/li')
    print(f'date_list: {date_list}')
    for li in date_list:
        print(li.get_attribute('data-perfday'))
        if config['bookInfo']['book_date'] == li.get_attribute('data-perfday'):
            print('date click')
            try:
                li.click()
                break
            except Exception as e:
                print(f'select_date list_date/li error:{e}')
                btn = driver.find_element(By.CSS_SELECTOR, f'button.ticketCalendarBtn[data-perfday="{config["bookInfo"]["bookDate"]}"]')
                btn.click()
                break
            
    try:
        time.sleep(0.3)
        time_list = driver.find_elements(By.XPATH,'//*[@id="list_time"]/li')
        for li in time_list:
            print(li.find_element(By.CSS_SELECTOR,'button > span').get_attribute('innerHTML').split(" "))
            times = li.find_element(By.CSS_SELECTOR,'button > span').get_attribute('innerHTML').split(" ")
            book_time = times[0][0:2] + times[1][0:2]
            if config['bookInfo']['bookTime'] == book_time:
                print("time ok")
                li.click()
                break

        driver.find_element(By.XPATH, '//*[@id="ticketReservation_Btn"]').click()
        time.sleep(1)
    except Exception as e:
        print(f"select_date part 2 error: {e}")
        success = False
    return success

def certification(driver, img_folder_path):
    i = 0
    try:
        while driver.find_element(By.ID,'certification').is_displayed() == 1:
            i += 1
            print(f"check: {i}")
            if i > 10:
                break
            image_check(driver, img_folder_path)
            if driver.find_element(By.ID,'certification').is_displayed() == 1:
                driver.find_element(By.ID,'btnReload').click()
                driver.find_element(By.ID,'label-for-captcha').clear()
                # time.sleep(0.1)
        print(driver.find_element(By.ID,'certification').is_displayed())
    except:
        print("no certification")

def image_check(driver, img_folder_path):
    capchaImg = driver.find_element(By.ID,'captchaImg')

    img_src = capchaImg.get_attribute('src')
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    img_file_path = f'./{img_folder_path}/{file_name}.png'
    urlretrieve(img_src, img_file_path)

    foreground = Image.open(img_file_path)
    width, height = foreground.size
    background = Image.new("RGBA", (width, height), color="#FFF")
    Image.alpha_composite(background, foreground).save('composite_img.png')

    # time.sleep(0.1)
    img = cv2.imread('composite_img.png')

    reader = easyocr.Reader(['en'], gpu=True)
    result = reader.readtext(img, detail=0)
    print(result[0])
    driver.find_element(By.ID,'label-for-captcha').send_keys(result[0])
    driver.find_element(By.ID,'btnComplete').click()

def select_seat(driver, config_grade_area, config_special_area, bool_special_area):
    grade_summary = driver.find_elements(By.CSS_SELECTOR,'#divGradeSummary > tr')
    print(f'len(grade_summary):{len(grade_summary)}')
    if len(grade_summary) != 0:
        if bool_special_area == "Y" and len(config_grade_area) > 0:
            # 짝수 index는 grade고 홀수 index는 실제 좌석있는 부분
            grade_index_list = [i for config_item in config_grade_area for i, grade in enumerate(grade_summary) if config_item in grade.text and i%2 == 0]
            if len(grade_index_list) == 0:
                return CODE.AREA_ERROR
            print_debug("---------------------------------------")
            for g in grade_index_list:
                print_debug(grade_summary[g].text)
            print_debug("---------------------------------------")
        else:
            grade_index_list = [i for i, grade in enumerate(grade_summary) if i%2 == 0]

        for idx in grade_index_list:
            tmp_special_area = copy.deepcopy(config_special_area)
            tr = grade_summary[idx]
            print_debug(tr.text)
            tr.click()
            time.sleep(0.1)
            box_list_area = grade_summary[idx+1]
            area_list = box_list_area.find_elements(By.CSS_SELECTOR,'td > div > ul > li')
            print_debug(f'len(area_list):{len(area_list)}')
            if len(tmp_special_area) == 0:
                tmp_special_area.append("")
            print_debug(f'config_special_area:{tmp_special_area}')
            
            while len(tmp_special_area) > 0:
                try:
                    if len(tmp_special_area) > 1 or tmp_special_area[0] != "":
                        new_area_list = [area for area in area_list if tmp_special_area[0] in area.text]
                        print_debug(f'len(new area_list):{len(new_area_list)} , tmp_special_area[0]:{tmp_special_area[0]}')
                        res = select_box(driver, new_area_list, tmp_special_area[0])
                    else:
                        res = select_box(driver, area_list, tmp_special_area[0])
                    print_debug(f"RESULT: {res}")
                    if res == CODE.EMPTY:
                        tmp_special_area.pop(0)
                        continue
                    elif res == CODE.CONFLICT:
                        return CODE.CONFLICT
                    else:
                        return CODE.SUCCESS
                except Exception as e:
                    print("select_seat error:")
                    print(e)
                    break
            
        return res
    else:
        print_debug("grade 없음")
        res = select_rect(driver)
        return res

def select_box(driver, li_list, choice=""):
    time.sleep(0.15)
    for i in li_list:
        print_debug(f'area = {i.text}')
        area = i.find_element(By.CLASS_NAME,'area_tit').text.strip()
        print_debug(area + ' choice: ' + choice)

        if choice == "":
            i.click()
            res = select_rect(driver)
            if res == CODE.SUCCESS:
                return CODE.SUCCESS
            elif res == CODE.CONFLICT:
                return CODE.CONFLICT
            else:
                continue
        else:
            if choice in area:
                i.click()
                res = select_rect(driver)
                if res == CODE.SUCCESS:
                    return CODE.SUCCESS
                elif res == CODE.CONFLICT:
                    return CODE.CONFLICT
                else:
                    break

    return CODE.EMPTY
def select_rect(driver):
    # WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
    #     (By.ID, 'ez_canvas')))
    seats = driver.execute_script("""
        const seats = document.querySelectorAll('#ez_canvas > svg > rect:not([fill="#DDDDDD"]):not([fill="none"])');
        const sortedSeats = Array.from(seats).sort((a, b) => parseFloat(a.getAttribute('y')) - parseFloat(b.getAttribute('y')));
        return sortedSeats;
        
    """)


    # seats = driver.find_element(By.CSS_SELECTOR,'#ez_canvas > svg > rect:not([fill="#DDDDDD"]):not([fill="none"])')
    print_debug(f"len(seats): {len(seats)}")

    if len(seats) == 0:
        print_debug("select_rect Return EMPTY")
        return CODE.EMPTY

    # if len(seats) < 1000:
        # print("sort!")
        # seats.sort(key=lambda rect: float(rect.get_attribute('y')))


    try:
        print("챱")
        if seat_jump == 'Y' and (len(seats) > seat_jump_count > 0):
            print(seats[seat_jump_count].get_attribute("x"), seats[seat_jump_count].get_attribute("y"))
            seats[seat_jump_count].click()
        else:
            print(seats[0].get_attribute("x"), seats[0].get_attribute("y"))
            seats[0].click()
        driver.find_element(By.ID,'nextTicketSelection').click()
    except Exception as e:
        print(f"seat read error: {e}")
        return CODE.CONFLICT

    try:
        alert = Alert(driver)
        alert_text = alert.text  # alert 메시지 텍스트 얻기
        # 띄어쓰기 제거 후 "다른" 단어가 포함됐는지 체크
        alert_text_no_space = alert_text.replace(" ", "")
        if "다른" in alert_text_no_space:
            print("Alert에 '다른' 문구가 포함됨")
            alert.accept()
            return CODE.CONFLICT
        else:
            print("Alert는 있으나 '다른' 문구는 없음")
            alert.dismiss()  # 또는 alert.accept() 상황에 따라 선택
            return CODE.SUCCESS  # 다른 분기용 코드
    except:
        print("Alert가 없음")
        return CODE.SUCCESS
    
def payment1(driver):
    # 결제창 티켓 선택 프로세스
    try:
         # 먼저 alert이 있는지 확인하고 처리
        try:
            alert = Alert(driver)
            # 이미 Alert이 떠 있는 경우, accept() 메서드를 사용하여 Alert을 수락하거나 dismiss() 메서드를 사용하여 Alert을 취소할 수 있습니다.
            # 예시: alert.accept()
            alert.accept()
            print("payment1 Alert is present")
        except:
            print("payment1 Alert is not present")

        try:
            # 기존에 iframe 안에 있다면 메인 컨텐츠로 먼저 나가기
            driver.switch_to.default_content()
        except:
            pass
            
        # iframe으로 전환
        wait = WebDriverWait(driver, 10)
        iframe = wait.until(EC.presence_of_element_located((By.ID, "oneStopFrame")))
        driver.switch_to.frame(iframe)
        print("payment1: oneStopFrame iframe으로 전환 완료")
        
        # 기본가 select 요소 찾기 (dt에서 "기본가" 텍스트를 포함하는 요소의 부모에서 select 찾기)
        basic_price_select = driver.find_element(By.XPATH, "//dt[contains(text(), '기본가')]/../../..//select")
        
        # Select 객체로 래핑
        
        select_obj = Select(basic_price_select)
        
        # 1매 선택
        select_obj.select_by_value("1")
        print("매수 선택 완료")
        
        # 잠시 대기 (페이지 업데이트를 위해)
        time.sleep(2)
        
        # 다음 버튼 클릭
        next_button = driver.find_element(By.ID, "nextPayment")
        next_button.click()
        return True
        
    except Exception as e:
        return False
    finally:
        try:
            driver.switch_to.default_content()
            print("payment1: default content로 전환 완료")
        except Exception:
            pass
    

def payment2(driver, phone):
    """
    멜론 티켓 결제 화면을 자동으로 완료하는 함수
    """
    try:
        wait = WebDriverWait(driver, 10)

        print("결제 화면 시작")
        
        # 1. 수령방법 선택 (배송 선택)
        try:
            # 배송 라디오 버튼 찾기 (텍스트에 "배송"이 포함된 것)
            delivery_options = driver.find_elements(By.XPATH, "//input[@type='radio' and @name='deliveryType']")
            for option in delivery_options:
                # 라벨 텍스트 확인
                label = driver.find_element(By.XPATH, f"//label[@for='{option.get_attribute('id')}']")
                if "배송" in label.text:
                    option.click()
                    print("수령방법: 배송 선택 완료")
                    break
        except Exception as e:
            print("결제 화면 오류: 수령방법 선택 중 오류")
            print(e)
            return False
        
        time.sleep(1)
        
        # 2. 결제수단 선택 (무통장입금)
        try:
            # 무통장입금 라디오 버튼 선택
            bank_transfer = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and contains(@value, 'bank') or contains(@id, 'bank') or contains(@name, 'payMethod')]")))
            
            # 무통장입금 관련 라디오 버튼들 찾기
            payment_options = driver.find_elements(By.XPATH, "//input[@type='radio' and @name='payMethod']")
            for option in payment_options:
                label = driver.find_element(By.XPATH, f"//label[@for='{option.get_attribute('id')}']")
                if "무통장" in label.text or "계좌이체" in label.text or "입금" in label.text:
                    option.click()
                    print("결제수단: 무통장입금 선택 완료")
                    break
        except Exception as e:
            traceback.print_exc()
            print(f"결제수단 선택 중 오류: {e}")
            return False
        
        time.sleep(1)
        
        # 3. 입금은행 선택 (농협은행)
        try:
            # 은행 선택 드롭다운 찾기
            bank_select = driver.find_element(By.XPATH, "//select[contains(@name, 'bank') or contains(@id, 'bank')]")
            select_element = Select(bank_select)
            
            # 농협은행 옵션 찾기
            for option in select_element.options:
                if "농협" in option.text:
                    select_element.select_by_visible_text(option.text)
                    print("입금은행: 농협은행 선택 완료")
                    break
        except Exception as e:
            print(f"입금은행 선택 중 오류: {e}")
            return False
        
        time.sleep(1)
        
        # 4. 현금영수증 소득공제 선택
        try:
            # 현금영수증 소득공제 라디오 버튼 선택
            receipt_options = driver.find_elements(By.XPATH, "//input[@type='radio' and contains(@name, 'receipt') or contains(@name, 'cashReceipt')]")
            for option in receipt_options:
                label = driver.find_element(By.XPATH, f"//label[@for='{option.get_attribute('id')}']")
                if "소득공제" in label.text:
                    option.click()
                    print("현금영수증: 소득공제 선택 완료")
                    break
        except Exception as e:
            print(f"현금영수증 선택 중 오류: {e}")
            return False
        
        time.sleep(1)
        
        # 5. 휴대폰번호 입력
        try:
            
            # 휴대폰번호를 3부분으로 분리
            phone1 = phone[:3]    # "010"
            phone2 = phone[3:7]   # "1234"
            phone3 = phone[7:]    # "5678"
            
            # 휴대폰번호 첫 번째 부분 (통신사 번호)
            phone1_select = driver.find_element(By.XPATH, "//select[contains(@name, 'phone1') or contains(@name, 'hp1')]")
            select_phone1 = Select(phone1_select)
            select_phone1.select_by_value(phone1)
            
            # 휴대폰번호 두 번째 부분
            phone2_input = driver.find_element(By.XPATH, "//input[contains(@name, 'phone2') or contains(@name, 'hp2')]")
            phone2_input.clear()
            phone2_input.send_keys(phone2)
            
            # 휴대폰번호 세 번째 부분
            phone3_input = driver.find_element(By.XPATH, "//input[contains(@name, 'phone3') or contains(@name, 'hp3')]")
            phone3_input.clear()
            phone3_input.send_keys(phone3)
            
            print(f"휴대폰번호 입력 완료: {phone1}-{phone2}-{phone3}")
            
        except Exception as e:
            print(f"휴대폰번호 입력 중 오류: {e}")
            return False
        
        time.sleep(1)
        
        # 6. 예매자동의 전체동의 체크박스 선택
        try:
            # 전체동의 체크박스 찾기
            agree_all_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox' and (contains(@id, 'agreeAll') or contains(@id, 'allAgree') or contains(@name, 'agreeAll'))]")
            if not agree_all_checkbox.is_selected():
                agree_all_checkbox.click()
                print("예매자동의 전체동의 체크 완료")
        except Exception as e:
            # 전체동의가 없는 경우 개별 동의 체크박스들을 찾아서 체크
            try:
                agree_checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and contains(@name, 'agree')]")
                for checkbox in agree_checkboxes:
                    if not checkbox.is_selected():
                        checkbox.click()
                print("개별 동의 체크박스 모두 체크 완료")
            except Exception as e2:
                print(f"동의 체크박스 선택 중 오류: {e2}")
                return False
        
        time.sleep(1)
        
        # 7. 결제하기 버튼 클릭
        try:
            # 결제하기 버튼 찾기 및 클릭
            payment_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '결제') or contains(@id, 'payment') or contains(@class, 'payment')] | //input[@type='button' and contains(@value, '결제')] | //a[contains(text(), '결제')]")))
            payment_button.click()
            print("결제하기 버튼 클릭 완료")
            
            # 결제 완료 대기 (몇 초 대기)
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"결제하기 버튼 클릭 중 오류: {e}")
            return False
    
    except TimeoutException:
        print("페이지 로딩 시간 초과")
        return False
    except Exception as e:
        print(f"결제 자동화 중 예상치 못한 오류: {e}")
        return False
    finally:
        # iframe에서 나오기
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        

def print_debug(msg):
    print(msg)
    pass
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

        iframe = wait.until(EC.presence_of_element_located((By.ID, "oneStopFrame")))
        driver.switch_to.frame(iframe)
        print("payment2: oneStopFrame iframe으로 전환 완료")
        
        # 1. 수령방법 선택 (배송 선택) - 수정된 버전
        try:
            # 먼저 페이지가 완전히 로드될 때까지 대기
            time.sleep(2)
            
            # 배송 옵션들의 상태 확인
            delivery_options = wait.until(EC.presence_of_all_elements_located((By.NAME, "delvyTypeCode")))
            
            print("=== 배송 옵션 상태 확인 ===")
            for option in delivery_options:
                option_value = option.get_attribute('value')
                is_disabled = option.get_attribute('disabled')
                option_id = option.get_attribute('id')
                
                # 해당 라벨 텍스트 찾기
                try:
                    label_span = driver.find_element(By.ID, f"delvyTypeName{option_value}")
                    label_text = label_span.text.strip()
                    print(f"옵션 {option_value}: {label_text}, 비활성화: {is_disabled is not None}")
                except:
                    print(f"옵션 {option_value}: 라벨 찾기 실패, 비활성화: {is_disabled is not None}")
            
            # 배송 옵션 (DV0003) 선택 시도
            delivery_option = None
            
            # 방법 1: 직접 value로 찾기
            try:
                delivery_option = driver.find_element(By.XPATH, "//input[@name='delvyTypeCode' and @value='DV0003']")
                
                # disabled 속성 확인
                if delivery_option.get_attribute('disabled'):
                    print("배송 옵션이 비활성화되어 있습니다.")
                    
                    # JavaScript로 강제로 활성화 시도
                    driver.execute_script("arguments[0].removeAttribute('disabled');", delivery_option)
                    driver.execute_script("arguments[0].disabled = false;", delivery_option)
                    time.sleep(1)
                    
                    # 라벨의 스타일도 변경
                    label_span = driver.find_element(By.ID, "delvyTypeNameDV0003")
                    driver.execute_script("arguments[0].style.color = '';", label_span)
                    
                # 클릭 시도
                if delivery_option.is_enabled():
                    # 여러 방법으로 클릭 시도
                    try:
                        delivery_option.click()
                        print("배송 옵션 선택 완료 (일반 클릭)")
                    except:
                        try:
                            driver.execute_script("arguments[0].click();", delivery_option)
                            print("배송 옵션 선택 완료 (JavaScript 클릭)")
                        except:
                            # 강제로 checked 상태로 변경
                            driver.execute_script("arguments[0].checked = true;", delivery_option)
                            # onChange 이벤트 트리거
                            driver.execute_script("setDeliveryType('DV0003');")
                            print("배송 옵션 선택 완료 (강제 설정)")
                else:
                    print("배송 옵션이 여전히 비활성화 상태입니다.")
                    
            except Exception as inner_e:
                print(f"배송 옵션 선택 실패: {inner_e}")
                
                # 대안: 사용 가능한 다른 옵션 선택
                print("=== 사용 가능한 옵션 찾기 ===")
                for option in delivery_options:
                    if not option.get_attribute('disabled'):
                        option_value = option.get_attribute('value')
                        try:
                            label_span = driver.find_element(By.ID, f"delvyTypeName{option_value}")
                            label_text = label_span.text.strip()
                            print(f"사용 가능한 옵션: {option_value} - {label_text}")
                            
                            # 첫 번째 사용 가능한 옵션 선택
                            option.click()
                            print(f"옵션 {label_text} 선택 완료")
                            break
                        except Exception as e:
                            print(f"옵션 선택 실패: {e}")
                            continue
                else:
                    print("사용 가능한 배송 옵션이 없습니다.")
                    return False

        except Exception as e:
            traceback.print_exc()
            print(f"결제 화면 오류: 수령방법 선택 중 오류: {e}")
            return False
        
        time.sleep(1)
        
        # 2. 결제수단 선택 (무통장입금) - 수정된 버전
        try:
            # 페이지 로드 대기
            time.sleep(2)
            
            # 결제수단 옵션들 확인
            payment_options = wait.until(EC.presence_of_all_elements_located((By.NAME, "payMethodCode")))
            
            print("=== 결제수단 옵션 확인 ===")
            for option in payment_options:
                option_value = option.get_attribute('value')
                option_id = option.get_attribute('id')
                is_disabled = option.get_attribute('disabled')
                
                try:
                    # 라벨 텍스트 찾기
                    if option_id:
                        label = driver.find_element(By.XPATH, f"//label[@for='{option_id}']//span[@class='txt_lab']")
                        label_text = label.text.strip()
                        print(f"옵션 {option_value}: {label_text}, 비활성화: {is_disabled is not None}")
                    else:
                        print(f"옵션 {option_value}: ID 없음, 비활성화: {is_disabled is not None}")
                except Exception as e:
                    print(f"옵션 {option_value}: 라벨 찾기 실패 - {e}")
            
            # 무통장입금 선택 (value="AP0003")
            try:
                bank_transfer_option = driver.find_element(By.XPATH, "//input[@name='payMethodCode' and @value='AP0003']")
                
                # 비활성화 상태 확인
                if bank_transfer_option.get_attribute('disabled'):
                    print("무통장입금 옵션이 비활성화되어 있습니다.")
                    return False
                
                # 클릭 시도
                try:
                    # 일반 클릭
                    bank_transfer_option.click()
                    print("결제수단: 무통장입금 선택 완료 (일반 클릭)")
                except:
                    try:
                        # JavaScript 클릭
                        driver.execute_script("arguments[0].click();", bank_transfer_option)
                        print("결제수단: 무통장입금 선택 완료 (JavaScript 클릭)")
                    except:
                        # 강제로 체크 상태로 변경하고 이벤트 호출
                        driver.execute_script("arguments[0].checked = true;", bank_transfer_option)
                        driver.execute_script("setPayMethodCode(arguments[0]);", bank_transfer_option)
                        print("결제수단: 무통장입금 선택 완료 (강제 설정)")
                
                # 선택 결과 확인
                time.sleep(1)
                if bank_transfer_option.is_selected():
                    print("무통장입금 선택 확인됨")
                    
                    # 무통장입금 관련 섹션이 표시되는지 확인
                    try:
                        vbank_section = driver.find_element(By.ID, "partPaymentVbank")
                        if vbank_section.is_displayed():
                            print("무통장입금 설정 섹션이 표시됨")
                        else:
                            print("무통장입금 설정 섹션이 숨겨져 있음")
                    except:
                        print("무통장입금 설정 섹션을 찾을 수 없음")
                else:
                    print("무통장입금 선택이 제대로 되지 않음")
                    
            except Exception as inner_e:
                print(f"무통장입금 옵션 선택 실패: {inner_e}")
                
                # 대안: 사용 가능한 첫 번째 결제수단 선택
                print("=== 사용 가능한 결제수단 찾기 ===")
                for option in payment_options:
                    if not option.get_attribute('disabled'):
                        option_value = option.get_attribute('value')
                        option_id = option.get_attribute('id')
                        
                        try:
                            if option_id:
                                label = driver.find_element(By.XPATH, f"//label[@for='{option_id}']//span[@class='txt_lab']")
                                label_text = label.text.strip()
                                print(f"사용 가능한 결제수단: {option_value} - {label_text}")
                                
                                # 첫 번째 사용 가능한 옵션 선택
                                option.click()
                                print(f"결제수단 '{label_text}' 선택 완료")
                                break
                        except Exception as e:
                            print(f"결제수단 선택 실패: {e}")
                            continue
                else:
                    print("사용 가능한 결제수단이 없습니다.")
                    return False
            
        except Exception as e:
            traceback.print_exc()
            print(f"결제수단 선택 중 오류: {e}")
            return False
        
        time.sleep(1)
        
        # 3. 입금은행 선택 (농협은행) - 수정된 버전
        try:
            # 무통장입금 섹션이 표시될 때까지 대기
            vbank_section = wait.until(EC.visibility_of_element_located((By.ID, "partPaymentVbank")))
            print("무통장입금 섹션이 표시됨")
            
            # 은행 선택 드롭다운 찾기 (정확한 name 사용)
            bank_select = wait.until(EC.presence_of_element_located((By.NAME, "bankCode")))
            
            # Select 객체 생성
            from selenium.webdriver.support.ui import Select
            select_element = Select(bank_select)
            
            print("=== 사용 가능한 은행 목록 ===")
            for option in select_element.options:
                print(f"은행: {option.text} (value: {option.get_attribute('value')})")
            
            # 농협은행 선택 시도 (여러 방법)
            try:
                # 방법 1: value로 선택 (농협은행 = "11")
                select_element.select_by_value("11")
                print("입금은행: 농협은행 선택 완료 (value로 선택)")
                
            except Exception as e1:
                print(f"value로 선택 실패: {e1}")
                
                try:
                    # 방법 2: 텍스트로 선택
                    select_element.select_by_visible_text("농협은행")
                    print("입금은행: 농협은행 선택 완료 (텍스트로 선택)")
                    
                except Exception as e2:
                    print(f"텍스트로 선택 실패: {e2}")
                    
                    try:
                        # 방법 3: 부분 텍스트 매칭으로 선택
                        for option in select_element.options:
                            if "농협" in option.text:
                                select_element.select_by_visible_text(option.text)
                                print(f"입금은행: {option.text} 선택 완료 (부분 매칭)")
                                break
                        else:
                            # 방법 4: JavaScript로 직접 선택
                            driver.execute_script("""
                                var select = document.querySelector('select[name="bankCode"]');
                                select.value = '11';
                                select.dispatchEvent(new Event('change'));
                                setBankContent(select);
                            """)
                            print("입금은행: 농협은행 선택 완료 (JavaScript 강제 설정)")
                            
                    except Exception as e3:
                        print(f"부분 매칭 선택 실패: {e3}")
                        
                        # 방법 5: 첫 번째 사용 가능한 은행 선택 (기본값 제외)
                        try:
                            available_options = [opt for opt in select_element.options if opt.get_attribute('value') != '']
                            if available_options:
                                first_bank = available_options[0]
                                select_element.select_by_value(first_bank.get_attribute('value'))
                                print(f"입금은행: {first_bank.text} 선택 완료 (대안 선택)")
                            else:
                                print("사용 가능한 은행이 없습니다.")
                                return False
                                
                        except Exception as e4:
                            print(f"대안 선택도 실패: {e4}")
                            return False
            
            # 선택 결과 확인
            time.sleep(1)
            try:
                current_selection = Select(bank_select).first_selected_option
                selected_bank = current_selection.text
                selected_value = current_selection.get_attribute('value')
                print(f"최종 선택된 은행: {selected_bank} (value: {selected_value})")
                
                # onChange 이벤트 강제 호출 (은행 정보 업데이트를 위해)
                driver.execute_script("setBankContent(arguments[0]);", bank_select)
                
            except Exception as e:
                print(f"선택 결과 확인 실패: {e}")
            
        except Exception as e:
            traceback.print_exc()
            print(f"입금은행 선택 중 오류: {e}")
            return False

        # 4. 현금영수증 소득공제 선택 - 수정된 버전
        try:
            # 현금영수증 옵션들 확인 (정확한 name 사용)
            receipt_options = wait.until(EC.presence_of_all_elements_located((By.NAME, "cashReceiptIssueCode")))
            
            print("=== 현금영수증 옵션 확인 ===")
            for option in receipt_options:
                option_value = option.get_attribute('value')
                option_id = option.get_attribute('id')
                is_checked = option.is_selected()
                
                try:
                    label = driver.find_element(By.XPATH, f"//label[@for='{option_id}']//span[@class='txt_lab']")
                    label_text = label.text.strip()
                    print(f"옵션 {option_value}: {label_text}, 선택됨: {is_checked}")
                except Exception as e:
                    print(f"옵션 {option_value}: 라벨 찾기 실패 - {e}")
            
            # 소득공제 선택 (value="0")
            try:
                # 이미 기본적으로 소득공제가 선택되어 있는지 확인
                income_deduction = driver.find_element(By.XPATH, "//input[@name='cashReceiptIssueCode' and @value='0']")
                
                if not income_deduction.is_selected():
                    # 선택되어 있지 않으면 클릭
                    try:
                        income_deduction.click()
                        print("현금영수증: 소득공제 선택 완료 (일반 클릭)")
                    except:
                        driver.execute_script("arguments[0].click();", income_deduction)
                        print("현금영수증: 소득공제 선택 완료 (JavaScript 클릭)")
                else:
                    print("현금영수증: 소득공제가 이미 선택되어 있음")
                    
                # onChange 이벤트 호출
                driver.execute_script("setCashReceiptIssueCode(arguments[0]);", income_deduction)
                
            except Exception as inner_e:
                print(f"소득공제 선택 실패: {inner_e}")
                return False
            
            # 선택 결과 확인
            time.sleep(1)
            try:
                selected_receipt = driver.find_element(By.XPATH, "//input[@name='cashReceiptIssueCode' and @checked]")
                selected_value = selected_receipt.get_attribute('value')
                selected_id = selected_receipt.get_attribute('id')
                selected_label = driver.find_element(By.XPATH, f"//label[@for='{selected_id}']//span[@class='txt_lab']")
                print(f"최종 선택된 현금영수증: {selected_value} - {selected_label.text}")
            except Exception as e:
                print(f"현금영수증 선택 결과 확인 실패: {e}")
            
        except Exception as e:
            traceback.print_exc()
            print(f"현금영수증 선택 중 오류: {e}")
            return False

        time.sleep(1)

        # 5. 휴대폰번호 입력 - 수정된 버전
        try:
            # phone 변수가 정의되어 있다고 가정 (예: "01012345678")
            if not phone:
                print("휴대폰번호가 정의되지 않았습니다.")
                return False
            
            # 휴대폰번호를 3부분으로 분리
            phone1 = phone[:3]    # "010"
            phone2 = phone[3:7]   # "1234"
            phone3 = phone[7:]    # "5678"
            
            print(f"휴대폰번호 분리: {phone1}-{phone2}-{phone3}")
            
            # 현금영수증 휴대폰번호 입력 필드들 찾기 (정확한 name 사용)
            try:
                # 휴대폰번호 첫 번째 부분 (통신사 번호) - 셀렉트박스
                phone1_select = driver.find_element(By.NAME, "cashReceiptRegTelNo1")
                select_phone1 = Select(phone1_select)
                
                # 사용 가능한 옵션 확인
                print("=== 통신사 번호 옵션 ===")
                for option in select_phone1.options:
                    print(f"옵션: {option.text} (value: {option.get_attribute('value')})")
                
                # 첫 번째 부분 선택
                select_phone1.select_by_value(phone1)
                print(f"통신사 번호 선택 완료: {phone1}")
                
            except Exception as e1:
                print(f"통신사 번호 선택 실패: {e1}")
                # 대안: 기본값 010 사용
                try:
                    phone1_select = driver.find_element(By.NAME, "cashReceiptRegTelNo1")
                    Select(phone1_select).select_by_value("010")
                    print("통신사 번호: 기본값 010 선택")
                except:
                    print("통신사 번호 선택 완전 실패")
                    return False
            
            try:
                # 휴대폰번호 두 번째 부분
                phone2_input = driver.find_element(By.NAME, "cashReceiptRegTelNo2")
                phone2_input.clear()
                phone2_input.send_keys(phone2)
                print(f"휴대폰번호 중간자리 입력 완료: {phone2}")
                
            except Exception as e2:
                print(f"휴대폰번호 중간자리 입력 실패: {e2}")
                return False
            
            try:
                # 휴대폰번호 세 번째 부분
                phone3_input = driver.find_element(By.NAME, "cashReceiptRegTelNo3")
                phone3_input.clear()
                phone3_input.send_keys(phone3)
                print(f"휴대폰번호 끝자리 입력 완료: {phone3}")
                
            except Exception as e3:
                print(f"휴대폰번호 끝자리 입력 실패: {e3}")
                return False
            
            print(f"현금영수증 휴대폰번호 입력 완료: {phone1}-{phone2}-{phone3}")
            
            # 입력 완료 후 잠시 대기
            time.sleep(1)
            
        except Exception as e:
            traceback.print_exc()
            print(f"휴대폰번호 입력 중 오류: {e}")
            return False
        
        time.sleep(1)
        
        # 6. 예매자동의 전체동의 체크박스 선택
        try:
            # 전체동의 체크박스 찾기 (chkAgreeAll ID 기준)
            agree_all_checkbox = driver.find_element(By.ID, "chkAgreeAll")
            if not agree_all_checkbox.is_selected():
                agree_all_checkbox.click()
                print("예매자동의 전체동의 체크 완료")
        except Exception as e:
            print(f"전체동의 체크박스를 찾을 수 없습니다: {e}")
            return False
        
        time.sleep(1)
        
        # 7. 결제하기 버튼 클릭
        try:
            # 결제하기 버튼 찾기 및 클릭 (정확한 ID 사용)
            payment_button = wait.until(EC.element_to_be_clickable((By.ID, "btnFinalPayment")))
            
            # JavaScript로 클릭 (일반 클릭이 안될 경우를 대비)
            driver.execute_script("arguments[0].click();", payment_button)
            print("결제하기 버튼 클릭 완료")
            
            # 결제 페이지 로딩 대기
            time.sleep(3)
            
        except Exception as e:
            # 대체 방법: 다른 선택자들로 시도
            try:
                # 텍스트로 찾기
                payment_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '결제하기')]")))
                driver.execute_script("arguments[0].click();", payment_button)
                print("결제하기 버튼 클릭 완료 (대체 방법)")
                time.sleep(3)
            except Exception as e2:
                print(f"결제하기 버튼 클릭 실패: {e2}")
                return False
            
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
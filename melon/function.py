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

from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

seat_jump = ""
seat_jump_count = 0
seat_jump_special_repeat = ""
seat_jump_special_repeat_count = 0

def login(driver, id, pw):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            driver.get("https://member.melon.com/muid/family/ticket/login/web/login_informM.htm")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'id')))
            break
        except Exception as e:
            print(f"페이지 로드 시도 {attempt + 1} 실패: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise
    
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
    if len(date_list) == 0:
        time.sleep(1)
        date_list = driver.find_elements(By.XPATH,'//*[@id="list_date"]/li')
        print(f'date_list: {date_list}')
        
    for li in date_list:
        print(li.get_attribute('data-perfday'))
        if config['bookInfo']['bookDate'] == li.get_attribute('data-perfday'):
            print('date click')
            try:
                li.click()
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
    err = 0
    
    while True:  # 무한 루프로 변경
        try:
            while driver.find_element(By.ID,'certification').is_displayed() == 1:
                i += 1
                print(f"check: {i}")
                if i > 10:
                    return False
                image_check(driver, img_folder_path)
                if driver.find_element(By.ID,'certification').is_displayed() == 1:
                    driver.find_element(By.ID,'btnReload').click()
                    driver.find_element(By.ID,'label-for-captcha').clear()
                    time.sleep(0.2)
            
            print(driver.find_element(By.ID,'certification').is_displayed())
            return True
            
        except Exception as e:
            print("no certification")
            err += 1
            if i > 0:
                print(e)
                if err > 20:
                    return False
                print(f"재시도 중... (현재 i={i})")
                time.sleep(1)  # 잠시 대기 후 재시도
                continue  # while True 루프 계속
            else:
                return True

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

            """area_list의 텍스트가 로딩될 때까지 대기"""
            try:
                WebDriverWait(driver, 1).until(
                    lambda d: any(
                        li.text.strip() != "" 
                        for li in box_list_area.find_elements(By.CSS_SELECTOR,'td > div > ul > li')
                    )
                )
            except Exception as e:
                print_debug(f'구역 텍스트 로딩 실패: {e}')
                print_debug(f'등급 재클릭 시도')
                tr.click()

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
    for i in li_list:
        try:

            print_debug(f'area = {i.text}')
            if i.text == "":
                break
            area_element = i.find_element(By.CLASS_NAME,'area_tit')
            area = area_element.text.strip()
            print_debug(f'area = "{area}", choice: "{choice}"')
            # 텍스트가 비어있으면 스크롤해서 로딩 시도
            if area == "":
                print_debug("텍스트 비어있음, 스크롤 시도")
                driver.execute_script("arguments[0].scrollIntoView(true);", i)
                # time.sleep(0.5)  # 로딩 대기
                area = area_element.text.strip()  # 다시 텍스트 가져오기
                # print_debug(f'스크롤 후 area = "{area}"')

            if choice == "" or choice in area:
                # print_debug(f"클릭 시도: {area}")

                # 스크롤 후 클릭
                # driver.execute_script("arguments[0].scrollIntoView(true);", i)
                # time.sleep(0.1)

                try:
                    i.click()
                    # print_debug("일반 클릭 성공")
                except:
                    print_debug("일반 클릭 실패, JS 클릭 시도")
                    driver.execute_script("arguments[0].click();", i)

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
        except Exception as e:
            print_debug(f"select_box 내부 오류: {e}")
            continue

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
        # alert 텍스트 출력
        alert_text = alert.text
        print(f"Alert 내용: {alert_text}")
        # 이미 Alert이 떠 있는 경우, accept() 메서드를 사용하여 Alert을 수락하거나 dismiss() 메서드를 사용하여 Alert을 취소할 수 있습니다.
        # 예시: alert.accept()
        alert.accept()
        print("Alert is present")
        # return CODE.SUCCESS
        return CODE.CONFLICT
    except:
        print("Alert is not present")
        return CODE.SUCCESS

def print_debug(msg):
    print(msg)
    pass
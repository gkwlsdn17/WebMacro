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

def login(driver,id, pw):

    driver.get("https://member.melon.com/muid/family/ticket/login/web/login_informM.htm")
    driver.find_element_by_id('id').send_keys(id)
    driver.find_element_by_id('pwd').send_keys(pw)
    time.sleep(0.5)
    driver.find_element_by_id('btnLogin').click()

    time.sleep(0.3)

def check_alert(driver):
    try:
        if driver.find_element_by_id('noticeAlert').is_displayed() == 1:
            driver.find_element_by_id('noticeAlert_layerpopup_close').click()
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
    date_list = driver.find_elements_by_xpath('//*[@id="list_date"]/li')
    for li in date_list:
        print(li.get_attribute('data-perfday'))
        if config['bookInfo']['bookDate'] == li.get_attribute('data-perfday'):
            print('date click')
            try:
                li.click()
                break
            except Exception as e:
                print(f'select_date list_date/li error:{e}')
                btn = driver.find_element_by_css_selector(f'button.ticketCalendarBtn[data-perfday="{config["bookInfo"]["bookDate"]}"]')
                btn.click()
                break
            

    time.sleep(0.3)
    time_list = driver.find_elements_by_xpath('//*[@id="list_time"]/li')
    for li in time_list:
        print(li.find_element_by_css_selector('button > span').get_attribute('innerHTML').split(" "))
        times = li.find_element_by_css_selector('button > span').get_attribute('innerHTML').split(" ")
        book_time = times[0][0:2] + times[1][0:2]
        if config['bookInfo']['bookTime'] == book_time:
            print("time ok")
            li.click()
            break

    driver.find_element_by_xpath('//*[@id="ticketReservation_Btn"]').click()
    time.sleep(1)

def certification(driver):
    i = 0
    try:
        while driver.find_element_by_id('certification').is_displayed() == 1:
            i += 1
            print(f"check: {i}")
            if i > 10:
                break
            image_check(driver)
            if driver.find_element_by_id('certification').is_displayed() == 1:
                driver.find_element_by_id('btnReload').click()
                driver.find_element_by_id('label-for-captcha').clear()
                # time.sleep(0.1)
        print(driver.find_element_by_id('certification').is_displayed())
    except:
        print("no certification")

def image_check(driver):
    capchaImg = driver.find_element_by_id('captchaImg')

    img_src = capchaImg.get_attribute('src')
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    img_file_path = f'./{file_name}.png'
    urlretrieve(img_src, img_file_path)

    foreground = Image.open(img_file_path)
    width, height = foreground.size
    background = Image.new("RGBA", (width, height), color="#FFF")
    Image.alpha_composite(background, foreground).save('composite_img.png')

    # time.sleep(0.1)
    img = cv2.imread('composite_img.png')

    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(img, detail=0)
    print(result[0])
    driver.find_element_by_id('label-for-captcha').send_keys(result[0])
    driver.find_element_by_id('btnComplete').click()

def select_seat(driver, config_grade_area, config_special_area, bool_special_area):
    grade_summary = driver.find_elements_by_css_selector('#divGradeSummary > tr')
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
            area_list = box_list_area.find_elements_by_css_selector('td > div > ul > li')
            print_debug(f'len(area_list):{len(area_list)}')
            if len(tmp_special_area) == 0:
                tmp_special_area.append("")
            print_debug(f'config_special_area:{tmp_special_area}')
            while len(tmp_special_area) > 0:
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
        return res
    else:
        print_debug("grade 없음")
        res = select_rect(driver)
        return res

def select_box(driver, li_list, choice=""):
    for i in li_list:
        print_debug(f'area = {i.text}')
        area = i.find_element_by_class_name('area_tit').text.strip()
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


    # seats = driver.find_elements_by_css_selector('#ez_canvas > svg > rect:not([fill="#DDDDDD"]):not([fill="none"])')
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
        driver.find_element_by_id('nextTicketSelection').click()
    except Exception as e:
        print(f"seat read error: {e}")
        return CODE.CONFLICT

    try:
        alert = Alert(driver)
        # 이미 Alert이 떠 있는 경우, accept() 메서드를 사용하여 Alert을 수락하거나 dismiss() 메서드를 사용하여 Alert을 취소할 수 있습니다.
        # 예시: alert.accept()
        alert.accept()
        print("Alert is present")
        return CODE.CONFLICT
    except:
        print("Alert is not present")
        return CODE.SUCCESS

def print_debug(msg):
    print(msg)
    pass
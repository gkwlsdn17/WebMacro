import traceback
from urllib.request import urlretrieve
from PIL import Image
import pause as pause
import datetime
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import easyocr
import cv2
import CODE
import playsound
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

seat_jump = ""
seat_jump_count = 0
seat_jump_special_repeat = ""
seat_jump_special_repeat_count = 0

is_certification = False # 보안문자창이 있는 경우 빠르게 클릭하면 자꾸 창이 떠서 보안문자창 뜨는 케이스인지 체크하려고 만든 변수

def get_chrome_driver():
    # window
    subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chromeCookie2"')

    # mac
    # subprocess.Popen([
    # '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    # '--remote-debugging-port=9222',
    # '--user-data-dir=/Users/kwon/chromeCookie2'  # 사용자 홈 디렉토리의 임시 폴더 사용
    # ])
    # Chrome이 완전히 실행될 때까지 대기
    time.sleep(3)


    option = Options()
    option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
    return driver

def login(driver, id, pw):
    driver.get(
        "https://ticket.interpark.com/Gate/TPLogin.asp?CPage=B&MN=Y&tid1=main_gnb&tid2=right_top&tid3=login&tid4=login")
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="loginAllWrap"]/div[2]/iframe')))
    #
    # driver.switch_to_frame(driver.find_element_by_xpath('//*[@id="loginAllWrap"]/div[2]/iframe'))
    # driver.find_element_by_xpath('//*[@id="userId"]').send_keys(id)
    # time.sleep(0.5)
    # driver.find_element_by_xpath('//*[@id="userPwd"]').send_keys(pw)
    # time.sleep(0.5)
    driver.find_element(By.ID,'userId').send_keys(id)
    driver.find_element(By.ID,'userPwd').send_keys(pw)
    time.sleep(0.5)
    # driver.find_element_by_xpath('//*[@id="btn_login"]').click()
    driver.find_element(By.ID,'btn_login').click()
    time.sleep(0.5)

def first_popup_check(driver):
    try:
        # if driver.find_element_by_css_selector('#popup-prdGuide > div').is_displayed() == 1:
        #     print_debug("닫는다")
        #     driver.find_element_by_css_selector('#popup-prdGuide > div > div.popupFooter > button').click()
        # else:
        #     print_debug("팝업 안열려있음")

        if driver.find_element(By.CSS_SELECTOR, '#popup-prdGuide > div').is_displayed() == 1:
            print_debug("닫는다")
            driver.find_element(By.CSS_SELECTOR,'#popup-prdGuide > div > div.popupFooter > button').click()
        else:
            print_debug("팝업 안열려있음")
    except Exception as e:
        print(e)
        print_debug("팝업 안열려있음")

    try:
        alert = Alert(driver)
        # 이미 Alert이 떠 있는 경우, accept() 메서드를 사용하여 Alert을 수락하거나 dismiss() 메서드를 사용하여 Alert을 취소할 수 있습니다.
        # 예시: alert.accept()
        alert.accept()
        print_debug("Alert is present")
    except:
        print_debug("Alert is not present")

def click_book(driver, date, book_time):
    book_time = book_time[:2] + ":" + book_time[2:]
    # li_list = driver.find_elements_by_css_selector(
    #     '#productSide > div > div.sideMain > div.sideContainer.containerTop.sideToggleWrap > div.sideContent.toggleCalendar > div > div > div > div > ul:nth-child(3) > li')
    li_list = driver.find_elements(By.CSS_SELECTOR, 
                '#productSide > div > div.sideMain > div.sideContainer.containerTop.sideToggleWrap > div.sideContent.toggleCalendar > div > div > div > div > ul:nth-child(3) > li')
    
    print_debug(f'date_list:{len(li_list)}')
    for i, li in enumerate(li_list):
        if li.get_attribute('innerHTML').zfill(2) == date[6:]:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(li))
            driver.execute_script(f"arguments[0].click();", li)
            time.sleep(0.2)
            # bk = driver.find_element_by_css_selector(f'a.timeTableLabel[data-text*="{book_time}"]')
            book_time.strip()
            # bk = driver.find_element(By.CSS_SELECTOR, f'a.timeTableLabel[data-text*="{book_time}"]')
            bk_list =driver.find_elements(By.CSS_SELECTOR,
                    f'#productSide > div > div.sideMain > div.sideContainer.containerMiddle.sideToggleWrap > div.sideContent > div.sideTimeTable.toggleTimeTable > ul > li'
            )
            bk = None
            for a in bk_list:
                e = a.find_element(By.CSS_SELECTOR, f'a.timeTableLabel')
                print(e.text)
                if book_time in e.text:
                    bk = e
                    print_debug(bk.get_attribute('outerHTML'))
                    driver.execute_script("arguments[0].click();", e)
                    break  # 원하는 요소를 클릭했으므로 반복문 종료
            if bk is None:
                raise Exception("회차 시간 못찾음")
            # print_debug(bk.get_attribute('outerHTML'))
            # bk.click()
            print_debug("예매하기 클릭시도")
            # driver.find_element_by_css_selector('#productSide > div > div.sideBtnWrap > a.sideBtn.is-primary').click()
            # bk_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#productSide > div > div.sideBtnWrap > a.sideBtn.is-primary')))

            bk_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="productSide"]/div/div[2]/a[1]')))
            bk_btn.click()
            print_debug("예매하기 클릭")
            break

def certification(driver):
    i = 0
    try:
        time.sleep(10)
        while driver.find_element(By.ID,'divRecaptcha').is_displayed() == 1:
            global is_certification
            is_certification = True
            i += 1
            print_debug(f"check: {i}")
            if i > 10:
                break
            image_check(driver)
            if driver.find_element(By.ID,'divRecaptcha').is_displayed() == 1:
                print_debug("문자 틀림")
                driver.find_element(By.CSS_SELECTOR, '#divRecaptcha > div.capchaInner > div.capchaImg > a.refreshBtn').click()

    except Exception as e:
        # traceback.print_debug_exc(e)
        print(f"no certification:\n{e}")

def image_check(driver):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'imgCaptcha')))
    capchaImg = driver.find_element(By.ID, 'imgCaptcha')

    img_src = capchaImg.get_attribute('src')
    file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    img_file_path = f'./{file_name}.png'
    # img_file_path = f'composite_img.png'
    urlretrieve(img_src, img_file_path)
    #
    # foreground = Image.open(img_file_path)
    # width, height = foreground.size
    # background = Image.new("RGBA", (width, height), color="#FFF")
    # Image.alpha_composite(background, foreground).save('composite_img.png')

    # time.sleep(0.1)
    # img = cv2.imread('composite_img.png')
    img = cv2.imread(img_file_path)
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(img, detail=0)
    print(result[0])
    value = result[0].replace(' ','').replace('5', 'S').replace('0', 'O').replace('$', 'S').replace(',', '') \
        .replace(':', '').replace('.', '').replace('+', 'T').replace("'", '').replace('`', '') \
        .replace('1', 'L').replace('e', 'Q').replace('3', 'S').replace('€', 'C').replace('{', '').replace('-', '').upper()
    print(f"교정한 result[0]: {value}")

    driver.find_element(By.CSS_SELECTOR, '#divRecaptcha > div.capchaInner > div.validationTxt > span').click()
    driver.find_element(By.ID,'txtCaptcha').send_keys(value)
    driver.find_element(By.CSS_SELECTOR,'a[onclick="fnCheck()"]').click()

def booking(driver, config_special_area, bool_special_area, col_special_area, special_grade):
    result = CODE.EMPTY
    # 좌석 등급 선택
    gradeList = []
    try:
        gradeList = driver.find_elements(By.CSS_SELECTOR,'#GradeRow > td > div > span.select')
        print_debug(f"len(gradeList): {len(gradeList)}")
    except Exception as e:
        print(f"좌석등급/잔여석 가져오기 에러:{e}")

    # 전석
    if len(gradeList) == 0:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'ifrmSeatDetail')))
        iframe = driver.find_element(By.ID,'ifrmSeatDetail')
        driver.switch_to.frame(iframe)
        while True:
            if len(config_special_area) != 0:
                print_debug(f"config_special_area[0]: {config_special_area[0]}")
                tag = ""
                if len(col_special_area) > 0:
                    for col in range(int(col_special_area[0]), int(col_special_area[1])+1):
                        if tag == "":
                            tag += f'[alt*="{config_special_area[0]}"][alt$="-{col}"]'
                        else:
                            tag += f',[alt*="{config_special_area[0]}"][alt$="-{col}"]'
                else:
                    tag = f'[alt*="{config_special_area[0]}"]'
                print_debug(tag)

                # seats = driver.find_elements_by_css_selector(
                #     f'#TmgsTable > tbody > tr > td > img[src*="http://ticketimage.interpark.com/TMGSNAS/TMGS/G/"]{tag}')
                seats = driver.execute_script("""
                        const regex_c = /(\d*)열/;
                        const regex_f = /(\d*)층/;
                        const seats = document.querySelectorAll('#TmgsTable > tbody > tr > td > img[src*="http://ticketimage.interpark.com/TMGSNAS/TMGS/G/"]""" + tag + """ ');
                        const sortedSeats = Array.from(seats).sort((a, b) =>
                        {if(a.getAttribute('alt').split('-')[0].match(regex_f)[1] == null || a.getAttribute('alt').split('-')[1].match(regex_c)[1] == null){
                            return a.getAttribute('alt').split('-')[1] - b.getAttribute('alt').split('-')[1]
                        } else{
                            if(parseInt(a.getAttribute('alt').split('-')[0].match(regex_f)[1]) - parseInt(b.getAttribute('alt').split('-')[0].match(regex_f)[1]) == 0){
                                return parseInt(a.getAttribute('alt').split('-')[1].match(regex_c)[1]) - parseInt(b.getAttribute('alt').split('-')[1].match(regex_c)[1])
                            } else{
                                return parseInt(a.getAttribute('alt').split('-')[0].match(regex_f)[1]) - parseInt(b.getAttribute('alt').split('-')[0].match(regex_f)[1])
                            }
                        }
                        
                        });
                        return sortedSeats;

                """)
                # for i in seats:
                #     print(i.get_attribute('alt'))

            else:
                if bool_special_area == "Y":
                    return CODE.EMPTY
                # seats = driver.find_elements_by_css_selector('#TmgsTable > tbody > tr > td > img[src*="http://ticketimage.interpark.com/TMGSNAS/TMGS/G/"]')

                print_debug('order없는걸로 테스트중')
                
                # seats = driver.execute_script("""
                #     const regex_c = /(\d*)열/;
                #     const regex_f = /(\d*)층/;
                #     const seats = document.querySelectorAll('#TmgsTable > tbody > tr > td > img[src*="http://ticketimage.interpark.com/TMGSNAS/TMGS/G/"]');
                #     const sortedSeats = Array.from(seats).sort((a, b) =>
                #         {
                #         if(a.getAttribute('alt').split('-')[0].match(regex_f)[1] == null || a.getAttribute('alt').split('-')[1].match(regex_c)[1] == null){
                #             return a.getAttribute('alt').split('-')[1] - b.getAttribute('alt').split('-')[1]
                #         } else{
                #             if(parseInt(a.getAttribute('alt').split('-')[0].match(regex_f)[1]) - parseInt(b.getAttribute('alt').split('-')[0].match(regex_f)[1]) == 0){
                #                 return parseInt(a.getAttribute('alt').split('-')[1].match(regex_c)[1]) - parseInt(b.getAttribute('alt').split('-')[1].match(regex_c)[1])
                #             } else{
                #                 return parseInt(a.getAttribute('alt').split('-')[0].match(regex_f)[1]) - parseInt(b.getAttribute('alt').split('-')[0].match(regex_f)[1])
                #             }
                #         }
                        
                #         });
                #     return sortedSeats;
                # """)

                # 오류 수정
                seats = driver.execute_script("""
                    const regex_c = /(\d*)열/;
                    const regex_f = /(\d*)층/;
                    const seats = document.querySelectorAll('#TmgsTable > tbody > tr > td > img[src*="http://ticketimage.interpark.com/TMGSNAS/TMGS/G/"]');
                    const sortedSeats = Array.from(seats).sort((a, b) => {
                        // 'alt' 속성 값이 있는지, 그리고 match 결과가 null이 아닌지 체크
                        const aFirstMatch = a.getAttribute('alt').split('-')[0].match(regex_f);
                        const bFirstMatch = b.getAttribute('alt').split('-')[0].match(regex_f);
                        const aSecondMatch = a.getAttribute('alt').split('-')[1].match(regex_c);
                        const bSecondMatch = b.getAttribute('alt').split('-')[1].match(regex_c);

                        // match 결과가 null인 경우에는 적절히 처리
                        const aFirstValue = aFirstMatch ? parseInt(aFirstMatch[1]) : -Infinity;  // null인 경우에는 매우 작은 값으로 처리
                        const bFirstValue = bFirstMatch ? parseInt(bFirstMatch[1]) : -Infinity;
                        const aSecondValue = aSecondMatch ? parseInt(aSecondMatch[1]) : -Infinity;
                        const bSecondValue = bSecondMatch ? parseInt(bSecondMatch[1]) : -Infinity;

                        // 이제 안전하게 비교할 수 있습니다
                        if (aFirstValue === bFirstValue) {
                            return aSecondValue - bSecondValue;
                        } else {
                            return aFirstValue - bFirstValue;
                        }
                    });
                    return sortedSeats;
                """)
                print_debug(f"len(seats): {len(seats)}")
                # for i in seats:
                #     print(i.get_attribute('alt'))


            print_debug(f"len(seats): {len(seats)}")

            if len(seats) == 0:
                if len(config_special_area) > 0:
                    config_special_area.pop(0)
                if len(config_special_area) == 0:
                    return CODE.EMPTY
                else:
                    continue
            try:
                if seat_jump == 'Y' and (len(seats) > seat_jump_count > 0):
                    seats[seat_jump_count].click()
                else:
                    seats[0].click()
                driver.switch_to.default_content()
                iframe = driver.find_element(By.ID,'ifrmSeat')
                driver.switch_to.frame(iframe)

                # 좌석선택 완료 클릭
                driver.find_element(By.CSS_SELECTOR,
                    'body > form:nth-child(2) > div > div.contWrap > div.seatR > div > div.btnWrap > a').click()
            except Exception as e:
                print(f"좌석클릭 에러:{e}")
                return CODE.CONFLICT
            try:
                alert = Alert(driver)
                # 이미 Alert이 떠 있는 경우, accept() 메서드를 사용하여 Alert을 수락하거나 dismiss() 메서드를 사용하여 Alert을 취소할 수 있습니다.
                # 예시: alert.accept()
                alert.accept()
                print_debug("Alert is present")
                # driver.find_element_by_css_selector(
                #     'body > form: nth - child(2) > div > div.contWrap > div.seatR > div > div.btnWrap > p.fl_r > a').click()
                return CODE.CONFLICT
            except:
                print("Alert is not present")
                return CODE.SUCCESS
    # 등급
    else:
        for grade in gradeList:

            if is_certification == True:
                # 보안문자창 뜨는거 예방
                time.sleep(1)
            print_debug(grade.find_element(By.CSS_SELECTOR,'strong').text)
            grade_text = grade.find_element(By.CSS_SELECTOR, 'strong').text
            try:
                time.sleep(0.3)
                grade.click()
                # 특정 등급만 돌게끔 할 때
                if len(special_grade) > 0:
                        grade_check = False
                        for special in special_grade:
                            if special in grade.text:
                                grade_check = True
                                break
                        if grade_check == False:
                            print_debug(f'{grade.text}, {special}')
                            print_debug('등급이 달라서 패스')
                            continue
                
            except Exception as e:
                # 보안문자창이 갑자기 뜰 때
                print(traceback.format_exc())
                return CODE.ERROR

            time.sleep(0.1)

            grade_text = re.sub(r'(?<!\\)([\\()])', r'\\\1', grade_text)
            print_debug(f"convert grade_text: {grade_text}")
            areas = driver.find_elements(By.CSS_SELECTOR, f'td[seatgradename={grade_text}] > div > ul > li > a')

            print_debug(f"len(areas): {len(areas)}")
            # if len(config_special_area) != 0:
            #     areas = [area for area in areas if any(config in area.text for config in config_special_area)]
            print_debug(f"len(areas) 22222: {len(areas)}")

            tag = ""
            if len(config_special_area) != 0:
                print_debug(f"config_special_area[0]: {config_special_area[0]}")
                if len(col_special_area) > 0:
                    # ex)
                    # title="[스탠딩석] 1층-A구역 입장번호-244"
                    # title="[VIP석] 2층-C2구역-56"
                    # title="[지정석R] 2층-29구역 1열-7"
                    for col in range(int(col_special_area[0]), int(col_special_area[1])+1):
                        if tag == "":
                            tag += f'[title*="{config_special_area[0]}"][title*="-{col}"]'
                        else:
                            tag += f',[title*="{config_special_area[0]}"][title*="-{col}"]'
                else:
                    tag = f'[title*="{config_special_area[0]}"]'
                print_debug(tag)

            for area in areas:
                if is_certification == True:
                    # 보안문자창 뜨는거 예방
                    time.sleep(0.4)
                try:
                    print_debug(f"area: {area.text}")

                    # # 특정 order 영역만 돌게끔 할 때
                    # if len(config_special_area) > 0:
                    #         s_check = False
                    #         for special in config_special_area:
                    #             if special in area.text:
                    #                 s_check = True
                    #                 break
                    #         if s_check == False:
                    #             print_debug(f'{area.text}, {special}')
                    #             print_debug('영역이 달라서 패스')
                    #             continue
                            
                except Exception as e:
                    # 보안문자창이 갑자기 뜰 때
                    print(traceback.format_exc())
                    return CODE.ERROR
                

                # area.click()
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(area)
                )
                element.click()              
                

                iframe = driver.find_element(By.ID,'ifrmSeatDetail')
                driver.switch_to.frame(iframe)
                # seats = driver.find_elements_by_css_selector('#Seats')
                if tag != "":
                    # script = """
                    #     const regex_c = /(\d*)열/;
                    #     const seats = document.querySelectorAll('#Seats""" + tag +"""');
                    #     const sortedSeats = Array.from(seats).sort((a, b) =>
                    #         a.getAttribute('title').split('-')[1].match(regex_c)[1] == "" ? a.getAttribute('title').split('-')[1] - b.getAttribute('title').split('-')[1] : parseInt(a.getAttribute('title').split('-')[1].match(regex_c)[1]) - parseInt(b.getAttribute('title').split('-')[1].match(regex_c)[1])
                    #     );
                    #     return sortedSeats;
                    # """
                    script = """
                        const regex_c = /(\d*)열/;
                        const seats = document.querySelectorAll('#Seats""" + tag +"""');

                        const sortedSeats = Array.from(seats).sort((a, b) => {
                            const aMatch = a.getAttribute('title').split('-')[1].match(regex_c);
                            const bMatch = b.getAttribute('title').split('-')[1].match(regex_c);

                            const aValue = aMatch ? parseInt(aMatch[1]) : 0;
                            const bValue = bMatch ? parseInt(bMatch[1]) : 0;

                            return aValue - bValue;
                        });

                        return sortedSeats;
                    """
                else:
                    script = """
                        const regex_c = /(\d*)열/;
                        const seats = document.querySelectorAll('#Seats');
                        const sortedSeats = Array.from(seats).sort((a, b) =>
                            a.getAttribute('title').split('-')[1].match(regex_c)[1] == "" ? a.getAttribute('title').split('-')[1] - b.getAttribute('title').split('-')[1] : parseInt(a.getAttribute('title').split('-')[1].match(regex_c)[1]) - parseInt(b.getAttribute('title').split('-')[1].match(regex_c)[1]));
                        return sortedSeats;
                    """
                # print_debug(script)
                seats = driver.execute_script(script)

                print_debug(f"len (seats): {len(seats)}")
                if len(seats) == 0:
                    # 다음 영역 선택 속도 지연 (빠르면 매크로로 인식되어버려 보안창뜸)
                    time.sleep(0.4)
                    driver.switch_to.default_content()
                    iframe = driver.find_element(By.ID,'ifrmSeat')
                    driver.switch_to.frame(iframe)
                    continue

                if seat_jump == 'Y' and (len(seats) > seat_jump_count > 0):
                    print(f"{seats[seat_jump_count].get_attribute('title')} click")
                    seats[seat_jump_count].click()
                else:
                    print(f"{seats[0].get_attribute('title')} click")
                    seats[0].click()

                driver.switch_to.default_content()
                iframe = driver.find_element(By.ID,'ifrmSeat')
                driver.switch_to.frame(iframe)
                
                book_btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body > form:nth-child(2) > div > div.contWrap > div.seatR > div > div.btnWrap > a'))
                )
                book_btn.click()

                try:
                    alert = Alert(driver)
                    # 이미 Alert이 떠 있는 경우, accept() 메서드를 사용하여 Alert을 수락하거나 dismiss() 메서드를 사용하여 Alert을 취소할 수 있습니다.
                    # 예시: alert.accept()
                    alert.accept()
                    print("Alert is present")
                    # driver.find_element_by_css_selector(
                    #     'body > form: nth - child(2) > div > div.contWrap > div.seatR > div > div.btnWrap > p.fl_r > a').click()
                    result = CODE.CONFLICT
                    continue

                except:
                    print("Alert is not present")
                    result = CODE.SUCCESS
                    return result


    return result

def print_debug(msg):
    print(msg)
    # pass
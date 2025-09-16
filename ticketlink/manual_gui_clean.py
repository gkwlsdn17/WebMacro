import time
import subprocess
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
from tkinter import messagebox
import threading
from manual_function import TicketAutomationFunctions

class ManualChromeController:
    def __init__(self):
        self.driver = None
        self.debug_port = 9222
        self.automation_functions = None
        self.log_text = None  # 실시간 로그 위젯

    def add_log(self, message):
        """실시간 로그에 메시지 추가"""
        if self.log_text:
            try:
                timestamp = time.strftime('%H:%M:%S')
                log_entry = f"[{timestamp}] {message}\n"
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)  # 자동 스크롤
                self.log_text.update()
            except:
                pass

    def check_chrome_running(self):
        """Chrome 디버그 모드가 실행 중인지 확인"""
        try:
            response = requests.get(f'http://localhost:{self.debug_port}/json/version', timeout=5)
            return response.status_code == 200
        except:
            return False

    def start_chrome_debug_mode(self):
        """Chrome 디버그 모드 시작"""
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        user_data_dir = r"C:\temp\chrome_manual_debug"

        cmd = [
            chrome_path,
            f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={user_data_dir}",
            "--disable-blink-features=AutomationControlled",
            "--exclude-switches=enable-automation",
            "--disable-infobars",
            "--no-first-run"
        ]

        try:
            subprocess.Popen(cmd)
            print("Chrome 디버그 모드를 시작했습니다...")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Chrome 시작 실패: {e}")
            return False

    def connect_to_chrome(self):
        """실행 중인 Chrome에 연결"""
        options = Options()
        options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")

        try:
            self.driver = webdriver.Chrome(options=options)
            self.automation_functions = TicketAutomationFunctions(self.driver)
            print("Chrome에 성공적으로 연결되었습니다!")
            return True
        except Exception as e:
            print(f"Chrome 연결 실패: {e}")
            return False

    def show_match_selection_dialog(self, match_info, parent):
        """경기 선택 다이얼로그 (simpledialog 오류 방지)"""
        selection_window = tk.Toplevel(parent)
        selection_window.title("경기 선택")
        selection_window.geometry("500x400")
        selection_window.transient(parent)
        selection_window.grab_set()

        # 중앙에 배치
        selection_window.update_idletasks()
        x = (selection_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (selection_window.winfo_screenheight() // 2) - (400 // 2)
        selection_window.geometry(f"500x400+{x}+{y}")

        # 결과 저장용
        self.selected_choice = None

        # 제목
        title_label = tk.Label(selection_window, text="📅 예매할 경기를 선택하세요",
                              font=("맑은 고딕", 14, "bold"), pady=15)
        title_label.pack()

        # 경기 목록 프레임
        list_frame = tk.Frame(selection_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 라디오 버튼 변수
        selected_var = tk.IntVar()

        # 각 경기에 대한 라디오 버튼 생성
        for match in match_info:
            radio_text = f"{match['index']}. {match['date']} {match['time']} - {match['teams']}"
            radio_btn = tk.Radiobutton(list_frame, text=radio_text,
                                     variable=selected_var, value=match['index'],
                                     font=("맑은 고딕", 11), anchor='w', pady=5)
            radio_btn.pack(fill='x')

        # 기본값 설정 (첫 번째 선택)
        selected_var.set(1)

        # 버튼 프레임
        button_frame = tk.Frame(selection_window)
        button_frame.pack(fill=tk.X, padx=20, pady=15)

        def on_select():
            self.selected_choice = selected_var.get()
            selection_window.destroy()

        def on_cancel():
            self.selected_choice = None
            selection_window.destroy()

        # 선택 버튼
        select_btn = tk.Button(button_frame, text="✅ 선택", command=on_select,
                              font=("맑은 고딕", 11), bg="lightgreen", width=10)
        select_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 취소 버튼
        cancel_btn = tk.Button(button_frame, text="❌ 취소", command=on_cancel,
                              font=("맑은 고딕", 11), bg="lightgray", width=10)
        cancel_btn.pack(side=tk.LEFT)

        # 창이 닫힐 때까지 대기
        selection_window.wait_window()

        return self.selected_choice

    def show_copyable_message(self, title, content, root, window_width=700, window_height=500):
        """복사 가능한 메시지 창 표시"""
        result_window = tk.Toplevel(root)
        result_window.title(f"{title} (복사 가능)")
        result_window.geometry(f"{window_width}x{window_height}")
        result_window.transient(root)
        result_window.grab_set()

        frame = tk.Frame(result_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                             font=("맑은 고딕", 10))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

        def copy_to_clipboard():
            result_window.clipboard_clear()
            result_window.clipboard_append(content)
            messagebox.showinfo("복사 완료", "내용이 클립보드에 복사되었습니다!")

        button_frame = tk.Frame(result_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        copy_btn = tk.Button(button_frame, text="📋 전체 복사", command=copy_to_clipboard,
                           font=("맑은 고딕", 10), bg="#4CAF50", fg="white")
        copy_btn.pack(side=tk.LEFT, padx=(0, 5))

        close_btn = tk.Button(button_frame, text="닫기", command=result_window.destroy,
                            font=("맑은 고딕", 10))
        close_btn.pack(side=tk.RIGHT)

        result_window.update_idletasks()
        x = (result_window.winfo_screenwidth() // 2) - (window_width // 2)
        y = (result_window.winfo_screenheight() // 2) - (window_height // 2)
        result_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def safe_execute_with_button(self, func, button, success_msg="", timeout=10):
        """버튼 상태 표시와 함께 안전하게 함수 실행"""
        def run():
            original_text = button.cget("text")
            original_color = button.cget("bg")

            try:
                button.config(text="⏳ 실행중...", bg="yellow")
                button.update()

                result = func()

                if result:
                    button.config(text="✅ 완료", bg="lightgreen")
                    if success_msg:
                        messagebox.showinfo("성공", success_msg)
                else:
                    button.config(text="❌ 실패", bg="lightcoral")

            except Exception as e:
                button.config(text="❌ 오류", bg="lightcoral")
                messagebox.showerror("오류", f"실행 중 오류 발생: {e}")

            # 일정 시간 후 원래 상태로 복원
            def restore():
                button.config(text=original_text, bg=original_color)

            threading.Timer(3.0, restore).start()

        threading.Thread(target=run, daemon=True).start()

    def manual_control_gui(self):
        """새로운 깔끔한 GUI"""
        root = tk.Tk()
        root.title("티켓링크 자동화 - 수동 제어")
        root.geometry("1000x800")
        root.resizable(True, True)
        root.minsize(950, 750)

        # 메인 제목
        title_label = tk.Label(root, text="🎫 티켓링크 자동화 제어판",
                              font=("맑은 고딕", 16, "bold"), fg="navy")
        title_label.pack(pady=15)

        # 상태 표시
        status_frame = tk.Frame(root)
        status_frame.pack(pady=10)

        status_label = tk.Label(status_frame, text="Chrome 상태: 확인 중...",
                               font=("맑은 고딕", 11), fg="blue")
        status_label.pack()

        # 메인 컨테이너 (좌우 분할)
        main_container = tk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 왼쪽 프레임 (버튼들)
        left_frame = tk.Frame(main_container, relief=tk.RAISED, bd=2, width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        # 오른쪽 프레임 (실시간 로그)
        right_frame = tk.Frame(main_container, relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 로그 헤더
        log_header = tk.Label(right_frame, text="📊 실시간 진행 로그",
                             font=("맑은 고딕", 12, "bold"), fg="darkblue")
        log_header.pack(pady=10)

        # 로그 텍스트 위젯
        self.log_text = tk.Text(right_frame, wrap=tk.WORD, font=("Consolas", 9),
                               bg="#f8f9fa", fg="#212529", height=35)

        # 스크롤바
        log_scrollbar = tk.Scrollbar(right_frame)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)

        # 초기 로그 메시지
        self.add_log("🚀 티켓링크 자동화 시스템 시작")
        self.add_log("Chrome 디버그 모드로 연결 대기 중...")

        # 메인 컨트롤 프레임을 왼쪽으로 변경
        main_frame = left_frame

        # 섹션별로 구분된 레이아웃
        sections = [
            ("🚀 Chrome 연결", 0),
            ("🏠 기본 네비게이션", 1),
            ("📍 창 관리", 2),
            ("🎯 좌석 예매", 3),
            ("🔧 고급 기능", 4)
        ]

        # 각 섹션 생성
        for section_name, row in sections:
            section_label = tk.Label(main_frame, text=section_name,
                                   font=("맑은 고딕", 12, "bold"), fg="darkgreen")
            section_label.grid(row=row*2, column=0, columnspan=4, sticky="w", padx=10, pady=(15, 5))

        # 🚀 Chrome 연결 (Row 1)
        def start_chrome():
            return self.start_chrome_debug_mode()

        def connect_chrome():
            success = self.connect_to_chrome()
            if success:
                status_label.config(text="Chrome 상태: ✅ 연결됨", fg="green")
            return success

        start_btn = tk.Button(main_frame, text="🚀 Chrome 시작",
                             font=("맑은 고딕", 10), width=18, height=2, bg="lightblue")
        start_btn.grid(row=1, column=0, padx=5, pady=5)
        start_btn.config(command=lambda: self.safe_execute_with_button(start_chrome, start_btn, "Chrome 디버그 모드가 시작되었습니다!"))

        connect_btn = tk.Button(main_frame, text="🔗 Chrome 연결",
                               font=("맑은 고딕", 10), width=18, height=2, bg="lightgreen")
        connect_btn.grid(row=1, column=1, padx=5, pady=5)
        connect_btn.config(command=lambda: self.safe_execute_with_button(connect_chrome, connect_btn, "Chrome에 성공적으로 연결되었습니다!"))

        # 🏠 기본 네비게이션 (Row 3)
        def goto_ticketlink():
            if self.driver:
                self.driver.get("https://www.ticketlink.co.kr")
                return True
            return False

        def refresh_page():
            if self.driver:
                self.driver.refresh()
                return True
            return False

        def click_booking():
            if self.driver:
                try:
                    # 모든 예매하기 버튼 찾기
                    booking_buttons = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'btn_reserve') and contains(text(), '예매하기')]")

                    if not booking_buttons:
                        messagebox.showerror("오류", "예매하기 버튼을 찾을 수 없습니다.")
                        return False

                    # 시간대 정보와 함께 버튼 목록 생성
                    match_info = []
                    for i, btn in enumerate(booking_buttons):
                        try:
                            # 버튼의 부모 요소에서 경기 정보 찾기
                            parent_li = btn.find_element(By.XPATH, ".//ancestor::li[1]")

                            # 날짜 정보
                            date_element = parent_li.find_element(By.CSS_SELECTOR, ".date_num")
                            date = date_element.text.strip()

                            # 시간 정보
                            time_element = parent_li.find_element(By.CSS_SELECTOR, ".time_num")
                            time = time_element.text.strip()

                            # 팀 정보
                            team_element = parent_li.find_element(By.CSS_SELECTOR, ".team_name span")
                            teams = team_element.text.strip()

                            match_info.append({
                                'index': i + 1,
                                'date': date,
                                'time': time,
                                'teams': teams,
                                'button': btn
                            })
                        except:
                            match_info.append({
                                'index': i + 1,
                                'date': '정보없음',
                                'time': '정보없음',
                                'teams': '정보없음',
                                'button': btn
                            })

                    if len(match_info) == 1:
                        # 하나뿐이면 바로 처리
                        selected_match = match_info[0]
                    else:
                        # 여러개면 커스텀 선택 창 사용 (simpledialog 오류 방지)
                        choice = self.show_match_selection_dialog(match_info, root)

                        if not choice:
                            return False

                        selected_match = match_info[choice - 1]

                    # 선택된 경기의 예매 버튼 클릭 (팝업 차단 해결)
                    try:
                        # 현재 URL 저장
                        old_url = self.driver.current_url

                        # 팝업 차단을 우회하기 위해 현재 탭에서 직접 이동
                        href = selected_match['button'].get_attribute('href')

                        if href:
                            # href가 있으면 직접 이동
                            self.driver.get(href)

                            # 페이지 로딩 대기
                            import time
                            time.sleep(2)

                            new_url = self.driver.current_url

                            if new_url != old_url:
                                messagebox.showinfo("성공", f"선택한 경기: {selected_match['date']} {selected_match['time']} - {selected_match['teams']}\n\n예매 페이지로 이동했습니다!\n{new_url}")
                                return True
                            else:
                                messagebox.showwarning("실패", "페이지가 이동되지 않았습니다.")
                                return False
                        else:
                            # href가 없으면 JavaScript로 클릭 시도 (팝업 차단 우회)
                            self.driver.execute_script("""
                                var link = arguments[0];
                                if (link.href) {
                                    window.location.href = link.href;
                                } else {
                                    link.click();
                                }
                            """, selected_match['button'])

                            import time
                            time.sleep(2)

                            new_url = self.driver.current_url

                            if new_url != old_url:
                                messagebox.showinfo("성공", f"선택한 경기: {selected_match['date']} {selected_match['time']} - {selected_match['teams']}\n\nJavaScript로 예매 페이지로 이동했습니다!\n{new_url}")
                                return True
                            else:
                                messagebox.showwarning("실패", f"선택한 경기: {selected_match['date']} {selected_match['time']} - {selected_match['teams']}\n\n페이지가 이동되지 않았습니다. 팝업이 차단되었거나 버튼이 비활성화되어 있을 수 있습니다.")
                                return False

                    except Exception as e:
                        messagebox.showerror("클릭 오류", f"선택한 경기: {selected_match['date']} {selected_match['time']} - {selected_match['teams']}\n\n클릭 중 오류 발생:\n{str(e)}")
                        return False

                except Exception as e:
                    messagebox.showerror("전체 오류", f"예매 버튼 처리 중 오류:\n{str(e)}")
                    return False
            return False

        ticketlink_btn = tk.Button(main_frame, text="🏠 티켓링크 이동",
                                  font=("맑은 고딕", 10), width=18, height=2)
        ticketlink_btn.grid(row=3, column=0, padx=5, pady=5)
        ticketlink_btn.config(command=lambda: self.safe_execute_with_button(goto_ticketlink, ticketlink_btn, "티켓링크로 이동했습니다!"))

        refresh_btn = tk.Button(main_frame, text="🔄 페이지 새로고침",
                               font=("맑은 고딕", 10), width=18, height=2)
        refresh_btn.grid(row=3, column=1, padx=5, pady=5)
        refresh_btn.config(command=lambda: self.safe_execute_with_button(refresh_page, refresh_btn, "페이지를 새로고침했습니다!"))

        booking_btn = tk.Button(main_frame, text="🎫 예매 버튼 클릭",
                               font=("맑은 고딕", 10), width=18, height=2)
        booking_btn.grid(row=3, column=2, padx=5, pady=5)
        booking_btn.config(command=lambda: self.safe_execute_with_button(click_booking, booking_btn, "예매 버튼을 클릭했습니다!"))

        # 📍 창 관리 (Row 5)
        def get_window_info():
            if self.driver:
                try:
                    handles = self.driver.window_handles
                    current = self.driver.current_window_handle
                    title = self.driver.title
                    url = self.driver.current_url

                    info = f"현재 창 정보:\n"
                    info += f"제목: {title}\n"
                    info += f"URL: {url}\n"
                    info += f"총 창 수: {len(handles)}개"

                    self.show_copyable_message("창 정보", info, root)
                    return True
                except:
                    return False
            return False

        def switch_window():
            if self.driver:
                try:
                    handles = self.driver.window_handles
                    current = self.driver.current_window_handle

                    for handle in handles:
                        if handle != current:
                            self.driver.switch_to.window(handle)
                            return True
                    return False
                except:
                    return False
            return False

        info_btn = tk.Button(main_frame, text="📍 현재 창 정보",
                            font=("맑은 고딕", 10), width=18, height=2)
        info_btn.grid(row=5, column=0, padx=5, pady=5)
        info_btn.config(command=lambda: self.safe_execute_with_button(get_window_info, info_btn))

        switch_btn = tk.Button(main_frame, text="↔️ 창 전환",
                              font=("맑은 고딕", 10), width=18, height=2)
        switch_btn.grid(row=5, column=1, padx=5, pady=5)
        switch_btn.config(command=lambda: self.safe_execute_with_button(switch_window, switch_btn, "창을 전환했습니다!"))

        # 🎯 좌석 예매 (Row 7) - 여기가 핵심!
        def auto_seat_select():
            if self.driver:
                try:
                    # 자동배정 버튼 찾기
                    auto_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '자동')] | //a[contains(text(), '자동')] | //button[contains(text(), '배정')] | //a[contains(text(), '배정')]")

                    if auto_buttons:
                        auto_buttons[0].click()
                        messagebox.showinfo("성공", f"자동배정 버튼을 클릭했습니다!\n버튼 텍스트: {auto_buttons[0].text}")
                        return True
                    else:
                        # 더 넓은 범위로 버튼 찾기
                        all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        clickable_buttons = []
                        for btn in all_buttons:
                            if btn.is_displayed() and btn.is_enabled():
                                text = btn.text.strip()
                                if text and any(word in text for word in ['자동', '배정', '선택', '예매']):
                                    clickable_buttons.append(f"'{text}'")

                        if clickable_buttons:
                            messagebox.showwarning("실패", f"자동배정 버튼을 찾을 수 없습니다.\n\n찾은 버튼들: {', '.join(clickable_buttons[:5])}\n\n페이지를 확인하고 수동으로 버튼을 클릭해주세요.")
                        else:
                            messagebox.showerror("실패", "페이지에서 클릭 가능한 버튼을 찾을 수 없습니다.\n페이지가 완전히 로딩되었는지 확인해주세요.")
                        return False

                except Exception as e:
                    messagebox.showerror("오류", f"자동 좌석 선택 중 오류 발생:\n{str(e)}")
                    return False
            else:
                messagebox.showerror("연결 오류", "Chrome에 연결되지 않았습니다.")
                return False

        def section_select():
            if self.automation_functions:
                return self.automation_functions.select_seat_section(root)
            return False

        def continuous_booking():
            if self.automation_functions:
                self.automation_functions.continuous_booking_attempt(root)
                return True
            return False

        def auto_seat_booking():
            if self.automation_functions:
                # GUI 인스턴스를 함수에 전달하여 실시간 로그 사용 가능하게 함
                self.automation_functions.gui_instance = self
                self.add_log("🚀 완전 자동 예매 시작")
                self.automation_functions.auto_seat_booking(root)
                return True
            return False

        auto_seat_btn = tk.Button(main_frame, text="🪑 자동 좌석 선택",
                                 font=("맑은 고딕", 10), width=18, height=2, bg="lightyellow")
        auto_seat_btn.grid(row=7, column=0, padx=5, pady=5)
        auto_seat_btn.config(command=lambda: self.safe_execute_with_button(auto_seat_select, auto_seat_btn, "자동 좌석을 선택했습니다!"))

        section_btn = tk.Button(main_frame, text="🎯 구역 선택",
                               font=("맑은 고딕", 10), width=18, height=2, bg="lightgreen")
        section_btn.grid(row=7, column=1, padx=5, pady=5)
        section_btn.config(command=lambda: self.safe_execute_with_button(section_select, section_btn))

        repeat_btn = tk.Button(main_frame, text="🔄 반복 예매",
                              font=("맑은 고딕", 10), width=18, height=2, bg="lightcoral")
        repeat_btn.grid(row=7, column=2, padx=5, pady=5)
        repeat_btn.config(command=lambda: self.safe_execute_with_button(continuous_booking, repeat_btn))

        # 🚀 완전 자동 예매 버튼 (구역 선택부터 다음단계까지 자동 진행)
        auto_booking_btn = tk.Button(main_frame, text="🚀 완전 자동 예매",
                                    font=("맑은 고딕", 10), width=18, height=2, bg="gold")
        auto_booking_btn.grid(row=7, column=3, padx=5, pady=5)
        auto_booking_btn.config(command=lambda: self.safe_execute_with_button(auto_seat_booking, auto_booking_btn))

        # 🔧 고급 기능 (Row 9)
        def save_html():
            if self.driver:
                try:
                    html = self.driver.page_source
                    filename = f"page_source_{int(time.time())}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html)
                    self.show_copyable_message("HTML 저장 완료", f"파일명: {filename}\n크기: {len(html):,} bytes", root)
                    return True
                except:
                    return False
            return False

        save_btn = tk.Button(main_frame, text="💾 HTML 소스 저장",
                            font=("맑은 고딕", 10), width=18, height=2, bg="lightsteelblue")
        save_btn.grid(row=9, column=0, padx=5, pady=5)
        save_btn.config(command=lambda: self.safe_execute_with_button(save_html, save_btn))

        # 상태 체크 함수
        def check_status():
            if self.check_chrome_running():
                if self.driver:
                    status_label.config(text="Chrome 상태: ✅ 연결됨", fg="green")
                else:
                    status_label.config(text="Chrome 상태: 🔄 실행중 (연결 필요)", fg="orange")
            else:
                status_label.config(text="Chrome 상태: ❌ 실행되지 않음", fg="red")

            root.after(5000, check_status)  # 5초마다 체크

        # 초기 상태 체크
        check_status()

        # 사용법 안내
        help_label = tk.Label(root, text="💡 사용법: Chrome 시작 → Chrome 연결 → 티켓링크 이동 → 원하는 기능 사용",
                             font=("맑은 고딕", 9), fg="gray")
        help_label.pack(pady=10)

        root.mainloop()

    def run(self):
        """프로그램 시작"""
        print("티켓링크 자동화 프로그램을 시작합니다...")
        self.manual_control_gui()

if __name__ == "__main__":
    controller = ManualChromeController()
    controller.run()
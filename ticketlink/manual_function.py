import time
import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tkinter import simpledialog, messagebox

class TicketAutomationFunctions:
    def __init__(self, driver):
        self.driver = driver

    def show_copyable_message(self, title, content, root, window_width=700, window_height=500):
        """복사 가능한 메시지 창 표시"""
        result_window = tk.Toplevel(root)
        result_window.title(f"{title} (복사 가능)")
        result_window.geometry(f"{window_width}x{window_height}")
        result_window.transient(root)
        result_window.grab_set()

        # 텍스트 위젯과 스크롤바
        frame = tk.Frame(result_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                             font=("맑은 고딕", 10))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=text_widget.yview)

        # 내용 삽입
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)  # 읽기 전용

        # 복사 버튼
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

        # 창 중앙에 배치
        result_window.update_idletasks()
        x = (result_window.winfo_screenwidth() // 2) - (window_width // 2)
        y = (result_window.winfo_screenheight() // 2) - (window_height // 2)
        result_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def show_text_input_dialog(self, title, message, parent):
        """텍스트 입력 다이얼로그 (simpledialog 대체)"""
        dialog_window = tk.Toplevel(parent)
        dialog_window.title(title)
        dialog_window.geometry("400x300")
        dialog_window.transient(parent)
        dialog_window.grab_set()

        # 중앙 배치
        dialog_window.update_idletasks()
        x = (dialog_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog_window.winfo_screenheight() // 2) - (300 // 2)
        dialog_window.geometry(f"400x300+{x}+{y}")

        self.input_result = None

        # 메시지
        tk.Label(dialog_window, text=message, font=("맑은 고딕", 10),
                wraplength=350, justify='left').pack(pady=15)

        # 입력 필드
        entry_var = tk.StringVar()
        entry = tk.Entry(dialog_window, textvariable=entry_var, font=("맑은 고딕", 11), width=30)
        entry.pack(pady=10)
        entry.focus_set()

        # 버튼 프레임
        button_frame = tk.Frame(dialog_window)
        button_frame.pack(pady=20)

        def on_ok():
            self.input_result = entry_var.get().strip()
            dialog_window.destroy()

        def on_cancel():
            self.input_result = None
            dialog_window.destroy()

        tk.Button(button_frame, text="확인", command=on_ok,
                 font=("맑은 고딕", 10), width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="취소", command=on_cancel,
                 font=("맑은 고딕", 10), width=8).pack(side=tk.LEFT, padx=5)

        # Enter 키 바인딩
        entry.bind('<Return>', lambda e: on_ok())

        dialog_window.wait_window()
        return self.input_result

    def show_number_input_dialog(self, title, message, parent, minvalue=1, maxvalue=100, default=20):
        """숫자 입력 다이얼로그 (simpledialog 대체)"""
        dialog_window = tk.Toplevel(parent)
        dialog_window.title(title)
        dialog_window.geometry("400x250")
        dialog_window.transient(parent)
        dialog_window.grab_set()

        # 중앙 배치
        dialog_window.update_idletasks()
        x = (dialog_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog_window.winfo_screenheight() // 2) - (250 // 2)
        dialog_window.geometry(f"400x250+{x}+{y}")

        self.number_result = None

        # 메시지
        tk.Label(dialog_window, text=message, font=("맑은 고딕", 10),
                wraplength=350, justify='left').pack(pady=15)

        # 입력 필드
        entry_var = tk.StringVar(value=str(default))
        entry = tk.Entry(dialog_window, textvariable=entry_var, font=("맑은 고딕", 11), width=15)
        entry.pack(pady=10)
        entry.focus_set()
        entry.select_range(0, tk.END)

        # 범위 표시
        tk.Label(dialog_window, text=f"범위: {minvalue} - {maxvalue}",
                font=("맑은 고딕", 9), fg="gray").pack()

        # 버튼 프레임
        button_frame = tk.Frame(dialog_window)
        button_frame.pack(pady=20)

        def on_ok():
            try:
                value = int(entry_var.get())
                if minvalue <= value <= maxvalue:
                    self.number_result = value
                    dialog_window.destroy()
                else:
                    messagebox.showerror("범위 오류", f"{minvalue}와 {maxvalue} 사이의 숫자를 입력해주세요.")
            except ValueError:
                messagebox.showerror("입력 오류", "올바른 숫자를 입력해주세요.")

        def on_cancel():
            self.number_result = None
            dialog_window.destroy()

        tk.Button(button_frame, text="확인", command=on_ok,
                 font=("맑은 고딕", 10), width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="취소", command=on_cancel,
                 font=("맑은 고딕", 10), width=8).pack(side=tk.LEFT, padx=5)

        # Enter 키 바인딩
        entry.bind('<Return>', lambda e: on_ok())

        dialog_window.wait_window()
        return self.number_result

    def show_float_input_dialog(self, title, message, parent, minvalue=0.1, maxvalue=10.0, default=1.0):
        """소수점 입력 다이얼로그"""
        dialog_window = tk.Toplevel(parent)
        dialog_window.title(title)
        dialog_window.geometry("400x250")
        dialog_window.transient(parent)
        dialog_window.grab_set()

        # 중앙 배치
        dialog_window.update_idletasks()
        x = (dialog_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog_window.winfo_screenheight() // 2) - (250 // 2)
        dialog_window.geometry(f"400x250+{x}+{y}")

        self.float_result = None

        # 메시지
        tk.Label(dialog_window, text=message, font=("맑은 고딕", 10),
                wraplength=350, justify='left').pack(pady=15)

        # 입력 필드
        entry_var = tk.StringVar(value=str(default))
        entry = tk.Entry(dialog_window, textvariable=entry_var, font=("맑은 고딕", 11), width=15)
        entry.pack(pady=10)
        entry.focus_set()
        entry.select_range(0, tk.END)

        # 범위 표시
        tk.Label(dialog_window, text=f"범위: {minvalue} - {maxvalue}",
                font=("맑은 고딕", 9), fg="gray").pack()

        # 버튼 프레임
        button_frame = tk.Frame(dialog_window)
        button_frame.pack(pady=20)

        def on_ok():
            try:
                value = float(entry_var.get())
                if minvalue <= value <= maxvalue:
                    self.float_result = value
                    dialog_window.destroy()
                else:
                    messagebox.showerror("범위 오류", f"{minvalue}와 {maxvalue} 사이의 숫자를 입력해주세요.")
            except ValueError:
                messagebox.showerror("입력 오류", "올바른 숫자를 입력해주세요.")

        def on_cancel():
            self.float_result = None
            dialog_window.destroy()

        tk.Button(button_frame, text="확인", command=on_ok,
                 font=("맑은 고딕", 10), width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="취소", command=on_cancel,
                 font=("맑은 고딕", 10), width=8).pack(side=tk.LEFT, padx=5)

        # Enter 키 바인딩
        entry.bind('<Return>', lambda e: on_ok())

        dialog_window.wait_window()
        return self.float_result

    def show_grade_selection_dialog(self, available_grades, parent):
        """사용 가능한 구역들을 리스트로 보여주고 선택하게 하는 다이얼로그"""
        import tkinter as tk
        from tkinter import ttk

        self.selected_grade = None

        # 다이얼로그 창 생성
        dialog_window = tk.Toplevel(parent)
        dialog_window.title("⚡ 구역 선택")
        dialog_window.geometry("500x600")
        dialog_window.resizable(False, False)
        dialog_window.grab_set()

        # 창을 부모 중앙에 위치
        dialog_window.transient(parent)
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 300
        dialog_window.geometry(f"500x600+{x}+{y}")

        # 헤더
        header_frame = tk.Frame(dialog_window, bg="#2E5BFF", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="⚡ 구역 선택",
                font=("맑은 고딕", 16, "bold"),
                fg="white", bg="#2E5BFF").pack(expand=True)

        # 정보 라벨
        info_frame = tk.Frame(dialog_window, bg="#F8F9FA", height=50)
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(info_frame, text=f"📍 현재 페이지에서 {len(available_grades)}개의 구역을 발견했습니다.",
                font=("맑은 고딕", 10), bg="#F8F9FA").pack(pady=10)

        # 리스트 프레임
        list_frame = tk.Frame(dialog_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 검색 기능
        search_frame = tk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="🔍 검색:", font=("맑은 고딕", 9)).pack(side=tk.LEFT)

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=("맑은 고딕", 9))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # 리스트박스와 스크롤바
        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        # 스크롤바
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 리스트박스
        listbox = tk.Listbox(listbox_frame,
                           yscrollcommand=scrollbar.set,
                           font=("맑은 고딕", 11),
                           height=15,
                           selectmode=tk.SINGLE,
                           activestyle="none",
                           selectbackground="#2E5BFF",
                           selectforeground="white")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # 구역 리스트 초기 로드
        def load_grades(filter_text=""):
            listbox.delete(0, tk.END)
            for grade in available_grades:
                if filter_text.lower() in grade.lower():
                    listbox.insert(tk.END, grade)

        load_grades()

        # 검색 기능
        def on_search_change(*args):
            load_grades(search_var.get())

        search_var.trace("w", on_search_change)

        # 더블클릭으로 선택
        def on_double_click(event):
            selection = listbox.curselection()
            if selection:
                self.selected_grade = listbox.get(selection[0])
                dialog_window.destroy()

        listbox.bind("<Double-Button-1>", on_double_click)

        # 버튼 프레임
        button_frame = tk.Frame(dialog_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        def on_select():
            selection = listbox.curselection()
            if selection:
                self.selected_grade = listbox.get(selection[0])
                dialog_window.destroy()
            else:
                messagebox.showwarning("선택 없음", "구역을 선택해주세요.", parent=dialog_window)

        def on_cancel():
            self.selected_grade = None
            dialog_window.destroy()

        # 버튼들
        tk.Button(button_frame, text="✅ 선택", command=on_select,
                 font=("맑은 고딕", 10, "bold"),
                 bg="#28a745", fg="white",
                 width=12, height=2).pack(side=tk.RIGHT, padx=(5, 0))

        tk.Button(button_frame, text="❌ 취소", command=on_cancel,
                 font=("맑은 고딕", 10),
                 bg="#dc3545", fg="white",
                 width=12, height=2).pack(side=tk.RIGHT, padx=(5, 0))

        # 새로고침 버튼
        def refresh_grades():
            try:
                messagebox.showinfo("새로고침", "구역 목록을 새로고침하는 중...", parent=dialog_window)
                # JavaScript 다시 실행
                refresh_script = """
                function findAllAvailableGrades() {
                    const selectors = [
                        '[id*="seat_grade_"]',
                        '.seat_grade',
                        '.seat_detail_info',
                        '[ng-click*="grade"]',
                        '[ng-click*="selectGrade"]',
                        'a[href*="grade"]',
                        'button[onclick*="grade"]'
                    ];

                    let grades = [];
                    const seen = new Set();

                    for (const selector of selectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            for (const elem of elements) {
                                const text = (elem.textContent || elem.innerText || '').trim();

                                if (text && text.length > 0 && text.length < 50 &&
                                    elem.offsetParent !== null && !seen.has(text)) {

                                    if (elem.tagName === 'A' || elem.tagName === 'BUTTON' ||
                                        elem.onclick || elem.getAttribute('ng-click') ||
                                        elem.getAttribute('href') ||
                                        window.getComputedStyle(elem).cursor === 'pointer') {

                                        grades.push(text);
                                        seen.add(text);
                                    }
                                }
                            }
                        } catch(e) {
                            console.log('Grade search error:', e);
                        }
                    }

                    grades.sort((a, b) => {
                        const aHasNumber = /\d/.test(a.toLowerCase());
                        const bHasNumber = /\d/.test(b.toLowerCase());
                        if (aHasNumber && !bHasNumber) return -1;
                        if (!aHasNumber && bHasNumber) return 1;
                        return a.toLowerCase().localeCompare(b.toLowerCase());
                    });

                    return grades;
                }
                return findAllAvailableGrades();
                """

                new_grades = self.driver.execute_script(refresh_script)
                if new_grades:
                    available_grades.clear()
                    available_grades.extend(new_grades)
                    load_grades(search_var.get())
                    messagebox.showinfo("완료", f"{len(new_grades)}개의 구역을 발견했습니다.", parent=dialog_window)
                else:
                    messagebox.showwarning("경고", "구역을 찾을 수 없습니다.", parent=dialog_window)
            except Exception as e:
                messagebox.showerror("오류", f"새로고침 중 오류: {str(e)}", parent=dialog_window)

        tk.Button(button_frame, text="🔄 새로고침", command=refresh_grades,
                 font=("맑은 고딕", 9),
                 width=12, height=2).pack(side=tk.LEFT)

        # 포커스 설정
        search_entry.focus_set()

        # Enter 키 바인딩
        def on_enter(event):
            on_select()

        dialog_window.bind('<Return>', on_enter)
        listbox.bind('<Return>', on_enter)

        dialog_window.wait_window()
        return self.selected_grade

    def select_seat_section(self, root, seat_section=None):
        """좌석 구역 선택 기능"""
        if not seat_section:
            seat_section = self.show_text_input_dialog("좌석 구역 선택",
                "원하는 좌석 구역을 입력하세요.\n\n예시:\n- 응원특별석\n- 1루 K8\n- 메디힐테이블석\n- 챔피언석\n- 중앙테이블석",
                root)

        if not seat_section:
            return False

        try:
            # 현재 페이지에서 좌석 구역 찾기
            seat_elements = []

            # 방법 1: seat_grade_ ID로 찾기
            try:
                grade_elements = self.driver.find_elements(By.CSS_SELECTOR, "[id^='seat_grade_']")
                for element in grade_elements:
                    if seat_section in element.text:
                        seat_elements.append(element)
            except:
                pass

            # 방법 2: 텍스트로 직접 찾기
            try:
                text_elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{seat_section}')]")
                seat_elements.extend(text_elements)
            except:
                pass

            # 방법 3: 클릭 가능한 요소 중에서 찾기
            try:
                clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, "a, button, div[onclick], span[onclick]")
                for element in clickable_elements:
                    if seat_section in element.text:
                        seat_elements.append(element)
            except:
                pass

            if seat_elements:
                # 첫 번째 매칭 요소 클릭
                target_element = seat_elements[0]
                self.driver.execute_script("arguments[0].click();", target_element)

                result_msg = f"✅ 좌석 구역 선택 성공!\n\n"
                result_msg += f"🎯 선택된 구역: {seat_section}\n"
                result_msg += f"📍 요소 정보: {target_element.tag_name} - {target_element.text[:50]}\n"
                result_msg += f"🔗 요소 ID: {target_element.get_attribute('id')}\n"
                result_msg += f"📊 총 매칭 요소: {len(seat_elements)}개\n"
                result_msg += f"⏰ 실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}"

                self.show_copyable_message("좌석 구역 선택 결과", result_msg, root)
                return True
            else:
                result_msg = f"❌ 좌석 구역을 찾을 수 없습니다.\n\n"
                result_msg += f"🎯 검색한 구역: {seat_section}\n"
                result_msg += f"💡 확인사항:\n"
                result_msg += f"   - 구역명이 정확한지 확인해주세요\n"
                result_msg += f"   - 페이지가 완전히 로드되었는지 확인해주세요\n"
                result_msg += f"   - 다른 탭이나 팝업창이 열려있는지 확인해주세요\n"
                result_msg += f"⏰ 실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}"

                self.show_copyable_message("좌석 구역 선택 실패", result_msg, root)
                return False

        except Exception as e:
            error_msg = f"❌ 오류가 발생했습니다.\n\n"
            error_msg += f"🎯 시도한 구역: {seat_section}\n"
            error_msg += f"🔥 오류 내용: {str(e)}\n"
            error_msg += f"⏰ 실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}"

            self.show_copyable_message("좌석 선택 오류", error_msg, root)
            return False

    def smart_ticket_booking(self, root):
        """스마트 티켓 예매 - auto_seat_booking과 동일"""
        return self.auto_seat_booking(root)

    def show_booking_result(self, result_log, success_count, fail_count, alert_count, start_time, root):
        """예매 결과를 표시하는 메서드"""
        end_time = time.time()
        total_time = end_time - start_time

        result_log.append("=" * 60)
        result_log.append(f"🎉 좌석 예매 성공!")
        result_log.append(f"✅ 성공: {success_count}회")
        result_log.append(f"❌ 실패: {fail_count}회")
        result_log.append(f"⚠️ Alert 처리: {alert_count}회")
        result_log.append(f"⏰ 소요시간: {total_time:.1f}초")
        result_log.append(f"🕐 완료 시간: {time.strftime('%H:%M:%S')}")
        result_log.append("")
        result_log.append("🎊 좌석이 선택되었습니다!")
        result_log.append("📋 다음 단계(결제)로 진행하세요.")

        final_result = "\n".join(result_log)
        self.show_copyable_message("좌석 예매 성공!", final_result, root, 800, 600)

    def auto_seat_booking(self, root):
        """⚡ 초고속 좌석 자동 예매 - JavaScript 기반"""
        # 1단계: 현재 페이지에서 사용 가능한 구역들을 JavaScript로 빠르게 찾기
        available_grades_script = """
        function findAllAvailableGrades() {
            const selectors = [
                '[id*="seat_grade_"]',
                '.seat_grade',
                '.seat_detail_info',
                '[ng-click*="grade"]',
                '[ng-click*="selectGrade"]',
                'a[href*="grade"]',
                'button[onclick*="grade"]'
            ];

            let grades = [];
            const seen = new Set();

            for (const selector of selectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const elem of elements) {
                        const text = (elem.textContent || elem.innerText || '').trim();

                        // 구역/등급으로 보이는 텍스트 필터링
                        if (text && text.length > 0 && text.length < 50 &&
                            elem.offsetParent !== null && !seen.has(text)) {

                            // 클릭 가능한 요소인지 확인
                            if (elem.tagName === 'A' || elem.tagName === 'BUTTON' ||
                                elem.onclick || elem.getAttribute('ng-click') ||
                                elem.getAttribute('href') ||
                                window.getComputedStyle(elem).cursor === 'pointer') {

                                grades.push({
                                    text: text,
                                    element: elem,
                                    tagName: elem.tagName,
                                    id: elem.id || 'none',
                                    className: elem.className || 'none'
                                });
                                seen.add(text);
                            }
                        }
                    }
                } catch(e) {
                    console.log('Grade search error:', e);
                }
            }

            // 결과 정렬 (일반적인 구역명 순서)
            grades.sort((a, b) => {
                const aText = a.text.toLowerCase();
                const bText = b.text.toLowerCase();

                // 숫자가 포함된 것들을 앞쪽으로
                const aHasNumber = /\d/.test(aText);
                const bHasNumber = /\d/.test(bText);

                if (aHasNumber && !bHasNumber) return -1;
                if (!aHasNumber && bHasNumber) return 1;

                return aText.localeCompare(bText);
            });

            return grades.map(g => g.text);
        }

        return findAllAvailableGrades();
        """

        try:
            messagebox.showinfo("구역 검색 중", "페이지에서 사용 가능한 구역을 검색하고 있습니다...", parent=root)
            available_grades = self.driver.execute_script(available_grades_script)

            if not available_grades:
                messagebox.showerror("구역 없음", "현재 페이지에서 선택 가능한 구역을 찾을 수 없습니다.\n좌석 선택 페이지에서 다시 시도해주세요.", parent=root)
                return

        except Exception as e:
            messagebox.showerror("오류", f"구역 검색 중 오류가 발생했습니다:\n{str(e)}", parent=root)
            return

        # 2단계: 사용자가 구역 선택할 수 있는 다이얼로그
        target_grade = self.show_grade_selection_dialog(available_grades, root)

        if not target_grade:
            return

        # 무한대 옵션 제공
        use_infinite = messagebox.askyesno("무한 시도", "무한대로 시도하시겠습니까?\n\n'예' = 성공할 때까지 무한 시도\n'아니요' = 횟수 제한", parent=root)

        if use_infinite:
            max_attempts = float('inf')  # 무한대
            result_log = [f"🚀 무한 자동 예매 모드: {target_grade}"]
        else:
            max_attempts = self.show_number_input_dialog("시도 횟수",
                "몇 번 시도하시겠습니까?", root, minvalue=1, maxvalue=999, default=50)
            if not max_attempts:
                return

        interval = self.show_float_input_dialog("클릭 간격",
            "클릭 간격(초) - JavaScript는 매우 빠름", root, minvalue=0.05, maxvalue=1.0, default=0.3)

        if interval is None:
            return

        # 확인
        attempt_text = "무한대" if max_attempts == float('inf') else f"{max_attempts}번"
        if not messagebox.askyesno("🚀 완전 자동 예매", f"구역: {target_grade}\n시도: {attempt_text}\n간격: {interval}초\n\n🚀 구역 선택부터 좌석 확정까지 자동 진행?", parent=root):
            return

        if max_attempts != float('inf'):
            result_log = []
            result_log.append(f"🚀 완전 자동 예매 시작: {target_grade}")
        result_log.append("-" * 40)
        start_time = time.time()

        # 1단계: TicketLink 정확한 구조로 등급 선택
        result_log.append("🎯 TicketLink 등급 구조로 선택...")

        grade_script = f"""
        function selectGradeByStructure() {{
            // TicketLink 실제 구조: ul#select_seat_grade > li[id^='seat_grade_'] > a
            const gradeList = document.querySelector('#select_seat_grade');
            if (!gradeList) {{
                return '❌ 등급 리스트를 찾을 수 없음';
            }}

            const gradeItems = gradeList.querySelectorAll('li[id^="seat_grade_"]');
            const targetGrade = '{target_grade}';

            for (const gradeItem of gradeItems) {{
                try {{
                    const gradeText = gradeItem.textContent || gradeItem.innerText || '';

                    if (gradeText.includes(targetGrade) && gradeItem.offsetParent !== null) {{
                        // 등급 아이템 내의 <a> 태그 찾아서 클릭
                        const gradeLink = gradeItem.querySelector('a[href="#"]');
                        if (gradeLink) {{
                            gradeLink.click();

                            // 잠시 대기 후 블록/구역 리스트 확인
                            setTimeout(() => {{
                                const zones = gradeItem.querySelector('ul.seat_zone');
                                if (zones) {{
                                    console.log('블록/구역 리스트 로드됨:', zones.children.length + '개');
                                }}
                            }}, 500);

                            return `✅ 등급 선택 성공: ${{gradeText.trim()}}`;
                        }}
                    }}
                }} catch(e) {{
                    console.log('등급 선택 오류:', e);
                }}
            }}

            return '❌ 지정된 등급을 찾을 수 없음';
        }}
        return selectGradeByStructure();
        """

        try:
            grade_result = self.driver.execute_script(grade_script)
            result_log.append(grade_result)

            if "❌" in grade_result:
                final_result = "\n".join(result_log)
                self.show_copyable_message("구역 선택 실패", final_result, root, 500, 300)
                return

            # 등급 선택 후 "직접선택" 버튼이 나타날 때까지 대기
            direct_button_wait = self.driver.execute_script("""
            return new Promise((resolve) => {
                let attempts = 0;
                const maxAttempts = 20; // 2초간 0.1초 간격으로 체크

                function checkDirectButton() {
                    // XPath를 사용하여 "직접선택" 텍스트를 포함한 버튼 찾기
                    let directButton = null;

                    // XPath로 직접선택 버튼 찾기
                    const xpathSelectors = [
                        '//button[contains(text(), "직접선택")]',
                        '//a[contains(text(), "직접선택")]',
                        '//input[@type="button" and contains(@value, "직접선택")]'
                    ];

                    for (let xpath of xpathSelectors) {
                        try {
                            const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                            if (result.singleNodeValue && result.singleNodeValue.offsetParent !== null) {
                                directButton = result.singleNodeValue;
                                break;
                            }
                        } catch (e) {
                            console.log('XPath 오류:', e);
                        }
                    }

                    // CSS 선택자로 ng-click 속성이나 클래스명으로 찾기
                    if (!directButton) {
                        const cssSelectors = [
                            '[ng-click*="direct"]',
                            '.direct',
                            '[onclick*="direct"]',
                            'button[title*="직접"]',
                            'a[title*="직접"]'
                        ];

                        for (let selector of cssSelectors) {
                            try {
                                const element = document.querySelector(selector);
                                if (element && element.offsetParent !== null) {
                                    directButton = element;
                                    break;
                                }
                            } catch (e) {
                                console.log('CSS 선택자 오류:', e);
                            }
                        }
                    }

                    if (directButton && directButton.offsetParent !== null) {
                        resolve({success: true, message: '직접선택 버튼 발견', element: directButton.tagName});
                        return;
                    }

                    attempts++;
                    if (attempts >= maxAttempts) {
                        resolve({success: false, message: '직접선택 버튼 대기 시간 초과'});
                    } else {
                        setTimeout(checkDirectButton, 100);
                    }
                }

                checkDirectButton();
            });
            """)

            result_log.append(f"🔍 직접선택 버튼 대기 결과: {direct_button_wait.get('message', '결과 없음')}")

            # 등급 선택 후 "직접선택" 버튼 클릭
            result_log.append("🔧 '직접선택' 버튼 클릭 중...")
            direct_select_script = """
            function clickDirectSelectButton() {
                // "직접선택" 버튼 찾기
                const directSelectSelectors = [
                    '//button[contains(text(), "직접선택")]',
                    '//a[contains(text(), "직접선택")]',
                    '//input[@value="직접선택"]',
                    '//span[contains(text(), "직접선택")]//parent::*',
                    '[onclick*="direct"], [onclick*="Direct"], [onclick*="직접"]'
                ];

                for (const selector of directSelectSelectors) {
                    try {
                        if (selector.startsWith('//')) {
                            // XPath 선택자
                            const result = document.evaluate(selector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                            if (result.singleNodeValue && result.singleNodeValue.offsetParent !== null) {
                                result.singleNodeValue.click();
                                return '✅ 직접선택 버튼 클릭 성공';
                            }
                        } else {
                            // CSS 선택자
                            const elements = document.querySelectorAll(selector);
                            for (const element of elements) {
                                if (element.offsetParent !== null) {
                                    element.click();
                                    return '✅ 직접선택 버튼 클릭 성공';
                                }
                            }
                        }
                    } catch(e) {
                        console.log('직접선택 버튼 찾기 오류:', e);
                        continue;
                    }
                }

                return '⚠️ 직접선택 버튼을 찾을 수 없음';
            }
            return clickDirectSelectButton();
            """

            try:
                direct_result = self.driver.execute_script(direct_select_script)
                result_log.append(direct_result)

                if hasattr(self, 'gui_instance') and self.gui_instance:
                    self.gui_instance.add_log(f"🔧 {direct_result}")

                # 블록 요소가 나타날 때까지 대기 (최대 10초)
                result_log.append("⏳ 블록 요소가 로드될 때까지 대기 중...")
                if hasattr(self, 'gui_instance') and self.gui_instance:
                    self.gui_instance.add_log("⏳ 블록 요소가 로드될 때까지 대기 중...")

                wait_script = """
                return new Promise((resolve) => {
                    let attempts = 0;
                    const maxAttempts = 20; // 2초간 0.1초 간격으로 체크

                    function checkBlocks() {
                        const zoneLists = document.querySelectorAll('ul.seat_zone');
                        const totalBlocks = Array.from(zoneLists).reduce((sum, list) =>
                            sum + list.querySelectorAll('li[id^="seat_zone_"] a[href="#"]').length, 0);

                        console.log(`블록 대기 중... ${attempts}/${maxAttempts}, 발견된 블록: ${totalBlocks}`);

                        if (totalBlocks > 0) {
                            resolve({
                                success: true,
                                zoneListCount: zoneLists.length,
                                totalBlocks: totalBlocks,
                                message: `✅ 블록 로드 완료: ${zoneLists.length}개 리스트, ${totalBlocks}개 블록`
                            });
                        } else if (attempts >= maxAttempts) {
                            resolve({
                                success: false,
                                zoneListCount: zoneLists.length,
                                totalBlocks: totalBlocks,
                                message: `❌ 블록 로드 실패: ${zoneLists.length}개 리스트, ${totalBlocks}개 블록`
                            });
                        } else {
                            attempts++;
                            setTimeout(checkBlocks, 100);
                        }
                    }

                    checkBlocks();
                });
                """

                block_status = self.driver.execute_script(wait_script)
                result_log.append(f"📋 {block_status['message']}")
                if hasattr(self, 'gui_instance') and self.gui_instance:
                    self.gui_instance.add_log(f"📋 {block_status['message']}")

                if not block_status['success']:
                    result_log.append("❌ 블록 로딩 실패 - 다음 시도로 넘어감")
                    if hasattr(self, 'gui_instance') and self.gui_instance:
                        self.gui_instance.add_log("❌ 블록 로딩 실패 - 다음 시도")
                    # continue 대신 return으로 함수를 종료하거나 루프를 다시 시작
                    return

            except Exception as e:
                result_log.append(f"⚠️ 직접선택 버튼 클릭 시도 중 오류: {str(e)}")
                return

        except Exception as e:
            result_log.append(f"❌ 구역 선택 실패: {str(e)}")
            final_result = "\n".join(result_log)
            self.show_copyable_message("구역 선택 오류", final_result, root, 500, 300)
            return

        # 2단계: TicketLink 구조 기반 블록/좌석 선택
        result_log.append("⚡ TicketLink 구조 기반 블록/좌석 선택 시작")

        seat_click_script = """
        function selectAvailableBlockAndSeat() {
            console.log('=== 블록 선택 함수 시작 ===');

            // 1단계: 실제 HTML 구조에서 사용 가능한 블록/구역 찾기
            const zoneLists = document.querySelectorAll('ul.seat_zone');
            console.log('발견된 seat_zone 리스트:', zoneLists.length);

            if (zoneLists.length === 0) {
                return {success: false, message: '❌ 블록/구역 리스트 없음'};
            }

            const availableZones = [];

            // 모든 seat_zone 리스트 확인
            for (const zoneList of zoneLists) {
                const zoneItems = zoneList.querySelectorAll('li[id^="seat_zone_"]');
                console.log('리스트에서 발견된 블록:', zoneItems.length);

                for (const zoneItem of zoneItems) {
                    try {
                        const zoneText = zoneItem.textContent || zoneItem.innerText || '';
                        console.log('블록 텍스트:', zoneText);

                        // 실제 클릭 가능한 a 태그 찾기
                        const clickableLink = zoneItem.querySelector('a[href="#"]');

                        if (clickableLink && zoneItem.offsetParent !== null &&
                            !zoneText.includes('0석') && !zoneText.includes('매진')) {

                            // 잔여석 수 확인 (429석 같은 형태)
                            const remainSpan = zoneItem.querySelector('span.seat .ng-binding');
                            const remainCount = remainSpan ? parseInt(remainSpan.textContent) : 1;

                            if (remainCount > 0) {
                                availableZones.push({
                                    element: clickableLink,  // a 태그를 클릭해야 함
                                    text: zoneText.trim(),
                                    zoneItem: zoneItem,
                                    remainCount: remainCount,
                                    ngClass: clickableLink.getAttribute('ng-class')
                                });
                                console.log('사용 가능한 블록 추가:', zoneText.trim(), '잔여석:', remainCount);
                            }
                        }
                    } catch(e) {
                        console.log('블록 확인 오류:', e);
                    }
                }
            }

            console.log('총 사용 가능한 블록:', availableZones.length);

            if (availableZones.length === 0) {
                return {success: false, message: '❌ 사용 가능한 블록 없음'};
            }

            // 2단계: 가장 좋은 블록 선택 (잔여석이 많은 순서대로)
            availableZones.sort((a, b) => b.remainCount - a.remainCount);
            const targetZone = availableZones[0];

            console.log('선택된 블록:', targetZone.text, '잔여석:', targetZone.remainCount);

            // 3단계: 4가지 방법으로 블록 클릭 시도
            const clickMethods = [
                {
                    name: 'A태그 직접 클릭',
                    action: () => {
                        targetZone.element.click();
                        return true;
                    }
                },
                {
                    name: 'MouseEvent 디스패치',
                    action: () => {
                        const mouseEvent = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        targetZone.element.dispatchEvent(mouseEvent);
                        return true;
                    }
                },
                {
                    name: 'LI 요소 클릭',
                    action: () => {
                        targetZone.zoneItem.click();
                        return true;
                    }
                },
                {
                    name: 'Angular 스코프 실행',
                    action: () => {
                        if (typeof angular !== 'undefined') {
                            const element = angular.element(targetZone.element);
                            const scope = element.scope();
                            if (scope && scope.selectZone) {
                                scope.selectZone(targetZone.element.getAttribute('data-zone-id'));
                                scope.$apply();
                                return true;
                            }
                        }
                        return false;
                    }
                }
            ];

            let clickSuccess = false;
            let usedMethod = '';

            for (const method of clickMethods) {
                try {
                    console.log('시도 중:', method.name);
                    const result = method.action();
                    if (result) {
                        clickSuccess = true;
                        usedMethod = method.name;
                        console.log('성공:', method.name);
                        break;
                    }
                } catch (e) {
                    console.log(method.name + ' 실패:', e);
                }
            }

            if (clickSuccess) {
                console.log('블록 클릭 성공, 이제 Canvas에서 좌석 선택 시도');

                // 블록 선택 후 Canvas 로딩 대기 및 즉시 좌석 선택 시도
                setTimeout(() => {
                    console.log('Canvas 좌석 선택 시작...');

                    // 더 강력한 Canvas 좌석 클릭 시도
                    const result = tryCanvasSeatSelectionImproved();
                    console.log('Canvas 좌석 선택 결과:', result);
                }, 1000); // 1초 대기로 Canvas 완전 로딩 보장

                return {
                    success: true,
                    message: `✅ ${usedMethod}로 블록 클릭 성공: ${targetZone.text}`,
                    method: usedMethod,
                    blockText: targetZone.text,
                    remainCount: targetZone.remainCount
                };
            } else {
                return {
                    success: false,
                    message: `❌ 모든 클릭 방법 실패: ${targetZone.text}`
                };
            }

            // 개선된 Canvas 좌석 선택 함수
            function tryCanvasSeatSelectionImproved() {
                console.log('=== 개선된 Canvas 좌석 선택 시작 ===');

                // 1. Canvas 요소 분석 및 선택
                const canvases = document.querySelectorAll('canvas');
                console.log('총 Canvas 개수:', canvases.length);

                if (canvases.length === 0) {
                    console.log('❌ Canvas 요소 없음');
                    return false;
                }

                // Canvas들의 정보 출력
                for (let i = 0; i < canvases.length; i++) {
                    const canvas = canvases[i];
                    const rect = canvas.getBoundingClientRect();
                    const style = window.getComputedStyle(canvas);
                    console.log(`Canvas ${i}: 크기=${rect.width}x${rect.height}, z-index=${style.zIndex}, display=${style.display}`);
                }

                // 가장 적합한 Canvas 선택 (보통 크기가 크고 z-index가 높은 것)
                let bestCanvas = null;
                let bestScore = -1;

                for (const canvas of canvases) {
                    const rect = canvas.getBoundingClientRect();
                    const style = window.getComputedStyle(canvas);
                    const zIndex = parseInt(style.zIndex) || 0;

                    if (style.display === 'none' || rect.width === 0 || rect.height === 0) continue;

                    // 점수 계산: 크기 + z-index
                    const score = (rect.width * rect.height) / 1000 + zIndex * 10;

                    if (score > bestScore) {
                        bestScore = score;
                        bestCanvas = canvas;
                    }
                }

                if (!bestCanvas) {
                    console.log('❌ 적합한 Canvas 없음');
                    return false;
                }

                console.log('선택된 Canvas 점수:', bestScore);
                const rect = bestCanvas.getBoundingClientRect();
                console.log('선택된 Canvas 크기:', rect.width, 'x', rect.height);

                // 2. Canvas 좌석 데이터 로딩 대기
                console.log('Canvas 좌석 데이터 로딩 대기 중...');

                // Promise 방식으로 Canvas 데이터 로딩 대기
                return new Promise((resolve) => {
                    waitForCanvasSeats(bestCanvas).then(() => {
                        proceedWithSeatSelection(bestCanvas, resolve);
                    });
                });
            }

            // 좌석 선택 진행 함수
            function proceedWithSeatSelection(bestCanvas, resolve) {

                const rect = bestCanvas.getBoundingClientRect();

                // 3. 좌석 선택 전 초기 상태 확인
                const initialSeatCheck = checkSeatSelectionBasic();
                console.log('초기 좌석 선택 상태:', initialSeatCheck.success);

                if (initialSeatCheck.success) {
                    console.log('✅ 이미 좌석이 선택되어 있음');
                    resolve(true);
                    return;
                }

                // 4. Canvas 좌석 데이터가 로드되었는지 확인
                const hasCanvasData = checkCanvasHasSeats(bestCanvas);
                console.log('Canvas 좌석 데이터 존재:', hasCanvasData);

                if (!hasCanvasData) {
                    console.log('❌ Canvas에 좌석 데이터가 로드되지 않음');
                    resolve(false);
                    return;
                }

                // 5. 전략적 좌석 클릭 (무대에 가까운 순서)
                const clickStrategies = [
                    // 1순위: 무대 앞쪽 중앙
                    { name: '무대 앞쪽 중앙', areas: [
                        { x: 0.45, y: 0.1, width: 0.1, height: 0.05 },
                        { x: 0.4, y: 0.15, width: 0.2, height: 0.1 }
                    ]},

                    // 2순위: 무대 앞쪽 좌우
                    { name: '무대 앞쪽 좌우', areas: [
                        { x: 0.25, y: 0.1, width: 0.15, height: 0.1 },
                        { x: 0.6, y: 0.1, width: 0.15, height: 0.1 }
                    ]},

                    // 3순위: 중앙 부분
                    { name: '중앙 부분', areas: [
                        { x: 0.3, y: 0.25, width: 0.4, height: 0.2 }
                    ]},

                    // 4순위: 넓은 범위
                    { name: '넓은 범위', areas: [
                        { x: 0.2, y: 0.2, width: 0.6, height: 0.6 }
                    ]}
                ];

                let seatSelected = false;

                for (const strategy of clickStrategies) {
                    if (seatSelected) break;

                    console.log(`시도 중: ${strategy.name}`);

                    for (const area of strategy.areas) {
                        if (seatSelected) break;

                        for (let attempt = 0; attempt < 5; attempt++) {
                            // 영역 내 랜덤 위치 생성
                            const randomX = area.x + (Math.random() * area.width);
                            const randomY = area.y + (Math.random() * area.height);

                            const clickX = rect.left + (randomX * rect.width);
                            const clickY = rect.top + (randomY * rect.height);

                            console.log(`${strategy.name} 클릭 ${attempt + 1}: (${Math.round(clickX)}, ${Math.round(clickY)})`);

                            // 강력한 클릭 이벤트 시퀀스 실행
                            performStrongClick(bestCanvas, clickX, clickY);

                            // 클릭 후 좌석 선택 확인
                            setTimeout(() => {
                                const seatCheck = checkSeatSelectionBasic();
                                if (seatCheck.success) {
                                    console.log(`✅ ${strategy.name}에서 좌석 선택 성공:`, seatCheck.seatInfo);
                                    seatSelected = true;
                                    resolve(true);
                                    return;
                                }
                            }, 300);

                            // 각 클릭 사이 잠시 대기
                            if (!seatSelected) {
                                setTimeout(() => {}, 200);
                            }
                        }
                    }
                }

                // 모든 시도 후에도 선택되지 않으면 실패
                setTimeout(() => {
                    if (!seatSelected) {
                        console.log('❌ 모든 전략으로 좌석 선택 실패');
                        resolve(false);
                    }
                }, 5000); // 5초 후 타임아웃
            }

            // 강력한 클릭 이벤트 실행 함수
            function performStrongClick(canvas, x, y) {
                const events = [
                    new MouseEvent('mousedown', {
                        bubbles: true, cancelable: true, view: window,
                        clientX: x, clientY: y, button: 0, buttons: 1
                    }),
                    new MouseEvent('mouseup', {
                        bubbles: true, cancelable: true, view: window,
                        clientX: x, clientY: y, button: 0, buttons: 0
                    }),
                    new MouseEvent('click', {
                        bubbles: true, cancelable: true, view: window,
                        clientX: x, clientY: y, button: 0, buttons: 0
                    })
                ];

                // 이벤트 순차 실행
                canvas.dispatchEvent(events[0]); // mousedown
                setTimeout(() => {
                    canvas.dispatchEvent(events[1]); // mouseup
                    setTimeout(() => {
                        canvas.dispatchEvent(events[2]); // click
                    }, 10);
                }, 50);
            }

            // 기본 좌석 선택 확인 함수
            function checkSeatSelectionBasic() {
                // Angular 상태 우선 확인
                if (typeof angular !== 'undefined') {
                    try {
                        const body = document.querySelector('body, [ng-app], [ng-controller]');
                        if (body) {
                            const scope = angular.element(body).scope();
                            if (scope && scope.selected && scope.selected.selectedSeatsAndZones) {
                                const seats = scope.selected.selectedSeatsAndZones;
                                if (seats.length > 0) {
                                    const seatInfo = seats[0].seatName || seats[0].name || JSON.stringify(seats[0]);
                                    return {success: true, seatInfo: `Angular: ${seatInfo}`};
                                }
                            }
                        }
                    } catch (e) {
                        console.log('Angular 확인 실패:', e);
                    }
                }

                // DOM 기반 확인
                const seatContainer = document.querySelector('.scrollbar-vista.seat');
                if (seatContainer) {
                    const seatItems = seatContainer.querySelectorAll('li');
                    for (const item of seatItems) {
                        const text = item.textContent || item.innerText || '';
                        if (text && text.length > 8 && (text.includes('블록') || text.includes('열') || text.includes('번'))) {
                            return {success: true, seatInfo: text.trim()};
                        }
                    }
                }

                return {success: false};
            }

            // Canvas 좌석 데이터 로딩 대기 함수
            async function waitForCanvasSeats(canvas) {
                return new Promise((resolve) => {
                    let attempts = 0;
                    const maxAttempts = 20; // 2초간 대기

                    function checkCanvasReady() {
                        attempts++;

                        // Canvas 컨텍스트 확인
                        try {
                            const ctx = canvas.getContext('2d');
                            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                            let hasContent = false;

                            // 투명하지 않은 픽셀이 있는지 확인
                            for (let i = 3; i < imageData.data.length; i += 4) {
                                if (imageData.data[i] > 0) { // alpha 값이 0보다 크면
                                    hasContent = true;
                                    break;
                                }
                            }

                            if (hasContent) {
                                console.log('✅ Canvas에 좌석 데이터 로딩 완료');
                                resolve(true);
                                return;
                            }
                        } catch (e) {
                            console.log('Canvas 데이터 확인 중 오류:', e);
                        }

                        if (attempts >= maxAttempts) {
                            console.log('Canvas 좌석 데이터 로딩 대기 시간 초과');
                            resolve(false);
                        } else {
                            setTimeout(checkCanvasReady, 100);
                        }
                    }

                    checkCanvasReady();
                });
            }

            // Canvas에 좌석 데이터가 있는지 확인하고 빈 좌석 개수를 분석하는 함수
            function checkCanvasHasSeats(canvas) {
                try {
                    const ctx = canvas.getContext('2d');
                    const rect = canvas.getBoundingClientRect();

                    if (rect.width === 0 || rect.height === 0) {
                        console.log('❌ Canvas 크기가 0');
                        return false;
                    }

                    console.log(`Canvas 분석 시작: ${rect.width}x${rect.height}`);

                    // 전체 Canvas 이미지 데이터 분석
                    const imageData = ctx.getImageData(0, 0, rect.width, rect.height);

                    let totalPixels = 0;
                    let transparentPixels = 0;
                    let whitePixels = 0;
                    let coloredPixels = 0;
                    let availableSeatsEstimate = 0;

                    // 좌석 색상 패턴 (일반적인 좌석 색상들)
                    const seatColors = {
                        available: 0, // 초록색 계열 (예매 가능)
                        occupied: 0,  // 빨간색 계열 (예매 완료)
                        selected: 0,  // 파란색 계열 (선택됨)
                        disabled: 0   // 회색 계열 (선택 불가)
                    };

                    for (let i = 0; i < imageData.data.length; i += 4) {
                        const r = imageData.data[i];
                        const g = imageData.data[i + 1];
                        const b = imageData.data[i + 2];
                        const a = imageData.data[i + 3];

                        totalPixels++;

                        if (a === 0) {
                            transparentPixels++;
                        } else if (r > 240 && g > 240 && b > 240) {
                            whitePixels++;
                        } else {
                            coloredPixels++;

                            // 좌석 색상 분류 (대략적)
                            if (g > r && g > b && g > 100) {
                                // 초록색 계열 - 예매 가능 좌석
                                seatColors.available++;
                                availableSeatsEstimate++;
                            } else if (r > g && r > b && r > 100) {
                                // 빨간색 계열 - 예매 완료 좌석
                                seatColors.occupied++;
                            } else if (b > r && b > g && b > 100) {
                                // 파란색 계열 - 선택된 좌석
                                seatColors.selected++;
                            } else if (r > 50 && g > 50 && b > 50 &&
                                     Math.abs(r - g) < 30 && Math.abs(g - b) < 30) {
                                // 회색 계열 - 선택 불가
                                seatColors.disabled++;
                            }
                        }
                    }

                    console.log('=== Canvas 좌석 분석 결과 ===');
                    console.log(`총 픽셀: ${totalPixels.toLocaleString()}`);
                    console.log(`투명 픽셀: ${transparentPixels.toLocaleString()}`);
                    console.log(`흰색 픽셀: ${whitePixels.toLocaleString()}`);
                    console.log(`컬러 픽셀: ${coloredPixels.toLocaleString()}`);
                    console.log('--- 좌석 색상 분석 ---');
                    console.log(`🟢 예매 가능 (초록): ${seatColors.available.toLocaleString()}개`);
                    console.log(`🔴 예매 완료 (빨강): ${seatColors.occupied.toLocaleString()}개`);
                    console.log(`🔵 선택됨 (파랑): ${seatColors.selected.toLocaleString()}개`);
                    console.log(`⚫ 선택 불가 (회색): ${seatColors.disabled.toLocaleString()}개`);
                    console.log(`🎯 예상 빈 좌석 수: ${availableSeatsEstimate.toLocaleString()}개`);

                    // 좌석 데이터가 있는지 판단
                    const hasSeats = coloredPixels > 1000; // 1000개 이상의 컬러 픽셀이 있으면 좌석 데이터 존재
                    console.log(`좌석 데이터 존재 여부: ${hasSeats}`);

                    return hasSeats;
                } catch (e) {
                    console.log('Canvas 좌석 분석 실패:', e);
                    return true; // 오류 시 일단 진행
                }
            }

            // 기존 Canvas 좌석 선택 함수 (호환성 유지)
            function tryCanvasSeatSelection() {
                console.log('=== Canvas 좌석 선택 시작 ===');

                // Canvas 요소들 찾기
                const canvases = document.querySelectorAll('#main_view canvas');
                console.log('발견된 Canvas 개수:', canvases.length);

                if (canvases.length === 0) {
                    console.log('❌ Canvas를 찾을 수 없음');
                    return false;
                }

                // 가장 위에 있는 Canvas 선택 (보통 마지막 Canvas가 클릭 가능한 좌석 레이어)
                let targetCanvas = null;
                let maxZIndex = -1;

                for (const canvas of canvases) {
                    const style = window.getComputedStyle(canvas);
                    const zIndex = parseInt(style.zIndex) || 0;
                    const display = style.display;

                    if (display !== 'none' && zIndex >= maxZIndex) {
                        maxZIndex = zIndex;
                        targetCanvas = canvas;
                    }
                }

                if (!targetCanvas) {
                    console.log('❌ 클릭 가능한 Canvas를 찾을 수 없음');
                    return false;
                }

                console.log('선택된 Canvas z-index:', maxZIndex);
                const rect = targetCanvas.getBoundingClientRect();
                console.log('Canvas 크기:', rect.width, 'x', rect.height);

                // 좌석 선택 전략: 경기장/무대에 가까운 곳 우선
                // Canvas의 위쪽과 중앙 부분을 우선적으로 클릭
                const preferredAreas = [
                    // 1순위: 상단 중앙 (무대/경기장에 가장 가까울 가능성)
                    { x: 0.4, y: 0.15, width: 0.2, height: 0.1 },
                    { x: 0.45, y: 0.2, width: 0.1, height: 0.1 },

                    // 2순위: 상단 좌우
                    { x: 0.25, y: 0.15, width: 0.15, height: 0.15 },
                    { x: 0.6, y: 0.15, width: 0.15, height: 0.15 },

                    // 3순위: 중앙 부분
                    { x: 0.3, y: 0.3, width: 0.4, height: 0.2 },

                    // 4순위: 넓은 범위
                    { x: 0.2, y: 0.2, width: 0.6, height: 0.4 }
                ];

                let seatClicked = false;

                for (let areaIndex = 0; areaIndex < preferredAreas.length && !seatClicked; areaIndex++) {
                    const area = preferredAreas[areaIndex];
                    console.log(`우선순위 ${areaIndex + 1} 영역에서 좌석 클릭 시도`);

                    // 각 영역에서 여러 번 클릭 시도
                    for (let attempt = 0; attempt < 8 && !seatClicked; attempt++) {
                        // 영역 내에서 랜덤 위치 선택
                        const randomX = area.x + (Math.random() * area.width);
                        const randomY = area.y + (Math.random() * area.height);

                        const clickX = rect.left + (randomX * rect.width);
                        const clickY = rect.top + (randomY * rect.height);

                        console.log(`클릭 시도 ${attempt + 1}: (${Math.round(clickX)}, ${Math.round(clickY)})`);

                        // Canvas 클릭 이벤트 생성
                        const clickEvent = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            clientX: clickX,
                            clientY: clickY,
                            button: 0,
                            buttons: 1
                        });

                        targetCanvas.dispatchEvent(clickEvent);

                        // 클릭 후 즉시 확인 및 더 많은 대기 시간
                        setTimeout(() => {
                            const selectedSeat = checkSeatSelection();
                            if (selectedSeat.success) {
                                console.log('✅ 좌석 선택 성공:', selectedSeat.seatInfo);
                                seatClicked = true;
                                return true;
                            }
                        }, 500);

                        // 추가로 더 강력한 클릭 이벤트 발생
                        const mouseDown = new MouseEvent('mousedown', {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            clientX: clickX,
                            clientY: clickY,
                            button: 0
                        });

                        const mouseUp = new MouseEvent('mouseup', {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            clientX: clickX,
                            clientY: clickY,
                            button: 0
                        });

                        targetCanvas.dispatchEvent(mouseDown);
                        setTimeout(() => {
                            targetCanvas.dispatchEvent(mouseUp);
                        }, 50);
                    }

                    // 각 영역 시도 후 잠시 대기
                    if (!seatClicked) {
                        console.log(`우선순위 ${areaIndex + 1} 영역에서 좌석 선택 실패, 다음 영역 시도`);
                        setTimeout(() => {}, 300);
                    }
                }

                if (!seatClicked) {
                    console.log('❌ 모든 영역에서 좌석 선택 실패');
                    return false;
                }

                return true;
            }

            // 좌석 선택 확인 함수 (Canvas용)
            function checkSeatSelection() {
                // 1. 좌석 컨테이너 표시 상태 확인
                const seatContainer = document.querySelector('.scrollbar-vista.seat');
                if (seatContainer) {
                    const containerStyle = window.getComputedStyle(seatContainer);
                    if (containerStyle.display !== 'none') {
                        const seatItems = seatContainer.querySelectorAll('ul.lst li');
                        if (seatItems.length > 0) {
                            const seatText = seatItems[0].textContent || seatItems[0].innerText || '';
                            if (seatText && seatText.trim().length > 5) {
                                return {success: true, seatInfo: seatText.trim()};
                            }
                        }
                    }
                }

                // 2. Angular 상태 확인
                if (typeof angular !== 'undefined') {
                    try {
                        const angularElements = document.querySelectorAll('[ng-controller], [ng-app]');
                        for (const element of angularElements) {
                            const scope = angular.element(element).scope();
                            if (scope && scope.selected && scope.selected.selectedSeatsAndZones) {
                                if (scope.selected.selectedSeatsAndZones.length > 0) {
                                    return {success: true, seatInfo: 'Angular에서 좌석 선택됨'};
                                }
                            }
                        }
                    } catch (e) {
                        // Angular 확인 실패는 무시
                    }
                }

                return {success: false};
            }
        }
        """

        # 각 함수는 호출 시점에 직접 정의하여 실행

        success_count = 0
        fail_count = 0
        attempt = 0

        while True:
            attempt += 1

            # 유한 모드에서 최대 시도 횟수 체크
            if max_attempts != float('inf') and attempt > max_attempts:
                break

            try:
                result_log.append(f"⚡ {attempt}번째 시도 - 페이지 상태 확인 중...")

                # 1. 페이지 상태 디버깅 정보 수집
                debug_info = self.driver.execute_script("""
                return {
                    url: window.location.href,
                    title: document.title,
                    hasGradeList: !!document.querySelector('#select_seat_grade'),
                    hasZoneList: !!document.querySelector('ul.seat_zone'),
                    hasCanvas: document.querySelectorAll('canvas').length,
                    selectedSeat: !!document.querySelector('.scrollbar-vista.seat ul.lst')
                };
                """)

                result_log.append(f"📊 페이지 상태: {debug_info}")

                # GUI 실시간 로그와 창 제목 업데이트
                try:
                    # GUI 로그에 진행 상황 표시
                    if hasattr(self, 'gui_instance') and self.gui_instance:
                        self.gui_instance.add_log(f"⚡ {attempt}번째 시도 - {debug_info.get('title', 'Unknown')}")
                        self.gui_instance.add_log(f"📊 페이지 요소: 등급목록={debug_info.get('hasGradeList')}, 구역목록={debug_info.get('hasZoneList')}, Canvas={debug_info.get('hasCanvas')}개")

                    # 창 제목 업데이트
                    status_title = f"🚀 완전 자동 예매 - {attempt}번째 시도 (성공:{success_count} 실패:{fail_count})"
                    root.title(status_title)
                    root.update()  # GUI 업데이트
                except:
                    pass

                # 2. 블록 로딩 재확인 후 선택
                result_log.append("🎯 블록 가용성 재확인 중...")
                if hasattr(self, 'gui_instance') and self.gui_instance:
                    self.gui_instance.add_log("🎯 블록 가용성 재확인 중...")

                # 블록 로딩 재확인 - 더 빠른 확인 주기
                recheck_script = """
                const zoneLists = document.querySelectorAll('ul.seat_zone');
                return {
                    hasBlocks: zoneLists.length > 0,
                    zoneCount: zoneLists.length,
                    totalBlocks: Array.from(zoneLists).reduce((sum, list) =>
                        sum + list.querySelectorAll('li[id^="seat_zone_"] a[href="#"]').length, 0)
                };
                """

                block_recheck = self.driver.execute_script(recheck_script)
                result_log.append(f"🔍 재확인 결과: 블록 리스트 {block_recheck['zoneCount']}개, 클릭 가능한 블록 {block_recheck['totalBlocks']}개")

                if hasattr(self, 'gui_instance') and self.gui_instance:
                    self.gui_instance.add_log(f"🔍 재확인 결과: 클릭 가능한 블록 {block_recheck['totalBlocks']}개")

                if block_recheck['totalBlocks'] == 0:
                    result_log.append("❌ 클릭 가능한 블록이 없음 - 다음 시도로 넘어감")
                    if hasattr(self, 'gui_instance') and self.gui_instance:
                        self.gui_instance.add_log("❌ 클릭 가능한 블록이 없음")
                    fail_count += 1
                    time.sleep(interval)
                    continue

                # 3. 블록 및 좌석 선택 시도
                result_log.append("🚀 블록 및 좌석 선택 시작!")
                if hasattr(self, 'gui_instance') and self.gui_instance:
                    self.gui_instance.add_log("🚀 블록 및 좌석 선택 시작!")

                # JavaScript 실행과 콘솔 로그 수집
                try:
                    # 콘솔 로그 수집을 위한 JavaScript 수정
                    detailed_block_script = """
                    let logMessages = [];
                    const originalLog = console.log;
                    console.log = function(...args) {
                        logMessages.push(args.join(' '));
                        originalLog.apply(console, args);
                    };

                    const result = selectAvailableBlockAndSeat();

                    // 콘솔 복원
                    console.log = originalLog;

                    return {
                        ...result,
                        logs: logMessages
                    };
                    """

                    # 함수를 직접 실행
                    full_block_script = f"""
                    {seat_click_script}
                    return selectAvailableBlockAndSeat();
                    """

                    block_result = self.driver.execute_script(full_block_script)

                    # 블록 클릭 결과를 GUI에 표시
                    if hasattr(self, 'gui_instance') and self.gui_instance:
                        if 'method' in block_result:
                            self.gui_instance.add_log(f"🎯 {block_result['message']}")
                        else:
                            self.gui_instance.add_log(f"🎯 블록 선택 결과: {block_result.get('message', '결과 없음')}")

                except Exception as e:
                    result_log.append(f"❌ JavaScript 실행 오류: {str(e)}")
                    if hasattr(self, 'gui_instance') and self.gui_instance:
                        self.gui_instance.add_log(f"❌ JavaScript 실행 오류: {str(e)}")
                    fail_count += 1
                    time.sleep(interval)
                    continue

                if block_result['success']:
                    result_log.append(block_result['message'])

                    # GUI 로그 업데이트
                    if hasattr(self, 'gui_instance') and self.gui_instance:
                        self.gui_instance.add_log(f"✅ {block_result['message']}")

                    # 블록 선택 후 좌석이 로딩될 때까지 동적 대기
                    seat_loading_wait = self.driver.execute_script("""
                    return new Promise((resolve) => {
                        let attempts = 0;
                        const maxAttempts = 15; // 1.5초간 대기

                        function checkSeatLoading() {
                            // 좌석 선택 관련 요소들이 업데이트되었는지 확인
                            const seatContainer = document.querySelector('.scrollbar-vista.seat');
                            const canvases = document.querySelectorAll('canvas');

                            let seatDataReady = false;

                            // Canvas가 업데이트되었는지 확인
                            if (canvases.length > 0) {
                                const canvas = canvases[canvases.length - 1];
                                try {
                                    const ctx = canvas.getContext('2d');
                                    const imageData = ctx.getImageData(0, 0, Math.min(50, canvas.width), Math.min(50, canvas.height));
                                    let hasPixels = false;

                                    for (let i = 3; i < imageData.data.length; i += 4) {
                                        if (imageData.data[i] > 0) {
                                            hasPixels = true;
                                            break;
                                        }
                                    }

                                    if (hasPixels) {
                                        seatDataReady = true;
                                    }
                                } catch(e) {
                                    // Canvas 확인 실패는 무시
                                }
                            }

                            if (seatDataReady) {
                                resolve({success: true, message: '좌석 데이터 로딩 완료'});
                                return;
                            }

                            attempts++;
                            if (attempts >= maxAttempts) {
                                resolve({success: true, message: '좌석 로딩 대기 시간 완료 (강제 진행)'});
                            } else {
                                setTimeout(checkSeatLoading, 100);
                            }
                        }

                        checkSeatLoading();
                    });
                    """)

                    if hasattr(self, 'gui_instance') and self.gui_instance:
                        self.gui_instance.add_log(f"🔍 {seat_loading_wait.get('message', '좌석 로딩 대기 완료')}")

                    # Alert 확인
                    try:
                        alert = self.driver.switch_to.alert
                        alert_text = alert.text
                        alert.accept()

                        if any(word in alert_text for word in ['선점', '이미', '매진', '불가', '선택된']):
                            result_log.append(f"❌ Alert: {alert_text}")
                            fail_count += 1
                            if hasattr(self, 'gui_instance') and self.gui_instance:
                                self.gui_instance.add_log(f"❌ Alert: {alert_text}")
                        else:
                            result_log.append(f"✅ Alert: {alert_text}")
                            if hasattr(self, 'gui_instance') and self.gui_instance:
                                self.gui_instance.add_log(f"✅ Alert: {alert_text}")

                    except:
                        # Alert 없음 - 좌석 선택 확인
                        seat_check_script = """
                        function checkSeatSelection() {
                            console.log('=== 좌석 선택 확인 시작 ===');

                            // 1. 좌석 컨테이너 및 내용 확인 (display 상태와 관계없이)
                            const seatContainer = document.querySelector('.scrollbar-vista.seat');
                            console.log('좌석 컨테이너:', seatContainer);

                            if (seatContainer) {
                                const containerStyle = window.getComputedStyle(seatContainer);
                                console.log('좌석 컨테이너 display:', containerStyle.display);

                                // display 상태와 관계없이 실제 좌석 데이터가 있는지 확인
                                const seatItems = seatContainer.querySelectorAll('ul.lst li[ng-repeat*="seat"]');
                                console.log('발견된 좌석 항목 수:', seatItems.length);

                                // ng-repeat로 생성된 좌석 항목이 있으면 선택된 것
                                if (seatItems.length > 0) {
                                    for (const seatItem of seatItems) {
                                        const seatText = seatItem.textContent || seatItem.innerText || '';
                                        console.log('좌석 텍스트:', seatText);

                                        if (seatText && seatText.trim().length > 5) {
                                            console.log('✅ 좌석 선택 감지 (display 무관):', seatText.trim());
                                            return {success: true, seatInfo: seatText.trim()};
                                        }
                                    }
                                }

                                // ng-repeat 없이도 텍스트로 확인
                                const allSeatItems = seatContainer.querySelectorAll('ul.lst li');
                                for (const item of allSeatItems) {
                                    const text = item.textContent || item.innerText || '';
                                    if (text && text.trim().length > 8) {
                                        if (text.includes('블록') || text.includes('열') || text.includes('번')) {
                                            console.log('✅ 일반 좌석 텍스트로 선택 감지:', text.trim());
                                            return {success: true, seatInfo: text.trim()};
                                        }
                                    }
                                }
                            }

                            // 2. Angular 기반 선택 상태 확인 + showSelectedSeatInfo 강제 활성화
                            if (typeof angular !== 'undefined') {
                                try {
                                    // 모든 Angular 스코프에서 좌석 정보 찾기
                                    const angularElements = document.querySelectorAll('[ng-controller], [ng-app], body');
                                    for (const element of angularElements) {
                                        try {
                                            const scope = angular.element(element).scope();
                                            if (scope) {
                                                // showSelectedSeatInfo 강제 활성화 시도
                                                if (typeof scope.showSelectedSeatInfo !== 'undefined') {
                                                    console.log('showSelectedSeatInfo 발견, 강제 활성화 시도');
                                                    scope.showSelectedSeatInfo = true;
                                                    scope.$apply();
                                                }

                                                // 선택된 좌석 확인
                                                if (scope.selected && scope.selected.selectedSeatsAndZones) {
                                                    const selectedSeats = scope.selected.selectedSeatsAndZones;
                                                    console.log('Angular 선택된 좌석 수:', selectedSeats.length);
                                                    if (selectedSeats.length > 0) {
                                                        const seatInfo = selectedSeats[0].seatName || selectedSeats[0].name || JSON.stringify(selectedSeats[0]);
                                                        console.log('✅ Angular로 좌석 선택 감지:', seatInfo);

                                                        // 좌석이 선택되었으므로 정보 표시 활성화
                                                        if (typeof scope.showSelectedSeatInfo !== 'undefined') {
                                                            scope.showSelectedSeatInfo = true;
                                                            scope.$apply();
                                                        }

                                                        return {success: true, seatInfo: seatInfo};
                                                    }
                                                }

                                                // $parent 스코프도 확인
                                                if (scope.$parent && scope.$parent.selected && scope.$parent.selected.selectedSeatsAndZones) {
                                                    const selectedSeats = scope.$parent.selected.selectedSeatsAndZones;
                                                    if (selectedSeats.length > 0) {
                                                        const seatInfo = selectedSeats[0].seatName || selectedSeats[0].name || 'Parent Scope 좌석';
                                                        console.log('✅ Parent Angular 스코프에서 좌석 선택 감지:', seatInfo);
                                                        return {success: true, seatInfo: seatInfo};
                                                    }
                                                }
                                            }
                                        } catch (e) {
                                            // 개별 스코프 확인 실패는 무시하고 다음으로
                                            continue;
                                        }
                                    }
                                } catch (e) {
                                    console.log('Angular 전체 확인 중 오류:', e);
                                }
                            }

                            // 3. 다른 가능한 좌석 선택 표시 요소들
                            const alternativeSelectors = [
                                '.select_seat_info strong:contains("선택")',
                                '[class*="selected"] li',
                                '.seat_header strong',
                                '.seat_lst li.selected',
                                '[data-seat-info]'
                            ];

                            for (const selector of alternativeSelectors) {
                                try {
                                    const element = document.querySelector(selector.replace(':contains("선택")', ''));
                                    if (element) {
                                        const text = element.textContent || element.innerText || '';
                                        console.log('대체 확인 - ' + selector + ':', text);
                                        // 실제 좌석 정보가 아닌 안내 메시지 제외
                                        if (text && text.length > 3 &&
                                            !text.includes('선택해 주세요') &&
                                            !text.includes('선택하세요') &&
                                            !text.includes('을 선택') &&
                                            !text.includes('를 선택') &&
                                            (text.includes('좌석') || text.includes('블록') || text.includes('열') || text.includes('번'))) {
                                            // 추가로 실제 좌석 정보인지 확인 (좌석 번호 패턴)
                                            if (text.match(/\d+열/) || text.match(/\d+번/) || text.match(/\d+블록/) || text.includes('석')) {
                                                console.log('✅ 대체 방법으로 좌석 선택 감지:', text.trim());
                                                return {success: true, seatInfo: text.trim()};
                                            }
                                        }
                                    }
                                } catch (e) {
                                    console.log('대체 확인 중 오류:', e);
                                }
                            }

                            // 모든 좌석 선택 감지 실패 전에 Canvas 좌석 개수 분석 수행
                            console.log('=== Canvas 좌석 개수 분석 시작 ===');

                            // 1단계: 등급별 빈 좌석 색깔 추출
                            function extractGradeColors() {
                                const gradeColors = [];

                                // 등급 리스트에서 색깔 정보 추출
                                const gradeElements = document.querySelectorAll('#select_seat_grade li[id^="seat_grade_"], ul#select_seat_grade li');
                                console.log(`등급 요소 발견 수: ${gradeElements.length}`);

                                for (let i = 0; i < gradeElements.length; i++) {
                                    const gradeElement = gradeElements[i];
                                    const gradeText = gradeElement.textContent || gradeElement.innerText || '';

                                    // 색깔 표시 요소 찾기 (span, div, i 등에서 배경색이나 색깔 정보)
                                    const colorIndicators = gradeElement.querySelectorAll('span, div, i, em, strong');

                                    for (const indicator of colorIndicators) {
                                        const style = window.getComputedStyle(indicator);
                                        const bgColor = style.backgroundColor;
                                        const color = style.color;
                                        const borderColor = style.borderColor;

                                        // RGB 값이 있는 색깔만 추출
                                        if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                                            const rgbMatch = bgColor.match(/rgb\\(?(\\d+),\\s*(\\d+),\\s*(\\d+)\\)?/);
                                            if (rgbMatch) {
                                                const r = parseInt(rgbMatch[1]);
                                                const g = parseInt(rgbMatch[2]);
                                                const b = parseInt(rgbMatch[3]);
                                                gradeColors.push({
                                                    grade: gradeText.trim(),
                                                    r: r, g: g, b: b,
                                                    colorType: 'background',
                                                    colorValue: bgColor
                                                });
                                                console.log(`등급 "${gradeText.trim()}" 배경색: RGB(${r}, ${g}, ${b})`);
                                            }
                                        }

                                        if (color && color !== 'rgba(0, 0, 0, 0)' && color !== 'transparent') {
                                            const rgbMatch = color.match(/rgb\\(?(\\d+),\\s*(\\d+),\\s*(\\d+)\\)?/);
                                            if (rgbMatch) {
                                                const r = parseInt(rgbMatch[1]);
                                                const g = parseInt(rgbMatch[2]);
                                                const b = parseInt(rgbMatch[3]);
                                                gradeColors.push({
                                                    grade: gradeText.trim(),
                                                    r: r, g: g, b: b,
                                                    colorType: 'text',
                                                    colorValue: color
                                                });
                                                console.log(`등급 "${gradeText.trim()}" 텍스트색: RGB(${r}, ${g}, ${b})`);
                                            }
                                        }
                                    }
                                }

                                return gradeColors;
                            }

                            // 2단계: Canvas에서 추출된 색깔 기준으로 좌석 분석
                            function analyzeCanvasWithGradeColors(canvas, gradeColors) {
                                try {
                                    const ctx = canvas.getContext('2d');
                                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                                    const data = imageData.data;

                                    let totalPixels = 0;
                                    let colorMatchCounts = {};
                                    let unknownColors = {};

                                    // 등급별 색깔 매칭을 위한 초기화
                                    gradeColors.forEach(gradeColor => {
                                        const colorKey = `${gradeColor.r},${gradeColor.g},${gradeColor.b}`;
                                        colorMatchCounts[colorKey] = {
                                            count: 0,
                                            grade: gradeColor.grade,
                                            colorType: gradeColor.colorType
                                        };
                                    });

                                    // 픽셀별 분석
                                    for (let j = 0; j < data.length; j += 4) {
                                        const r = data[j];
                                        const g = data[j + 1];
                                        const b = data[j + 2];
                                        const a = data[j + 3];

                                        if (a > 0 && !(r > 240 && g > 240 && b > 240)) {
                                            totalPixels++;

                                            // 등급 색깔과 매칭 (허용 오차 ±10)
                                            let matched = false;
                                            for (const gradeColor of gradeColors) {
                                                if (Math.abs(r - gradeColor.r) <= 10 &&
                                                    Math.abs(g - gradeColor.g) <= 10 &&
                                                    Math.abs(b - gradeColor.b) <= 10) {
                                                    const colorKey = `${gradeColor.r},${gradeColor.g},${gradeColor.b}`;
                                                    colorMatchCounts[colorKey].count++;
                                                    matched = true;
                                                    break;
                                                }
                                            }

                                            // 매칭되지 않은 색깔 추적
                                            if (!matched) {
                                                const colorKey = `${r},${g},${b}`;
                                                unknownColors[colorKey] = (unknownColors[colorKey] || 0) + 1;
                                            }
                                        }
                                    }

                                    // 결과 출력
                                    console.log(`\\n📊 Canvas 분석 결과 (${canvas.width}x${canvas.height}):`);
                                    console.log(`총 컬러 픽셀: ${totalPixels.toLocaleString()}개`);

                                    console.log('\\n🎨 등급별 좌석 색깔 매칭:');
                                    let totalAvailableSeats = 0;
                                    for (const [colorKey, info] of Object.entries(colorMatchCounts)) {
                                        if (info.count > 0) {
                                            console.log(`${info.grade} (RGB ${colorKey}): ${info.count.toLocaleString()}개`);
                                            totalAvailableSeats += info.count;
                                        }
                                    }

                                    console.log('\\n🔍 알 수 없는 색깔 (상위 10개):');
                                    const sortedUnknown = Object.entries(unknownColors)
                                        .sort(([,a], [,b]) => b - a)
                                        .slice(0, 10);

                                    for (const [colorKey, count] of sortedUnknown) {
                                        console.log(`RGB ${colorKey}: ${count.toLocaleString()}개`);
                                    }

                                    console.log(`\\n🎯 총 예상 빈 좌석 수: ${totalAvailableSeats.toLocaleString()}개`);

                                    return totalAvailableSeats;

                                } catch (e) {
                                    console.log('Canvas 분석 중 오류:', e);
                                    return 0;
                                }
                            }

                            // 실행
                            const gradeColors = extractGradeColors();
                            console.log(`추출된 등급 색깔 수: ${gradeColors.length}개`);

                            const canvases = document.querySelectorAll('canvas');
                            console.log(`발견된 Canvas 수: ${canvases.length}`);

                            let totalAnalyzedSeats = 0;
                            for (let i = 0; i < canvases.length; i++) {
                                const canvas = canvases[i];
                                if (canvas.offsetParent !== null && canvas.width > 0 && canvas.height > 0) {
                                    console.log(`\\nCanvas ${i+1} 분석 시작...`);
                                    const seatCount = analyzeCanvasWithGradeColors(canvas, gradeColors);
                                    totalAnalyzedSeats += seatCount;
                                } else {
                                    console.log(`Canvas ${i+1}은 숨겨져 있거나 크기가 0`);
                                }
                            }

                            if (totalAnalyzedSeats > 0) {
                                console.log(`\\n🏆 전체 Canvas에서 발견된 총 빈 좌석: ${totalAnalyzedSeats.toLocaleString()}개`);
                            }

                            console.log('❌ 모든 방법으로 좌석 선택 감지 실패');
                            return {success: false};
                        }
                        return checkSeatSelection();
                        """

                        seat_check = self.driver.execute_script(seat_check_script)

                        if seat_check['success']:
                            success_count += 1
                            result_log.append(f"🎉 좌석 선택 성공! - {seat_check['seatInfo']}")

                            if hasattr(self, 'gui_instance') and self.gui_instance:
                                self.gui_instance.add_log(f"🎉 좌석 선택 성공! - {seat_check['seatInfo']}")

                            # 🚀 자동으로 다음 단계 진행
                            result_log.append("🚀 자동으로 다음 단계 진행 중...")
                            if hasattr(self, 'gui_instance') and self.gui_instance:
                                self.gui_instance.add_log("🚀 자동으로 다음 단계 진행 중...")

                            # 다음 버튼이 클릭 가능할 때까지 동적 대기
                            next_button_wait = self.driver.execute_script("""
                            return new Promise((resolve) => {
                                let attempts = 0;
                                function checkNextButton() {
                                    attempts++;
                                    const nextSelectors = [
                                        '//button[contains(text(), "다음")]',
                                        '//button[contains(text(), "확인")]',
                                        '//input[@type="button" and contains(@value, "다음")]'
                                    ];

                                    for (let selector of nextSelectors) {
                                        const button = document.evaluate(selector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                        if (button && button.offsetParent !== null && !button.disabled) {
                                            resolve({success: true, message: `다음 버튼 발견 (${attempts}번째 시도)`, selector: selector});
                                            return;
                                        }
                                    }

                                    if (attempts < 20) { // 최대 10초 대기 (500ms * 20)
                                        setTimeout(checkNextButton, 500);
                                    } else {
                                        resolve({success: false, message: '다음 버튼을 찾을 수 없음'});
                                    }
                                }
                                checkNextButton();
                            });
                            """)

                            if next_button_wait['success']:
                                result_log.append(f"✅ {next_button_wait['message']}")
                                if hasattr(self, 'gui_instance') and self.gui_instance:
                                    self.gui_instance.add_log(f"✅ {next_button_wait['message']}")

                            next_button_script = """
                            function clickNextButton() {
                                // 다음 단계 버튼 찾기
                                const nextSelectors = [
                                    '//button[contains(text(), "다음")]',
                                    '//button[contains(text(), "확인")]',
                                    '//button[contains(text(), "선택완료")]',
                                    '//input[@value="다음"]',
                                    '//a[contains(text(), "다음")]'
                                ];

                                for (const xpath of nextSelectors) {
                                    try {
                                        const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                                        if (result.singleNodeValue && result.singleNodeValue.offsetParent !== null) {
                                            result.singleNodeValue.click();
                                            return '➡️ 다음 단계 버튼 클릭';
                                        }
                                    } catch(e) {
                                        continue;
                                    }
                                }

                                return '⚠️ 다음 버튼 없음';
                            }
                            return clickNextButton();
                            """

                            next_result = self.driver.execute_script(next_button_script)
                            result_log.append(next_result)

                            if "다음 단계" in next_result:
                                result_log.append("✅ 완전 자동 예매 완료!")
                                result_log.append(f"🎯 최종 선택 좌석: {seat_check['seatInfo']}")
                                result_log.append("➡️ 이제 결제 페이지로 이동합니다")

                                if hasattr(self, 'gui_instance') and self.gui_instance:
                                    self.gui_instance.add_log("✅ 완전 자동 예매 완료!")
                                    self.gui_instance.add_log(f"🎯 최종 선택 좌석: {seat_check['seatInfo']}")
                                    self.gui_instance.add_log("➡️ 이제 결제 페이지로 이동합니다")

                                break  # 성공 시 루프 종료

                            break  # 좌석 선택 성공 시 루프 종료
                        else:
                            result_log.append("❓ 좌석 선택 상태 확인 중...")
                            # 좌석 선택 상태가 업데이트될 때까지 동적 대기
                            seat_check2 = self.driver.execute_script("""
                            return new Promise((resolve) => {
                                let attempts = 0;
                                function checkSeatStatus() {
                                    attempts++;

                                    // 좌석 선택 확인 로직 (기존 seat_check_script와 동일)
                                    let selectedSeats = [];

                                    // 캔버스에서 선택된 좌석 정보 확인
                                    const canvases = document.querySelectorAll('canvas');
                                    for (let canvas of canvases) {
                                        if (canvas.offsetParent !== null && canvas.width > 0 && canvas.height > 0) {
                                            const ctx = canvas.getContext('2d');
                                            const rect = canvas.getBoundingClientRect();

                                            try {
                                                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                                                const data = imageData.data;
                                                let hasSelectedPixels = false;

                                                for (let i = 0; i < data.length; i += 4) {
                                                    const r = data[i];
                                                    const g = data[i + 1];
                                                    const b = data[i + 2];

                                                    // 선택된 좌석 색상 확인 (파란색 계열)
                                                    if (b > 150 && r < 100 && g < 100) {
                                                        hasSelectedPixels = true;
                                                        break;
                                                    }
                                                }

                                                if (hasSelectedPixels) {
                                                    selectedSeats.push("Canvas 좌석 선택됨");
                                                    resolve({success: true, selectedSeats: selectedSeats, seatInfo: `Canvas에서 좌석 선택 확인 (${attempts}번째 시도)`});
                                                    return;
                                                }
                                            } catch (e) {
                                                console.log('Canvas 분석 중 오류:', e);
                                            }
                                        }
                                    }

                                    if (attempts < 10) { // 최대 5초 대기 (500ms * 10)
                                        setTimeout(checkSeatStatus, 500);
                                    } else {
                                        resolve({success: false, selectedSeats: [], seatInfo: '좌석 선택 상태를 확인할 수 없음'});
                                    }
                                }
                                checkSeatStatus();
                            });
                            """)
                            if seat_check2['success']:
                                success_count += 1
                                result_log.append(f"🎉 지연 확인으로 좌석 선택 성공! - {seat_check2['seatInfo']}")

                                # 🚀 자동으로 다음 단계 진행
                                result_log.append("🚀 자동으로 다음 단계 진행 중...")
                                # 다음 버튼이 클릭 가능할 때까지 동적 대기
                                next_button_wait = self.driver.execute_script("""
                                return new Promise((resolve) => {
                                    let attempts = 0;
                                    function checkNextButton() {
                                        attempts++;
                                        const nextSelectors = [
                                            '//button[contains(text(), "다음")]',
                                            '//button[contains(text(), "확인")]',
                                            '//input[@type="button" and contains(@value, "다음")]'
                                        ];

                                        for (let selector of nextSelectors) {
                                            const button = document.evaluate(selector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                            if (button && button.offsetParent !== null && !button.disabled) {
                                                resolve({success: true, message: `다음 버튼 발견 (${attempts}번째 시도)`, selector: selector});
                                                return;
                                            }
                                        }

                                        if (attempts < 20) { // 최대 10초 대기 (500ms * 20)
                                            setTimeout(checkNextButton, 500);
                                        } else {
                                            resolve({success: false, message: '다음 버튼을 찾을 수 없음'});
                                        }
                                    }
                                    checkNextButton();
                                });
                                """)

                                if next_button_wait['success']:
                                    result_log.append(f"✅ {next_button_wait['message']}")
                                    if hasattr(self, 'gui_instance') and self.gui_instance:
                                        self.gui_instance.add_log(f"✅ {next_button_wait['message']}")

                                next_button_script = """
                            function clickNextButton() {
                                // 다음 단계 버튼 찾기
                                const nextSelectors = [
                                    '//button[contains(text(), "다음")]',
                                    '//button[contains(text(), "확인")]',
                                    '//button[contains(text(), "선택완료")]',
                                    '//input[@value="다음"]',
                                    '//a[contains(text(), "다음")]'
                                ];

                                for (const xpath of nextSelectors) {
                                    try {
                                        const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                                        if (result.singleNodeValue && result.singleNodeValue.offsetParent !== null) {
                                            result.singleNodeValue.click();
                                            return '➡️ 다음 단계 버튼 클릭';
                                        }
                                    } catch(e) {
                                        continue;
                                    }
                                }

                                return '⚠️ 다음 버튼 없음';
                            }
                            return clickNextButton();
                            """

                            next_result = self.driver.execute_script(next_button_script)
                            result_log.append(next_result)

                            if "다음 단계" in next_result:
                                result_log.append("✅ 완전 자동 예매 완료!")
                                result_log.append(f"🎯 최종 선택 좌석: {seat_check2['seatInfo']}")
                                result_log.append("➡️ 이제 결제 페이지로 이동합니다")
                            break

                else:
                    result_log.append(f"❌ {block_result['message']}")
                    fail_count += 1

                time.sleep(interval)  # 극단적으로 빠른 간격

            except Exception as e:
                result_log.append(f"❌ 오류: {str(e)}")
                fail_count += 1
                time.sleep(interval)

        # 초고속 결과 표시
        end_time = time.time()
        total_time = end_time - start_time

        result_log.append("-" * 40)
        result_log.append(f"⚡ 초고속 JavaScript 예매 완료")
        result_log.append(f"✅ 성공: {success_count}회")
        result_log.append(f"❌ 실패: {fail_count}회")
        result_log.append(f"⏱️ 총 소요시간: {total_time:.2f}초")
        result_log.append(f"🚀 평균 속도: {max_attempts/total_time:.1f}회/초")

        if success_count > 0:
            result_log.append("🎊 초고속 좌석 예매 성공!")
        else:
            result_log.append("😞 좌석 예매 실패 - 다시 시도해보세요")

        final_result = "\n".join(result_log)
        self.show_copyable_message("⚡ 초고속 예매 결과", final_result, root, 700, 600)

    def continuous_booking_attempt(self, root):
        """연속 예매 시도 기능"""
        # 구성 정보 입력
        seat_section = self.show_text_input_dialog("연속 예매 설정",
            "원하는 좌석 구역을 입력하세요.\n\n예시:\n- 응원특별석\n- 1루 K8\n- 메디힐테이블석",
            root)

        if not seat_section:
            return

        max_attempts = self.show_number_input_dialog("시도 횟수",
            "최대 몇 번 시도하시겠습니까?",
            root, minvalue=1, maxvalue=100, default=20)

        if not max_attempts:
            return

        interval = self.show_float_input_dialog("시도 간격",
            "각 시도 사이의 간격(초)을 입력하세요",
            root, minvalue=0.5, maxvalue=10.0, default=1.0)

        if not interval:
            return

        # 확인 메시지
        confirm_msg = f"연속 예매 시도를 시작합니다.\n\n"
        confirm_msg += f"🎯 좌석 구역: {seat_section}\n"
        confirm_msg += f"🔄 시도 횟수: {max_attempts}번\n"
        confirm_msg += f"⏱️ 시도 간격: {interval}초\n"
        confirm_msg += f"🔄 5번마다 페이지 새로고침\n\n"
        confirm_msg += f"계속하시겠습니까?"

        if not messagebox.askyesno("연속 예매 확인", confirm_msg, parent=root):
            return

        # 연속 시도 시작
        success_count = 0
        fail_count = 0
        start_time = time.time()

        result_log = []
        result_log.append(f"🚀 연속 예매 시도 시작")
        result_log.append(f"🎯 대상 구역: {seat_section}")
        result_log.append(f"📊 최대 시도: {max_attempts}번")
        result_log.append(f"⏱️ 간격: {interval}초")
        result_log.append(f"🕐 시작 시간: {time.strftime('%H:%M:%S')}")
        result_log.append("=" * 50)

        for attempt in range(1, max_attempts + 1):
            try:
                # 5번마다 페이지 새로고침
                if attempt % 5 == 1 and attempt > 1:
                    self.driver.refresh()
                    time.sleep(2)  # 페이지 로딩 대기
                    result_log.append(f"🔄 시도 {attempt}: 페이지 새로고침 완료")

                # 좌석 구역 선택 시도
                if self.select_seat_section(root, seat_section):
                    success_count += 1
                    result_log.append(f"✅ 시도 {attempt}: 성공! (총 성공: {success_count}회)")
                else:
                    fail_count += 1
                    result_log.append(f"❌ 시도 {attempt}: 실패 (총 실패: {fail_count}회)")

                # 진행률 표시
                progress = (attempt / max_attempts) * 100
                result_log.append(f"📊 진행률: {progress:.1f}% ({attempt}/{max_attempts})")

                # 마지막 시도가 아니면 대기
                if attempt < max_attempts:
                    time.sleep(interval)

            except Exception as e:
                fail_count += 1
                result_log.append(f"🔥 시도 {attempt}: 오류 발생 - {str(e)}")

        # 최종 결과
        end_time = time.time()
        total_time = end_time - start_time

        result_log.append("=" * 50)
        result_log.append(f"🏁 연속 예매 시도 완료")
        result_log.append(f"✅ 성공: {success_count}회")
        result_log.append(f"❌ 실패: {fail_count}회")
        result_log.append(f"📊 성공률: {(success_count/max_attempts)*100:.1f}%")
        result_log.append(f"⏰ 총 소요시간: {total_time:.1f}초")
        result_log.append(f"🕐 완료 시간: {time.strftime('%H:%M:%S')}")

        final_result = "\n".join(result_log)
        self.show_copyable_message("연속 예매 시도 결과", final_result, root, 800, 600)
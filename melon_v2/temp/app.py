from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import threading
import json
import os
import configparser
from datetime import datetime
import traceback
import queue
import time

# 기존 Macro 클래스를 import (파일명에 맞게 수정)
# from your_macro_file import Macro  # 실제 파일명으로 변경 필요

app = Flask(__name__)
app.config['SECRET_KEY'] = 'melon-ticket-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class MacroBridge:
    def __init__(self):
        self.macro_instance = None
        self.is_running = False
        self.is_paused = False
        self.current_part = "login"
        self.config = self.load_config()
        self.command_queue = queue.Queue()
        self.log_queue = queue.Queue()
        
    def load_config(self):
        """기본 설정 로드"""
        config = {
            'loginInfo': {'id': '', 'pw': ''},
            'bookInfo': {
                'prodId': '',
                'bookDate': '',
                'bookTime': '',
                'order': '',
                'grade': ''
            },
            'program': {
                'year': datetime.now().year,
                'month': datetime.now().month,
                'day': datetime.now().day,
                'hour': 14,
                'minute': 0
            },
            'function': {
                'auto_certification': 'Y',
                'special_area': 'N',
                'sound': 'Y',
                'seat_jump': 'N',
                'seat_jump_count': 0,
                'seat_jump_special_repeat': 'N',
                'seat_jump_special_repeat_count': 0,
                'skip_date_click': 'N'
            }
        }
        
        # config.ini 파일이 있으면 로드
        if os.path.exists('config.ini'):
            try:
                config_parser = configparser.ConfigParser()
                config_parser.read('config.ini', encoding='utf-8')
                
                for section in config_parser.sections():
                    if section in config:
                        for key, value in config_parser[section].items():
                            if key in config[section]:
                                # 숫자 변환 시도
                                try:
                                    config[section][key] = int(value)
                                except ValueError:
                                    config[section][key] = value
            except Exception as e:
                self.emit_log(f"Config 파일 로드 에러: {e}", "error")
        
        return config
    
    def save_config(self):
        """설정을 config.ini 파일로 저장"""
        try:
            config_parser = configparser.ConfigParser()
            
            for section, items in self.config.items():
                config_parser[section] = {}
                for key, value in items.items():
                    config_parser[section][key] = str(value)
            
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config_parser.write(configfile)
                
            self.emit_log("설정이 저장되었습니다.", "success")
        except Exception as e:
            self.emit_log(f"설정 저장 에러: {e}", "error")
    
    def emit_log(self, message, log_type="info"):
        """로그 메시지를 UI로 전송"""
        log_data = {
            'message': message,
            'type': log_type,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        socketio.emit('log_message', log_data)
        print(f"[{log_data['timestamp']}] {message}")
    
    def emit_status(self):
        """현재 상태를 UI로 전송"""
        status_data = {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_part': self.current_part,
            'config': self.config
        }
        socketio.emit('status_update', status_data)
    
    def start_macro(self):
        """매크로 시작"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.emit_log("매크로를 시작합니다.", "success")
            
            # 여기서 실제 Macro 클래스를 시작
            try:
                # self.macro_instance = Macro()  # 실제 Macro 클래스 인스턴스 생성
                # 실제 구현시에는 위 주석을 해제하고 아래 시뮬레이션 코드 제거
                threading.Thread(target=self.simulate_macro_run, daemon=True).start()
            except Exception as e:
                self.emit_log(f"매크로 시작 에러: {e}", "error")
                self.is_running = False
            
            self.emit_status()
    
    def stop_macro(self):
        """매크로 일시정지"""
        if self.is_running:
            self.is_paused = True
            self.emit_log(f"현재 단계: {self.current_part} - 일시정지", "warning")
            # 실제 매크로에 정지 신호 전송
            if self.macro_instance:
                self.macro_instance.stop = True
            self.emit_status()
    
    def resume_macro(self):
        """매크로 재개"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            self.emit_log(f"현재 단계: {self.current_part} - 재개", "success")
            # 실제 매크로에 재개 신호 전송
            if self.macro_instance:
                self.macro_instance.stop = False
            self.emit_status()
    
    def end_macro(self):
        """매크로 종료"""
        self.is_running = False
        self.is_paused = False
        self.current_part = "login"
        self.emit_log("매크로를 종료했습니다.", "error")
        # 실제 매크로 종료
        if self.macro_instance:
            self.macro_instance.end = True
            self.macro_instance = None
        self.emit_status()
    
    def set_part(self, part):
        """현재 단계 설정"""
        self.current_part = part
        self.emit_log(f"단계를 {part}로 설정했습니다.", "info")
        # 실제 매크로에 단계 변경 신호 전송
        if self.macro_instance:
            self.macro_instance.part = part
        self.emit_status()
    
    def update_config(self, section, field, value):
        """설정 업데이트"""
        if section in self.config and field in self.config[section]:
            self.config[section][field] = value
            self.save_config()
            self.emit_status()
            return True
        return False
    
    def simulate_macro_run(self):
        """매크로 실행 시뮬레이션 (실제 구현시 제거)"""
        parts = [
            'login', 'time_wait', 'popup_check', 'click_book',
            'change_window', 'certification', 'seat_frame_move',
            'set_seat_jump', 'booking', 'catch'
        ]
        
        for part in parts:
            if not self.is_running:
                break
                
            while self.is_paused:
                time.sleep(0.1)
                if not self.is_running:
                    break
            
            if not self.is_running:
                break
                
            self.current_part = part
            self.emit_log(f"{part} 단계를 시작합니다.", "info")
            self.emit_status()
            
            # 각 단계별 시뮬레이션 시간
            if part == 'time_wait':
                time.sleep(2)  # 실제로는 예매 시간까지 대기
            elif part == 'booking':
                # booking 단계에서는 반복 실행
                for i in range(5):  # 5번 시도
                    if not self.is_running or self.is_paused:
                        break
                    self.emit_log(f"좌석 선택 시도 {i+1}회", "info")
                    time.sleep(1)
                # 성공으로 가정
                self.current_part = 'catch'
                break
            else:
                time.sleep(1)
        
        if self.is_running:
            self.current_part = 'catch'
            self.emit_log("예매가 완료되었습니다!", "success")
            self.emit_status()

# 글로벌 브리지 인스턴스
bridge = MacroBridge()

@app.route('/')
def index():
    """메인 페이지"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>멜론티켓 예매 자동화</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body>
        <div id="root"></div>
        <script type="text/babel">
            // React 컴포넌트가 여기에 들어갑니다
            // 별도 파일로 분리하는 것을 권장
        </script>
    </body>
    </html>
    """

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """설정 관리 API"""
    if request.method == 'GET':
        return jsonify(bridge.config)
    
    elif request.method == 'POST':
        data = request.json
        section = data.get('section')
        field = data.get('field')
        value = data.get('value')
        
        if bridge.update_config(section, field, value):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid config path'})

@app.route('/api/control', methods=['POST'])
def handle_control():
    """매크로 제어 API"""
    data = request.json
    command = data.get('command')
    
    try:
        if command == 'start':
            bridge.start_macro()
        elif command == 'stop':
            bridge.stop_macro()
        elif command == 'resume':
            bridge.resume_macro()
        elif command == 'end':
            bridge.end_macro()
        elif command == 'set_part':
            part = data.get('part')
            bridge.set_part(part)
        else:
            return jsonify({'success': False, 'error': 'Unknown command'})
        
        return jsonify({'success': True})
    
    except Exception as e:
        bridge.emit_log(f"Control API 에러: {e}", "error")
        return jsonify({'success': False, 'error': str(e)})

@socketio.on('connect')
def handle_connect():
    """클라이언트 연결시"""
    bridge.emit_log("클라이언트가 연결되었습니다.", "info")
    bridge.emit_status()

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제시"""
    bridge.emit_log("클라이언트 연결이 해제되었습니다.", "info")

@socketio.on('control_command')
def handle_control_command(data):
    """WebSocket을 통한 제어 명령"""
    command = data.get('command')
    
    try:
        if command == 'start':
            bridge.start_macro()
        elif command == 'stop':
            bridge.stop_macro()
        elif command == 'resume':
            bridge.resume_macro()
        elif command == 'end':
            bridge.end_macro()
        elif command == 'set_part':
            part = data.get('part')
            bridge.set_part(part)
        elif command == 'update_config':
            section = data.get('section')
            field = data.get('field')
            value = data.get('value')
            bridge.update_config(section, field, value)
    
    except Exception as e:
        bridge.emit_log(f"WebSocket 제어 에러: {e}", "error")

if __name__ == '__main__':
    bridge.emit_log("멜론티켓 예매 자동화 서버를 시작합니다.", "success")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
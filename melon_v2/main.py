from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_socketio import SocketIO, emit
import threading
import json
import os
import sys
import configparser
from datetime import datetime
import traceback
import queue
import time

# Flask 앱 설정
app = Flask(__name__)
app.config['SECRET_KEY'] = 'melon-ticket-secret'
app.static_folder = 'static'
socketio = SocketIO(app, cors_allowed_origins="*")

class MacroBridge:
    """매크로와 웹 UI 간의 브리지 클래스"""
    
    def __init__(self):
        self.macro_instance = None
        self.is_running = False
        self.is_paused = False
        self.current_part = "login"
        self.config = self.load_config()
        self.command_queue = queue.Queue()
        self.log_queue = queue.Queue()
        
        # 시작 시 설정 출력으로 디버깅
        self.emit_log("=== 서버 시작 시 설정 확인 ===", "info")
        self.emit_log(f"prod_id: {self.config['bookInfo']['prod_id']}", "info")
        self.emit_log(f"아이디: {self.config['loginInfo']['id']}", "info")
        self.emit_log("==========================", "info")
        
    def load_config(self):
        """기본 설정 로드 - config.ini를 우선적으로 로드"""
        # 먼저 기본값 설정
        config = {
            'loginInfo': {'id': '', 'pw': ''},
            'bookInfo': {
                'prod_id': '',
                'book_date': '',
                'book_time': '',
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
        
        # config.ini 파일이 있으면 로드하여 덮어쓰기
        config_path = 'config.ini'
        if os.path.exists(config_path):
            try:
                config_parser = configparser.ConfigParser()
                config_parser.read(config_path, encoding='utf-8')
                
                print(f"✅ config.ini 파일 발견: {config_path}")
                print(f"📄 섹션들: {list(config_parser.sections())}")
                
                for section_name in config_parser.sections():
                    if section_name in config:
                        print(f"🔄 [{section_name}] 섹션 처리 중...")
                        for key, value in config_parser[section_name].items():
                            if key in config[section_name]:
                                old_value = config[section_name][key]
                                try:
                                    # 숫자로 변환 시도
                                    if value.isdigit():
                                        config[section_name][key] = int(value)
                                    else:
                                        config[section_name][key] = value
                                    
                                    print(f"  ✓ {key}: {old_value} → {config[section_name][key]}")
                                except ValueError:
                                    config[section_name][key] = value
                                    print(f"  ✓ {key}: {old_value} → {value}")
                            else:
                                print(f"  ⚠️ 알 수 없는 키 무시: {key}")
                    else:
                        print(f"  ⚠️ 알 수 없는 섹션 무시: {section_name}")
                
                print("✅ config.ini 로드 완료")
                
            except Exception as e:
                print(f"❌ config.ini 로드 실패: {e}")
                print("기본 설정을 사용합니다.")
                traceback.print_exc()
        else:
            print("⚠️ config.ini 파일이 없습니다. 기본 설정을 사용합니다.")
        
        return config
    
    def save_config(self):
        """설정을 config.ini 파일로 저장 및 매크로에 동기화"""
        try:
            config_parser = configparser.ConfigParser()
            
            # 섹션별로 설정을 config_parser에 추가
            for section, items in self.config.items():
                config_parser[section] = {}
                for key, value in items.items():
                    config_parser[section][key] = str(value)
            
            # 파일에 저장
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config_parser.write(configfile)
            
            # 실행 중인 매크로가 있으면 설정 동기화
            if self.macro_instance:
                self.macro_instance.sync_config_from_bridge()
                
            self.emit_log("✅ 설정이 저장되었습니다.", "success")
            
        except Exception as e:
            self.emit_log(f"❌ 설정 저장 에러: {e}", "error")
            traceback.print_exc()
    
    def reload_config(self):
        """설정을 다시 로드"""
        self.emit_log("🔄 설정을 다시 로드합니다...", "info")
        old_config = self.config.copy()
        self.config = self.load_config()
        
        # 변경된 설정 확인
        changed_items = []
        for section in self.config:
            for key in self.config[section]:
                if old_config.get(section, {}).get(key) != self.config[section][key]:
                    changed_items.append(f"{section}.{key}: {old_config.get(section, {}).get(key)} → {self.config[section][key]}")
        
        if changed_items:
            for item in changed_items:
                self.emit_log(f"  📝 {item}", "info")
        else:
            self.emit_log("  ℹ️ 변경된 설정이 없습니다.", "info")
        
        # UI로 새로운 설정 전송
        self.emit_status()
        return True
    
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
            'config': self.config  # 전체 설정을 전송
        }
        socketio.emit('status_update', status_data)
        print(f"📤 UI로 상태 전송: running={self.is_running}, paused={self.is_paused}, part={self.current_part}")
        print(f"📤 설정 전송: prod_id={self.config['bookInfo']['prod_id']}, id={self.config['loginInfo']['id']}")
    
    def start_macro(self):
        """매크로 시작"""
        if not self.is_running:
            # 필수 설정값들 검증
            if not self.config['loginInfo']['id']:
                self.emit_log("❌ 아이디를 입력해주세요.", "error")
                return
            if not self.config['loginInfo']['pw']:
                self.emit_log("❌ 비밀번호를 입력해주세요.", "error")
                return
            if not self.config['bookInfo']['prod_id']:
                self.emit_log("❌ 상품 ID를 입력해주세요.", "error")
                return
            
            self.is_running = True
            self.is_paused = False
            self.emit_log("🚀 매크로를 시작합니다.", "success")
            
            # 최신 설정으로 config.ini 저장
            self.save_config()
            
            try:
                # 실제 매크로 클래스 인스턴스 생성 (브리지 전달)
                from Macro import Macro
                self.macro_instance = Macro(bridge=self)
                self.macro_instance.start_with_ui()
                
            except Exception as e:
                self.emit_log(f"❌ 매크로 시작 에러: {e}", "error")
                self.is_running = False
                traceback.print_exc()
            
            self.emit_status()
    
    def stop_macro(self):
        """매크로 일시정지"""
        if self.is_running:
            self.is_paused = True
            self.emit_log(f"⏸️ 현재 단계: {self.current_part} - 일시정지", "warning")
            if self.macro_instance:
                self.macro_instance.stop = True
            self.emit_status()
    
    def resume_macro(self):
        """매크로 재개"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            self.emit_log(f"▶️ 현재 단계: {self.current_part} - 재개", "success")
            if self.macro_instance:
                self.macro_instance.stop = False
            self.emit_status()
    
    def end_macro(self):
        """매크로 종료"""
        self.is_running = False
        self.is_paused = False
        self.current_part = "login"
        self.emit_log("🛑 매크로를 종료했습니다.", "error")
        
        if self.macro_instance:
            self.macro_instance.end = True
            # 웹드라이버 종료
            try:
                if hasattr(self.macro_instance, 'driver') and self.macro_instance.driver:
                    self.macro_instance.driver.quit()
            except:
                pass
            self.macro_instance = None
        
        self.emit_status()
    
    def set_part(self, part):
        """현재 단계 설정"""
        self.current_part = part
        self.emit_log(f"📍 단계를 {part}로 설정했습니다.", "info")
        if self.macro_instance:
            self.macro_instance.part = part
        self.emit_status()
    
    def update_config(self, section, field, value):
        """설정 업데이트"""
        if section in self.config and field in self.config[section]:
            old_value = self.config[section][field]
            self.config[section][field] = value
            
            # 특별한 설정들에 대한 추가 처리
            if section == 'bookInfo':
                if field in ['order', 'grade']:
                    # 좌석 순서나 등급이 설정되면 special_area를 Y로 변경
                    if value and str(value).strip():
                        self.config['function']['special_area'] = 'Y'
                        self.emit_log(f"🎯 {field} 설정으로 특별 구역이 활성화됩니다.", "info")
                    else:
                        # 둘 다 비어있으면 special_area를 N으로 변경
                        if not self.config['bookInfo']['order'] and not self.config['bookInfo']['grade']:
                            self.config['function']['special_area'] = 'N'
                            self.emit_log("🔄 특별 구역이 비활성화됩니다.", "info")
            
            # 설정 저장 및 UI 업데이트
            self.save_config()
            self.emit_status()
            
            self.emit_log(f"⚙️ {section}.{field}: {old_value} → {value}", "info")
            return True
        else:
            self.emit_log(f"❌ 잘못된 설정 경로: {section}.{field}", "error")
            return False

# 글로벌 브리지 인스턴스
bridge = MacroBridge()

# HTML 템플릿들 (기존과 동일)
MAIN_UI_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>멜론티켓 예매 자동화</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        .fade-in { animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div id="root">
        <div class="flex items-center justify-center min-h-screen">
            <div class="text-lg text-gray-600">UI 컴포넌트를 로딩하는 중...</div>
        </div>
    </div>
    
    <script>
        async function loadReactComponent() {
            console.log("컴포넌트 로딩 시작");
            try {
                // React와 라이브러리들을 전역으로 설정
                window.React = React;
                window.ReactDOM = ReactDOM;
                
                // React hooks 전역 설정
                const { useState, useEffect, useRef } = React;
                window.useState = useState;
                window.useEffect = useEffect;
                window.useRef = useRef;
                
                // Lucide 아이콘들 확인 및 개별 설정
                console.log('Lucide 객체 확인:', typeof lucide, lucide);
                
                if (typeof lucide === 'object' && lucide !== null) {
                    // 각 아이콘이 함수인지 확인하고 설정
                    const iconNames = ['Play', 'Square', 'Settings', 'RotateCcw', 'Calendar', 
                                     'Clock', 'Music', 'Volume2', 'VolumeX', 'SkipForward'];
                    
                    iconNames.forEach(iconName => {
                        const icon = lucide[iconName];
                        console.log(`${iconName} 아이콘:`, typeof icon, icon);
                        
                        if (typeof icon === 'function') {
                            window[iconName] = icon;
                            console.log(`✓ ${iconName} 아이콘 설정 완료`);
                        } else {
                            console.warn(`✗ ${iconName} 아이콘이 함수가 아닙니다. div로 대체합니다.`);
                            window[iconName] = 'div';
                        }
                    });
                } else {
                    console.error('Lucide 라이브러리를 로드할 수 없습니다. 모든 아이콘을 div로 대체합니다.');
                    ['Play', 'Square', 'Settings', 'RotateCcw', 'Calendar', 
                     'Clock', 'Music', 'Volume2', 'VolumeX', 'SkipForward'].forEach(name => {
                        window[name] = 'div';
                    });
                }

                // ui.jsx 파일 로드
                let componentUrl = '/static/components/ui.jsx';
                let response = await fetch(componentUrl);
                
                if (!response.ok) {
                    console.log('ui.jsx 파일을 찾을 수 없음, ui.js 시도');
                    componentUrl = '/static/components/ui.js';
                    response = await fetch(componentUrl);
                }
                
                if (!response.ok) {
                    throw new Error(`컴포넌트 파일을 찾을 수 없습니다: ${response.status}`);
                }
                
                console.log(`컴포넌트 파일 로드 성공: ${componentUrl}`);
                const componentCode = await response.text();
                console.log('컴포넌트 코드 길이:', componentCode.length);

                // 코드가 이미 React.createElement 형태이므로 직접 실행
                console.log('컴포넌트 코드 실행 시작');
                eval(componentCode);
                
                // MelonTicketUI가 전역에 있는지 확인
                if (typeof window.MelonTicketUI !== 'function') {
                    throw new Error('MelonTicketUI 컴포넌트를 찾을 수 없습니다. window.MelonTicketUI가 정의되지 않았습니다.');
                }
                
                console.log('컴포넌트 생성 완료');

                // React 컴포넌트 렌더링
                const root = ReactDOM.createRoot(document.getElementById('root'));
                root.render(React.createElement(window.MelonTicketUI));
                
                console.log('컴포넌트 렌더링 완료');
                
            } catch (error) {
                console.error('컴포넌트 로딩 실패:', error);
                console.error('Error stack:', error.stack);
                
                // 상세한 에러 정보 표시
                document.getElementById('root').innerHTML = `
                    <div class="flex items-center justify-center min-h-screen">
                        <div class="max-w-lg p-6 bg-red-50 border border-red-200 rounded-lg">
                            <h2 class="text-lg font-semibold text-red-800 mb-2">컴포넌트 로딩 실패</h2>
                            <p class="text-red-600 mb-4">${error.message}</p>
                            <button onclick="loadFallbackUI()" 
                                    class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                                폴백 UI로 이동
                            </button>
                        </div>
                    </div>
                `;
            }
        }

        function loadFallbackUI() {
            console.log('폴백 UI로 리다이렉트');
            window.location.href = '/fallback';
        }

        // DOM 로드 완료 후 실행
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadReactComponent);
        } else {
            loadReactComponent();
        }
    </script>
</body>
</html>
'''

def setup_directories():
    """필요한 디렉토리 구조 생성"""
    directories = ['static', 'static/components', 'static/js', 'static/css']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def check_ui_component():
    """UI 컴포넌트 파일 존재 여부 확인 (.jsx 또는 .js)"""
    ui_paths = [
        os.path.join('static', 'components', 'ui.jsx'),
        os.path.join('static', 'components', 'ui.js')
    ]
    for path in ui_paths:
        if os.path.exists(path):
            return True, path
    return False, None

# Flask 라우트 설정
@app.route('/')
def index():
    """메인 페이지"""
    exists, path = check_ui_component()
    if exists:
        return MAIN_UI_TEMPLATE
    else:
        return '''
        <div style="text-align: center; padding: 50px;">
            <h1>UI 컴포넌트 파일이 없습니다</h1>
            <p>static/components/ui.jsx 또는 ui.js 파일을 배치해주세요.</p>
            <a href="/fallback">기본 UI로 이동</a>
        </div>
        '''

@app.route('/fallback')
def fallback():
    """간단한 폴백 UI"""
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>멜론티켓 예매 자동화 - 기본 UI</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    </head>
    <body>
        <div style="padding: 20px;">
            <h1>멜론티켓 예매 자동화</h1>
            <div id="status">연결 중...</div>
            <div>
                <button onclick="sendCommand('start')">시작</button>
                <button onclick="sendCommand('stop')">일시정지</button>
                <button onclick="sendCommand('resume')">재개</button>
                <button onclick="sendCommand('end')">종료</button>
                <button onclick="reloadConfig()">설정 다시 로드</button>
            </div>
            <div id="logs" style="height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-top: 20px;"></div>
        </div>
        
        <script>
            const socket = io();
            
            socket.on('connect', () => {
                document.getElementById('status').innerHTML = '서버에 연결됨';
            });
            
            socket.on('log_message', (data) => {
                const logs = document.getElementById('logs');
                logs.innerHTML += '<div>' + data.timestamp + ' - ' + data.message + '</div>';
                logs.scrollTop = logs.scrollHeight;
            });
            
            function sendCommand(cmd) {
                socket.emit('control_command', {command: cmd});
            }
            
            function reloadConfig() {
                fetch('/api/config/reload', { method: 'POST' });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/static/<path:filename>')
def static_files(filename):
    """정적 파일 서빙"""
    return send_from_directory(app.static_folder, filename)

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
            return jsonify({'success': True, 'config': bridge.config})
        else:
            return jsonify({'success': False, 'error': 'Invalid config path'})

@app.route('/api/config/reload', methods=['POST'])
def reload_config():
    """설정 다시 로드 API"""
    try:
        bridge.reload_config()
        return jsonify({'success': True, 'config': bridge.config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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

# WebSocket 이벤트 핸들러
@socketio.on('connect')
def handle_connect():
    """클라이언트 연결시"""
    bridge.emit_log("🔗 클라이언트가 연결되었습니다.", "success")
    # 연결 즉시 현재 설정을 전송
    bridge.emit_status()

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제시"""
    bridge.emit_log("🔌 클라이언트 연결이 해제되었습니다.", "info")

@socketio.on('request_config')
def handle_request_config():
    """클라이언트에서 설정 요청 시"""
    bridge.emit_log("📤 클라이언트가 설정을 요청했습니다.", "info")
    bridge.emit_status()

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
        bridge.emit_log(f"❌ WebSocket 제어 에러: {e}", "error")

if __name__ == '__main__':
    print("=" * 60)
    print("🎵 멜론티켓 예매 자동화 웹 UI")
    print("=" * 60)
    
    # 디렉토리 구조 설정
    setup_directories()
    
    # config.ini 파일 확인
    if os.path.exists('config.ini'):
        print("✅ config.ini 파일 발견")
        try:
            config_parser = configparser.ConfigParser()
            config_parser.read('config.ini', encoding='utf-8')
            
            if 'bookInfo' in config_parser and 'prod_id' in config_parser['bookInfo']:
                prod_id = config_parser['bookInfo']['prod_id']
                print(f"📦 상품ID 확인: {prod_id}")
            else:
                print("⚠️ bookInfo 섹션 또는 prod_id가 없습니다.")
        except Exception as e:
            print(f"❌ config.ini 읽기 실패: {e}")
    else:
        print("⚠️ config.ini 파일이 없습니다.")
    
    # UI 컴포넌트 파일 확인
    exists, path = check_ui_component()
    if exists:
        print(f"✅ 고급 UI 컴포넌트 발견: {path}")
        print("   -> 풀 기능 UI로 실행됩니다.")
    else:
        print("⚠️  UI 컴포넌트 파일이 없습니다:")
        print("   static/components/ui.jsx 또는 ui.js")
        print("   -> 기본 UI로 실행됩니다.")
    
    print("=" * 60)
    print("🚀 서버 시작 중...")
    print("📱 웹 브라우저에서 http://localhost:5000 접속")
    print("=" * 60)
    
    try:
        bridge.emit_log("🎉 멜론티켓 예매 자동화 서버를 시작합니다.", "success")
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 서버를 종료합니다.")
    except Exception as e:
        print(f"❌ 서버 실행 에러: {e}")
        print("\n📦 필요한 패키지 설치:")
        print("pip install flask flask-socketio selenium pillow easyocr opencv-python playsound configparser pause")
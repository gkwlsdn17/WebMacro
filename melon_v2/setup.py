#!/usr/bin/env python3
"""
멜론티켓 예매 자동화 UI 설정 스크립트
ui.tsx 파일을 자동으로 적절한 위치에 복사하고 설정합니다.
"""

import os
import shutil
import sys

def create_directories():
    """필요한 디렉토리 구조 생성"""
    directories = [
        'static',
        'static/components', 
        'static/js',
        'static/css'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 디렉토리 생성: {directory}")
        else:
            print(f"📁 디렉토리 존재: {directory}")

def setup_ui_component():
    """UI 컴포넌트 파일 설정"""
    source_files = [
        'ui.tsx',
        'paste-2.txt'  # 두 번째 문서의 파일명
    ]
    
    target_path = os.path.join('static', 'components', 'ui.tsx')
    
    # 소스 파일 찾기
    source_file = None
    for filename in source_files:
        if os.path.exists(filename):
            source_file = filename
            break
    
    if source_file:
        try:
            shutil.copy2(source_file, target_path)
            print(f"✅ UI 컴포넌트 복사 완료: {source_file} -> {target_path}")
            return True
        except Exception as e:
            print(f"❌ 파일 복사 실패: {e}")
            return False
    else:
        print("❌ ui.tsx 파일을 찾을 수 없습니다.")
        print("다음 중 하나의 파일이 현재 디렉토리에 있어야 합니다:")
        for filename in source_files:
            print(f"  - {filename}")
        return False

def create_package_json():
    """package.json 파일 생성 (개발용)"""
    package_json_content = '''{
  "name": "melon-ticket-automation-ui",
  "version": "1.0.0",
  "description": "멜론티켓 예매 자동화 UI",
  "main": "index.js",
  "scripts": {
    "dev": "python main.py",
    "start": "python main.py"
  },
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "typescript": "^4.9.0"
  }
}'''
    
    try:
        with open('package.json', 'w', encoding='utf-8') as f:
            f.write(package_json_content)
        print("✅ package.json 생성 완료")
    except Exception as e:
        print(f"⚠️  package.json 생성 실패: {e}")

def create_readme():
    """README.md 파일 생성"""
    readme_content = '''# 멜론티켓 예매 자동화 UI

## 설치 및 실행

### 1. 필요한 패키지 설치
```bash
pip install flask flask-socketio selenium pillow easyocr opencv-python playsound configparser pause
```

### 2. 프로젝트 설정
```bash
python setup.py
```

### 3. 실행
```bash
python main.py
```

### 4. 웹 브라우저 접속
http://localhost:5000

## 파일 구조
```
project/
├── main.py              # 메인 실행 파일
├── setup.py             # 설정 스크립트
├── static/
│   └── components/
│       └── ui.tsx       # React UI 컴포넌트
├── app.py               # Flask 앱 (기존)
├── macro_ui.py          # 매크로 UI (기존)
└── README.md
```

## 주요 기능
- 실시간 로그 확인
- 매크로 상태 모니터링
- 설정 변경 및 저장
- 단계별 실행 제어

## 문제 해결
1. UI가 로딩되지 않는 경우:
   - static/components/ui.tsx 파일이 있는지 확인
   - 브라우저 콘솔에서 오류 메시지 확인

2. 서버 연결 문제:
   - Flask 서버가 정상적으로 실행되는지 확인
   - 포트 5000이 사용 중인지 확인
'''
    
    try:
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ README.md 생성 완료")
    except Exception as e:
        print(f"⚠️  README.md 생성 실패: {e}")

def main():
    print("=" * 60)
    print("🚀 멜론티켓 예매 자동화 UI 설정")
    print("=" * 60)
    
    # 1. 디렉토리 생성
    print("\n1. 디렉토리 구조 생성...")
    create_directories()
    
    # 2. UI 컴포넌트 설정
    print("\n2. UI 컴포넌트 설정...")
    ui_success = setup_ui_component()
    
    # 3. 추가 파일 생성
    print("\n3. 추가 파일 생성...")
    create_package_json()
    create_readme()
    
    # 4. 설정 완료 메시지
    print("\n" + "=" * 60)
    if ui_success:
        print("✅ 설정이 완료되었습니다!")
        print("\n다음 단계:")
        print("1. python main.py 실행")
        print("2. 웹 브라우저에서 http://localhost:5000 접속")
    else:
        print("⚠️  설정이 부분적으로 완료되었습니다.")
        print("\n남은 단계:")
        print("1. ui.tsx 파일을 static/components/ 폴더에 수동으로 복사")
        print("2. python main.py 실행")
        print("3. 웹 브라우저에서 http://localhost:5000 접속")
    print("=" * 60)

if __name__ == '__main__':
    main()
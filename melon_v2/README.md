# 멜론티켓 예매 자동화 UI

기존 콘솔 기반 멜론티켓 예매 자동화 프로그램을 웹 UI로 업그레이드한 버전입니다.

## 🚀 주요 기능

- **웹 기반 UI**: 브라우저에서 쉽게 조작 가능
- **실시간 제어**: 시작/중지/재개/종료 버튼으로 간편한 조작
- **실시간 로그**: WebSocket을 통한 실시간 로그 모니터링
- **설정 관리**: UI에서 직접 모든 설정 변경 가능
- **단계별 제어**: 원하는 단계부터 시작 가능
- **좌석 설정**: 좌석 순서, 등급 등 세부 설정 지원

## 📋 설치 요구사항

### Python 패키지 설치

```bash
pip install flask flask-socketio selenium pillow easyocr opencv-python playsound configparser pause
```

### 추가 요구사항

- **Chrome 브라우저** 및 **ChromeDriver** 설치
- **EasyOCR**을 위한 GPU 드라이버 (선택사항, 성능 향상용)

## 📁 파일 구조

```
project/
├── main.py                 # 메인 실행 파일
├── Macroy.py              # 수정된 매크로 클래스
├── function.py            # 기존 함수들
├── CODE.py                # 상수 정의
├── config.ini             # 설정 파일 (자동 생성)
├── catch.mp3             # 완료 사운드 (선택사항)
└── images/               # 보안문자 이미지 저장 폴더 (자동 생성)
└── static/components/ui.jsx      # ui 구성 파일
```

## 🎯 실행 방법

### 1. 기본 실행

```bash
python main.py
```

### 2. 웹 브라우저 접속

- **URL**: `http://localhost:5000`
- 자동으로 기본 브라우저에서 열리지 않는다면 수동으로 접속

### 3. UI 사용법

#### 초기 설정

1. **로그인 정보**: 멜론 계정 아이디/비밀번호 입력
2. **예매 정보**: 상품 ID, 예매 날짜, 시간 입력
3. **예매 시작 시간**: 예매가 시작되는 정확한 시간 설정

#### 고급 설정

- **좌석 순서**: `A,B,C` 형태로 선호 구역 설정
- **좌석 등급**: `S석,A석,B석` 형태로 선호 등급 설정
- **좌석 점프**: N번째 좌석부터 선택 (빠른 선택용)
- **자동 보안인증**: EasyOCR을 이용한 자동 보안문자 입력
- **완료 사운드**: 예매 완료시 알림 사운드 재생

#### 실행 제어

- **시작**: 매크로 실행 시작
- **일시정지**: 현재 단계에서 대기
- **재개**: 일시정지된 매크로 재개
- **종료**: 매크로 완전 종료
- **단계 선택**: 특정 단계부터 시작 가능

## 🔧 설정 파일 (config.ini)

프로그램이 처음 실행되면 `config.ini` 파일이 자동으로 생성됩니다.

```ini
[loginInfo]
id = your_id
pw = your_password

[bookInfo]
prod_id = 12345
book_date = 2024-12-25
book_time = 1400
order = A,B,C
grade = S석,A석

[program]
year = 2024
month = 12
day = 25
hour = 14
minute = 0

[function]
auto_certification = Y
special_area = Y
sound = Y
seat_jump = N
seat_jump_count = 0
seat_jump_special_repeat = N
seat_jump_special_repeat_count = 0
skip_date_click = N
```

## 🚨 주의사항

1. **Chrome 브라우저**: 반드시 Chrome 브라우저가 설치되어 있어야 합니다
2. **ChromeDriver**: Selenium이 Chrome을 제어하기 위해 필요합니다
3. **네트워크**: 예매 시간에 안정적인 인터넷 연결 필요
4. **시간 동기화**: 시스템 시간이 정확해야 합니다
5. **방화벽**: 5000 포트가 차단되지 않아야 합니다

## 🐛 트러블슈팅

### 서버 연결 안됨

- 브라우저에서 `http://localhost:5000` 접속 확인
- 방화벽에서 5000 포트 허용 확인
- 다른 프로그램이 5000 포트 사용 여부 확인

### ChromeDriver 에러

```bash
# ChromeDriver 자동 설치
pip install webdriver-manager
```

### 보안문자 인식 실패

- EasyOCR 재설치: `pip uninstall easyocr && pip install easyocr`
- 수동 인증 모드 사용: 자동 보안인증을 '미사용'으로 설정

### 메모리 부족

- 불필요한 브라우저 탭 닫기
- 시스템 메모리 확인 (최소 4GB 권장)

## 📞 지원

문제가 발생하거나 개선 제안이 있다면 이슈를 등록해 주세요.

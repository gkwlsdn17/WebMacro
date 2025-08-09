#!/usr/bin/env python3
"""
NumPy 호환성 문제 해결 스크립트
EasyOCR과 관련 패키지의 NumPy 버전 호환성 문제를 해결합니다.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """명령어 실행 및 결과 출력"""
    print(f"\n🔧 {description}")
    print(f"실행: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 성공: {description}")
            if result.stdout.strip():
                print(f"출력: {result.stdout.strip()}")
        else:
            print(f"❌ 실패: {description}")
            if result.stderr.strip():
                print(f"오류: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return False
    
    return True

def check_current_versions():
    """현재 설치된 패키지 버전 확인"""
    print("\n📦 현재 설치된 패키지 버전:")
    packages = ['numpy', 'torch', 'easyocr', 'opencv-python', 'scikit-image', 'Pillow']
    
    for package in packages:
        try:
            result = subprocess.run(f"pip show {package}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('Version:'):
                        version = line.split(': ')[1]
                        print(f"  {package}: {version}")
                        break
            else:
                print(f"  {package}: 설치되지 않음")
        except Exception as e:
            print(f"  {package}: 확인 실패 - {e}")

def solution_1_downgrade_numpy():
    """해결방법 1: NumPy 다운그레이드"""
    print("\n" + "="*60)
    print("해결방법 1: NumPy를 1.x 버전으로 다운그레이드")
    print("="*60)
    
    commands = [
        ("pip uninstall numpy -y", "기존 NumPy 제거"),
        ("pip install 'numpy<2.0'", "NumPy 1.x 설치"),
        ("pip install 'numpy>=1.21.0,<2.0'", "안정적인 NumPy 1.x 설치")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def solution_2_upgrade_packages():
    """해결방법 2: 호환 가능한 패키지로 업그레이드"""
    print("\n" + "="*60)
    print("해결방법 2: NumPy 2.x 호환 패키지로 업그레이드")
    print("="*60)
    
    commands = [
        ("pip install --upgrade pip", "pip 업그레이드"),
        ("pip install --upgrade setuptools wheel", "빌드 도구 업그레이드"),
        ("pip install 'numpy>=2.0'", "NumPy 2.x 설치"),
        ("pip uninstall torch torchvision easyocr opencv-python scikit-image -y", "호환성 문제 패키지 제거"),
        ("pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu", "PyTorch 재설치"),
        ("pip install --no-cache-dir --upgrade scikit-image", "scikit-image 재설치"),
        ("pip install --no-cache-dir opencv-python", "OpenCV 재설치"),
        ("pip install --no-cache-dir easyocr", "EasyOCR 재설치")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️ {description} 실패, 다음 단계로 진행...")
    
    return True

def solution_3_virtual_environment():
    """해결방법 3: 가상환경 생성 및 설정"""
    print("\n" + "="*60)
    print("해결방법 3: 새로운 가상환경 생성")
    print("="*60)
    
    venv_name = "melon_macro_env"
    
    commands = [
        (f"python -m venv {venv_name}", f"가상환경 '{venv_name}' 생성"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    # 가상환경 활성화 명령어는 OS별로 다름
    if os.name == 'nt':  # Windows
        activate_command = f"{venv_name}\\Scripts\\activate"
        pip_command = f"{venv_name}\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        activate_command = f"source {venv_name}/bin/activate"
        pip_command = f"{venv_name}/bin/pip"
    
    print(f"\n가상환경 활성화 방법:")
    print(f"Windows: {venv_name}\\Scripts\\activate")
    print(f"Linux/Mac: source {venv_name}/bin/activate")
    
    # 가상환경에서 패키지 설치
    venv_commands = [
        (f"{pip_command} install --upgrade pip", "가상환경에서 pip 업그레이드"),
        (f"{pip_command} install 'numpy<2.0'", "NumPy 1.x 설치"),
        (f"{pip_command} install flask flask-socketio", "Flask 관련 패키지"),
        (f"{pip_command} install selenium", "Selenium"),
        (f"{pip_command} install pillow", "Pillow"),
        (f"{pip_command} install opencv-python", "OpenCV"),
        (f"{pip_command} install easyocr", "EasyOCR"),
        (f"{pip_command} install playsound configparser pause", "기타 패키지")
    ]
    
    for command, description in commands:
        run_command(command, description)
    
    return True

def create_requirements_txt():
    """호환되는 requirements.txt 파일 생성"""
    requirements_content = """# NumPy 1.x 호환 패키지 버전
numpy>=1.21.0,<2.0
flask>=2.0.0
flask-socketio>=5.0.0
selenium>=4.0.0
pillow>=8.0.0
opencv-python>=4.5.0
easyocr>=1.6.0
playsound>=1.2.0
configparser>=5.0.0
pause>=0.3

# 추가적으로 필요할 수 있는 패키지
torch>=1.12.0
torchvision>=0.13.0
scikit-image>=0.19.0,<0.22.0
"""
    
    try:
        with open('requirements_compatible.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        print("✅ requirements_compatible.txt 파일 생성 완료")
        print("사용법: pip install -r requirements_compatible.txt")
    except Exception as e:
        print(f"❌ requirements.txt 파일 생성 실패: {e}")

def main():
    print("🚀 NumPy 호환성 문제 해결 도구")
    print("="*60)
    
    # 현재 상태 확인
    check_current_versions()
    
    print("\n💡 해결 방법을 선택해주세요:")
    print("1. NumPy를 1.x로 다운그레이드 (권장)")
    print("2. 모든 패키지를 NumPy 2.x 호환으로 업그레이드")
    print("3. 새로운 가상환경 생성")
    print("4. 호환 가능한 requirements.txt 생성만")
    print("0. 종료")
    
    while True:
        try:
            choice = input("\n선택 (0-4): ").strip()
            
            if choice == '0':
                print("종료합니다.")
                break
            elif choice == '1':
                print("\n선택: NumPy 다운그레이드")
                if solution_1_downgrade_numpy():
                    print("✅ NumPy 다운그레이드 완료!")
                    print("이제 python main.py를 실행해보세요.")
                break
            elif choice == '2':
                print("\n선택: 패키지 업그레이드")
                solution_2_upgrade_packages()
                print("✅ 패키지 업그레이드 시도 완료!")
                print("이제 python main.py를 실행해보세요.")
                break
            elif choice == '3':
                print("\n선택: 가상환경 생성")
                solution_3_virtual_environment()
                print("✅ 가상환경 생성 완료!")
                print("가상환경을 활성화한 후 python main.py를 실행해보세요.")
                break
            elif choice == '4':
                print("\n선택: requirements.txt 생성")
                create_requirements_txt()
                break
            else:
                print("올바른 번호를 선택해주세요 (0-4)")
                
        except KeyboardInterrupt:
            print("\n\n종료합니다.")
            break
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == '__main__':
    main()
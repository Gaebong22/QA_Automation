import pyautogui
import time
import sys
import os

# --- 설정 ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 이미지 파일 경로
IMAGES = {
    'step1_button': os.path.join(SCRIPT_DIR, 'step1.png'),
    'step2_screen': os.path.join(SCRIPT_DIR, 'step2.png'),
    'step3_button': os.path.join(SCRIPT_DIR, 'step3.png'),
    'step4_screen': os.path.join(SCRIPT_DIR, 'step4.png'),
}

CONFIDENCE_THRESHOLD = 0.75
WAIT_BEFORE_ACTION = 1
MAX_FIND_ATTEMPTS = 5
FIND_RETRY_INTERVAL = 1
MAX_VERIFY_TIME = 10
VERIFY_CHECK_INTERVAL = 0.5

# --- 헬퍼 함수들 ---

def find_and_click_image(image_path, name, max_attempts=MAX_FIND_ATTEMPTS):
    """이미지를 찾아서 클릭하는 함수"""
    print(f"\n[동작] '{name}' 버튼을 찾습니다...")
    
    for attempt in range(max_attempts):
        try:
            location = pyautogui.locateOnScreen(
                image_path,
                confidence=CONFIDENCE_THRESHOLD,
                grayscale=False
            )
            
            if location:
                print(f"✅ '{name}' 발견! (시도 {attempt + 1}/{max_attempts})")
                
                # 클릭
                center_x = location.left + location.width / 2
                center_y = location.top + location.height / 2
                pyautogui.click(center_x, center_y, duration=0.1)
                
                print(f"➡️ '{name}' 클릭 완료! 위치: ({center_x:.0f}, {center_y:.0f})")
                print(f"    화면 전환 대기 ({WAIT_BEFORE_ACTION}초)...")
                time.sleep(WAIT_BEFORE_ACTION)
                return True
                
        except Exception as e:
            print(f"⚠️ 검색 중 오류: {e}")
        
        if attempt < max_attempts - 1:
            print(f"👀 '{name}'을(를) 찾을 수 없습니다. {FIND_RETRY_INTERVAL}초 후 재시도... (시도 {attempt + 1}/{max_attempts})")
            time.sleep(FIND_RETRY_INTERVAL)
    
    print(f"❌ 실패: '{name}'을(를) {max_attempts}회 시도 후에도 찾을 수 없습니다.")
    return False


def verify_screen(image_path, name, max_time=MAX_VERIFY_TIME):
    """화면에 특정 이미지가 나타나는지 검증하는 함수"""
    print(f"\n[검증] '{name}' 화면을 최대 {max_time}초 동안 확인합니다...")
    
    start_time = time.time()
    
    while time.time() - start_time < max_time:
        try:
            found = pyautogui.locateOnScreen(
                image_path,
                confidence=CONFIDENCE_THRESHOLD,
                grayscale=False
            )
            
            if found:
                print(f"🎉 성공: '{name}' 화면이 출력되었습니다!")
                return True
                
        except Exception as e:
            pass  # 계속 시도
        
        time.sleep(VERIFY_CHECK_INTERVAL)
    
    print(f"❌ 실패: '{name}' 화면이 {max_time}초 내에 나타나지 않았습니다.")
    return False


def run_step(step_num, button_key, screen_key):
    """단일 스텝 실행: 버튼 클릭 -> 화면 검증"""
    print(f"\n{'='*60}")
    print(f"📍 STEP {step_num} 시작")
    print(f"{'='*60}")
    
    # 버튼 클릭
    if not find_and_click_image(IMAGES[button_key], button_key):
        return False
    
    # 화면 검증
    if not verify_screen(IMAGES[screen_key], screen_key):
        return False
    
    return True


# --- 메인 실행 ---

def main():
    print("="*60)
    print("🤖 PyAutoGUI 자동화 스크립트 시작 🤖")
    print("="*60)
    print("👉 1단계: step1.png 클릭 -> step2.png 확인")
    print("👉 2단계: step3.png 클릭 -> step4.png 확인")
    print("="*60)
    
    # 초기 대기
    print(f"\n[초기화] {WAIT_BEFORE_ACTION}초 대기 중...")
    time.sleep(WAIT_BEFORE_ACTION)
    
    # STEP 1: step1 버튼 클릭 -> step2 화면 확인
    if not run_step(1, 'step1_button', 'step2_screen'):
        sys.exit(1)
    
    # STEP 2: step3 버튼 클릭 -> step4 화면 확인
    if not run_step(2, 'step3_button', 'step4_screen'):
        sys.exit(1)
    
    # 완료
    print("\n" + "="*60)
    print("✨ 모든 자동화 단계가 성공적으로 완료되었습니다! ✨")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 스크립트를 중단했습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
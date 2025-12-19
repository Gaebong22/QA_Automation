import pyautogui
import time
import sys
import os

# --- 설정 ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ⭐ 여기만 수정 ⭐
# 각 단계를 (버튼 이미지, 확인할 화면 이미지, 클릭 전 추가 대기시간) 튜플로 정의
STEPS = [
    # (클릭할 버튼, 확인할 화면, 클릭 전 대기시간(초) - 생략 시 0초)
    ('step1.png', 'step2.png'),
    ('step3.png', 'step4.png'),
    ('step5.png', 'step6.png', 3),  # step5는 3초 추가 대기
    ('step7.png', 'step8.png'),
    # 예시: ('step9.png', 'step10.png', 5),  # 5초 추가 대기
]

# 예외 팝업 이미지 (발견 시 클릭하여 닫기)
EXCEPTION_POPUPS = [
    'newRanagerpup.png',      # SS급 캐릭터 첫 획득 팝업
    'taptocontinue.png',   # tap to continue
    'cancel_button.png',      # 취소 버튼 루비 부족 혹은 범용
    # 추가 예외 팝업을 여기에 등록
]   

CONFIDENCE_THRESHOLD = 0.75
WAIT_BEFORE_ACTION = 1
MAX_FIND_ATTEMPTS = 5
FIND_RETRY_INTERVAL = 1
MAX_VERIFY_TIME = 10
VERIFY_CHECK_INTERVAL = 0.5
EXCEPTION_CHECK_INTERVAL = 0.3  # 예외 팝업 체크 주기 (초)

# --- 헬퍼 함수들 ---

def check_and_close_exception_popups():
    """예외 팝업이 있는지 확인하고 있으면 클릭해서 닫기"""
    for popup_file in EXCEPTION_POPUPS:
        popup_path = os.path.join(SCRIPT_DIR, popup_file)
        
        # 파일이 존재하지 않으면 건너뛰기
        if not os.path.exists(popup_path):
            continue
        
        try:
            location = pyautogui.locateOnScreen(
                popup_path,
                confidence=0.6,#CONFIDENCE_THRESHOLD,
                grayscale=True
            )
            
            if location:
                center_x = location.left + location.width / 2
                center_y = location.top + location.height / 2
                pyautogui.click(center_x, center_y, duration=0.1)
                
                print(f"⚠️ 예외 팝업 발견 및 처리: {popup_file}")
                time.sleep(0.5)  # 팝업 닫힌 후 잠시 대기
                return True
                
        except Exception:
            pass
    
    return False

def find_and_click_image(image_path, name, max_attempts=MAX_FIND_ATTEMPTS):
    """이미지를 찾아서 클릭하는 함수"""
    print(f"\n[동작] '{name}' 버튼을 찾습니다...")
    
    for attempt in range(max_attempts):
        # 매 시도마다 예외 팝업 체크
        check_and_close_exception_popups()
        
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
        # 예외 팝업 체크
        check_and_close_exception_popups()
        
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


def run_step(step_num, button_file, screen_file, extra_wait=0):
    """단일 스텝 실행: 버튼 클릭 -> 화면 검증"""
    print(f"\n{'='*60}")
    print(f"📍 STEP {step_num} 시작")
    print(f"{'='*60}")
    
    # 클릭 전 추가 대기 (애니메이션, 로딩 등)
    if extra_wait > 0:
        print(f"⏳ 클릭 전 {extra_wait}초 추가 대기 중...")
        time.sleep(extra_wait)
    
    button_path = os.path.join(SCRIPT_DIR, button_file)
    screen_path = os.path.join(SCRIPT_DIR, screen_file)
    
    # 버튼 클릭
    if not find_and_click_image(button_path, button_file):
        return False
    
    # 화면 검증
    if not verify_screen(screen_path, screen_file):
        return False
    
    return True


# --- 메인 실행 ---

def main():
    print("="*60)
    print("🤖 PyAutoGUI 자동화 스크립트 시작 🤖")
    print("="*60)
    
    # 단계 목록 출력
    for i, step_data in enumerate(STEPS, 1):
        if len(step_data) == 3:
            btn, scr, wait = step_data
            print(f"👉 {i}단계: {btn} 클릭 -> {scr} 확인 (대기: {wait}초)")
        else:
            btn, scr = step_data
            print(f"👉 {i}단계: {btn} 클릭 -> {scr} 확인")
    
    print("="*60)
    
    # 초기 대기
    print(f"\n[초기화] {WAIT_BEFORE_ACTION}초 대기 중...")
    time.sleep(WAIT_BEFORE_ACTION)
    
    # 모든 단계 실행
    for step_num, step_data in enumerate(STEPS, 1):
        # 튜플 언패킹: 2개 또는 3개 요소 처리
        if len(step_data) == 3:
            button_file, screen_file, extra_wait = step_data
        else:
            button_file, screen_file = step_data
            extra_wait = 0
        
        if not run_step(step_num, button_file, screen_file, extra_wait):
            print(f"\n{'='*60}")
            print(f"🚨 STEP {step_num}에서 실패했습니다.")
            print(f"{'='*60}")
            sys.exit(1)
    
    # 완료
    print("\n" + "="*60)
    print(f"✨ 모든 자동화 단계가 성공적으로 완료되었습니다! (총 {len(STEPS)}단계) ✨")
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
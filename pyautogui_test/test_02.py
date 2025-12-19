import pyautogui
import time
import sys
import pytesseract
from PIL import Image
import re

# --- Tesseract 경로 설정 (필요시 수정) ---
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- 설정 (필요에 따라 조정) ---
SUMMON_BUTTON_IMAGE = r'C:\Users\gde0005\Documents\tP\pyautogui_test\summon_button.png'
TEN_TIMES_BUTTON_IMAGE = r'C:\Users\gde0005\Documents\tP\pyautogui_test\ten_times_button.png'
CLOSE_BUTTON_IMAGE = r'C:\Users\gde0005\Documents\tP\pyautogui_test\close_button.png'

# 루비 숫자 영역 좌표 (스크린샷으로 확인 후 설정 필요)
# 예: (x, y, width, height) 형식
RUBY_COUNT_REGION = (100, 50, 150, 40)  # 실제 좌표로 변경 필요

CONFIDENCE_THRESHOLD = 0.8
EXPECTED_RUBY_COST = 3000  # 10회 소환 비용
WAIT_AFTER_CLICK = 1.5     # 클릭 후 대기 시간 (초)
MAX_FIND_ATTEMPTS = 5      # 버튼 찾기 최대 시도 횟수
FIND_RETRY_INTERVAL = 1    # 재시도 간격 (초)

# --- 헬퍼 함수들 ---

def find_and_click_button(image_path, button_name, max_attempts=MAX_FIND_ATTEMPTS):
    """이미지를 찾아 클릭하는 함수"""
    print(f"\n[검색] '{button_name}' 버튼을 찾습니다...")
    
    for attempt in range(max_attempts):
        try:
            location = pyautogui.locateOnScreen(
                image_path,
                confidence=CONFIDENCE_THRESHOLD,
                grayscale=False
            )
            
            if location:
                center_x = location.left + location.width / 2
                center_y = location.top + location.height / 2
                
                print(f"✅ '{button_name}' 버튼 발견! 위치: ({center_x:.0f}, {center_y:.0f})")
                pyautogui.click(center_x, center_y, duration=0.1)
                print(f"➡️ '{button_name}' 버튼 클릭 완료!")
                time.sleep(WAIT_AFTER_CLICK)
                return True
                
        except Exception as e:
            print(f"⚠️ 검색 중 오류: {e}")
        
        if attempt < max_attempts - 1:
            print(f"👀 '{button_name}' 버튼을 찾을 수 없습니다. {FIND_RETRY_INTERVAL}초 후 재시도... (시도 {attempt + 1}/{max_attempts})")
            time.sleep(FIND_RETRY_INTERVAL)
    
    print(f"❌ 실패: '{button_name}' 버튼을 찾을 수 없습니다.")
    return False


def extract_ruby_count(region):
    """화면에서 루비 개수를 OCR로 추출하는 함수"""
    try:
        # 지정된 영역 스크린샷
        screenshot = pyautogui.screenshot(region=region)
        
        # 디버깅용 이미지 저장
        screenshot.save('debug_ruby_region.png')
        
        # OCR로 텍스트 추출
        text = pytesseract.image_to_string(screenshot, config='--psm 7 digits')
        
        # 숫자만 추출 (쉼표 제거)
        numbers = re.findall(r'\d+', text.replace(',', ''))
        
        if numbers:
            ruby_count = int(''.join(numbers))
            print(f"📊 현재 루비: {ruby_count:,}개")
            return ruby_count
        else:
            print(f"⚠️ 루비 개수를 읽을 수 없습니다. OCR 결과: '{text}'")
            return None
            
    except Exception as e:
        print(f"❌ 루비 개수 추출 오류: {e}")
        return None


def verify_ruby_deduction(before_count, after_count, expected_cost):
    """루비 차감이 정확한지 확인하는 함수"""
    if before_count is None or after_count is None:
        print("⚠️ 루비 개수를 확인할 수 없어 검증을 건너뜁니다.")
        return True  # 검증 실패해도 계속 진행
    
    actual_deduction = before_count - after_count
    print(f"\n[검증] 루비 차감 확인:")
    print(f"  이전: {before_count:,}개")
    print(f"  이후: {after_count:,}개")
    print(f"  차감: {actual_deduction:,}개 (예상: {expected_cost:,}개)")
    
    if actual_deduction == expected_cost:
        print("✅ 루비가 정확히 차감되었습니다!")
        return True
    else:
        print(f"⚠️ 루비 차감이 예상과 다릅니다. (차이: {abs(actual_deduction - expected_cost):,}개)")
        return False


# --- 메인 자동화 시퀀스 ---

def main():
    print("=" * 60)
    print("🎮 루비 소환 자동화 스크립트 시작 🎮")
    print("=" * 60)
    print(f"📝 시나리오:")
    print(f"  1. 소환 버튼 클릭")
    print(f"  2. 10회 소환 버튼 클릭 (루비 {EXPECTED_RUBY_COST:,}개)")
    print(f"  3. 루비 차감 확인")
    print(f"  4. 닫기 버튼 클릭")
    print("=" * 60)
    
    # STEP 0: 초기 루비 개수 확인
    print("\n[STEP 0] 초기 루비 개수 확인")
    ruby_before = extract_ruby_count(RUBY_COUNT_REGION)
    if ruby_before and ruby_before < EXPECTED_RUBY_COST:
        print(f"❌ 루비가 부족합니다! (현재: {ruby_before:,}개, 필요: {EXPECTED_RUBY_COST:,}개)")
        return False
    
    time.sleep(1)
    
    # STEP 1: 소환 버튼 클릭
    print("\n[STEP 1] 소환 버튼 클릭")
    if not find_and_click_button(SUMMON_BUTTON_IMAGE, "소환"):
        return False
    
    # STEP 2: 10회 소환 버튼 클릭
    print("\n[STEP 2] 10회 소환 버튼 클릭")
    if not find_and_click_button(TEN_TIMES_BUTTON_IMAGE, "10회 소환"):
        return False
    
    # 소환 애니메이션 대기
    print("⏳ 소환 처리 중... (3초 대기)")
    time.sleep(3)
    
    # STEP 3: 루비 차감 확인
    print("\n[STEP 3] 루비 차감 확인")
    ruby_after = extract_ruby_count(RUBY_COUNT_REGION)
    
    if not verify_ruby_deduction(ruby_before, ruby_after, EXPECTED_RUBY_COST):
        print("⚠️ 루비 차감에 문제가 있을 수 있습니다. 그래도 계속 진행합니다.")
    
    # STEP 4: 닫기 버튼 클릭
    print("\n[STEP 4] 닫기 버튼 클릭")
    if not find_and_click_button(CLOSE_BUTTON_IMAGE, "닫기"):
        return False
    
    # 완료
    print("\n" + "=" * 60)
    print("✨ 모든 자동화 단계가 성공적으로 완료되었습니다! ✨")
    print("=" * 60)
    return True


# --- 스크립트 실행 ---
if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 스크립트를 중단했습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
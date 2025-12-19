import pyautogui
import time
import sys
import os

# --- 설정 ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ⭐ 여기만 수정 ⭐
# 각 단계를 (버튼 이미지, 확인할 화면 이미지, 클릭 전 추가 대기시간) 튜플로 정의
STEPS = [
    ('step1.png', 'step2.png'),
    ('step3.png', 'step4.png'),
    ('step5.png', 'step6.png', 1),
    ('step7.png', 'step8.png'),
]

CONFIDENCE_THRESHOLD = 0.75
WAIT_BEFORE_ACTION = 1
MAX_FIND_ATTEMPTS = 5
FIND_RETRY_INTERVAL = 1
MAX_VERIFY_TIME = 10
VERIFY_CHECK_INTERVAL = 0.5

# -----------------------------------------------------------
# 📸 스크린샷 저장 함수
# -----------------------------------------------------------
def save_screenshot(name):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SCRIPT_DIR, f"screenshot_{name}_{timestamp}.png")
    pyautogui.screenshot(filename)
    print(f"📸 스크린샷 저장됨: {filename}")


# -----------------------------------------------------------
# 버튼 이미지 찾아서 클릭
# -----------------------------------------------------------
def find_and_click_image(image_path, name, max_attempts=MAX_FIND_ATTEMPTS):
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

                # 클릭 위치 계산
                center_x = location.left + location.width / 2
                center_y = location.top + location.height / 2

                pyautogui.click(center_x, center_y, duration=0.1)
                print(f"➡️ '{name}' 클릭 완료! 위치: ({center_x:.0f}, {center_y:.0f})")

                # 📸 클릭 직후 스크린샷 저장
                save_screenshot(f"click_{name}")

                print(f"    화면 전환 대기 ({WAIT_BEFORE_ACTION}초)...")
                time.sleep(WAIT_BEFORE_ACTION)
                return True

        except Exception as e:
            print(f"⚠️ 검색 중 오류: {e}")

        # 재시도 안내
        if attempt < max_attempts - 1:
            print(f"👀 '{name}'을(를) 찾을 수 없습니다. {FIND_RETRY_INTERVAL}초 후 재시도... (시도 {attempt + 1}/{max_attempts})")
            time.sleep(FIND_RETRY_INTERVAL)

    print(f"❌ 실패: '{name}'을(를) {max_attempts}회 시도 후에도 찾을 수 없습니다.")

    # 📸 실패 시 스크린샷 저장
    save_screenshot(f"fail_find_{name}")

    return False


# -----------------------------------------------------------
# 화면 검증
# -----------------------------------------------------------
def verify_screen(image_path, name, max_time=MAX_VERIFY_TIME):
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

                # 📸 검증 성공 스크린샷
                save_screenshot(f"verify_{name}")

                return True

        except Exception:
            pass  # 무시하고 계속 확인

        time.sleep(VERIFY_CHECK_INTERVAL)

    print(f"❌ 실패: '{name}' 화면이 {max_time}초 내에 나타나지 않았습니다.")

    # 📸 검증 실패 스크린샷
    save_screenshot(f"fail_verify_{name}")

    return False


# -----------------------------------------------------------
# 단일 스텝 실행
# -----------------------------------------------------------
def run_step(step_num, button_file, screen_file, extra_wait=0):
    print(f"\n{'='*60}")
    print(f"📍 STEP {step_num} 시작")
    print(f"{'='*60}")

    # 클릭 전 추가 대기
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


# -----------------------------------------------------------
# 메인 실행 함수
# -----------------------------------------------------------
def main():
    print("=" * 60)
    print("🤖 PyAutoGUI 자동화 스크립트 시작 🤖")
    print("=" * 60)

    # 스텝 목록 표시
    for i, step_data in enumerate(STEPS, 1):
        if len(step_data) == 3:
            btn, scr, wait = step_data
            print(f"👉 {i}단계: {btn} 클릭 -> {scr} 확인 (대기: {wait}초)")
        else:
            btn, scr = step_data
            print(f"👉 {i}단계: {btn} 클릭 -> {scr} 확인")

    print("=" * 60)

    # 초기 대기
    print(f"\n[초기화] {WAIT_BEFORE_ACTION}초 대기 중...")
    time.sleep(WAIT_BEFORE_ACTION)

    # 모든 단계 실행
    for step_num, step_data in enumerate(STEPS, 1):
        if len(step_data) == 3:
            button_file, screen_file, extra_wait = step_data
        else:
            button_file, screen_file = step_data
            extra_wait = 0

        if not run_step(step_num, button_file, screen_file, extra_wait):
            print("\n" + "=" * 60)
            print(f"🚨 STEP {step_num}에서 실패했습니다.")
            print("=" * 60)
            sys.exit(1)

    print("\n" + "=" * 60)
    print(f"✨ 모든 자동화 단계가 성공적으로 완료되었습니다! (총 {len(STEPS)}단계) ✨")
    print("=" * 60)


# -----------------------------------------------------------
# 실행
# -----------------------------------------------------------
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

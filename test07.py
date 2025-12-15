import pyautogui
import time
import sys
import os
from datetime import datetime

# ----------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "screenshots")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 로그 파일 생성
log_filename = os.path.join(LOG_DIR, f"run_{time.strftime('%Y%m%d_%H%M%S')}.log")
log_file = open(log_filename, "w", encoding="utf-8")

# ANSI 컬러
C_RESET = "\033[0m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"

# ----------------------------------------------------------------------
# 사용자 설정
# ----------------------------------------------------------------------
STEPS = [
    ('step1.png', 'step2.png'),
    ('step3.png', 'step4.png'),
    ('step5.png', 'step6.png', 1),
    ('step7.png', 'step8.png'),
]

CONFIDENCE_THRESHOLD = 0.7
WAIT_BEFORE_ACTION = 1
MAX_FIND_ATTEMPTS = 5
FIND_RETRY_INTERVAL = 1
MAX_VERIFY_TIME = 10
VERIFY_CHECK_INTERVAL = 0.5
MAX_TOTAL_RETRY = 3


# ----------------------------------------------------------------------
# 안전한 locate 함수 (예외 방지)
# ----------------------------------------------------------------------
def safe_locate(image_path, confidence=0.8, grayscale=False):
    try:
        return pyautogui.locateOnScreen(
            image_path,
            confidence=confidence,
            grayscale=grayscale
        )
    except Exception:
        return None


# ----------------------------------------------------------------------
# 로그 출력 + 파일 기록
# ----------------------------------------------------------------------
def log(msg):
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()


# ----------------------------------------------------------------------
# 📸 스크린샷 저장
# ----------------------------------------------------------------------
def save_screenshot(name):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
    pyautogui.screenshot(filename)
    log(f"{C_CYAN}📸 스크린샷 저장됨: {filename}{C_RESET}")


# ----------------------------------------------------------------------
# 버튼 찾고 클릭
# ----------------------------------------------------------------------
def find_and_click_image(image_path, name):
    log(f"\n{C_MAGENTA}[동작] '{name}' 버튼을 찾습니다...{C_RESET}")

    for attempt in range(MAX_FIND_ATTEMPTS):
        location = safe_locate(
            image_path,
            confidence=CONFIDENCE_THRESHOLD,
            grayscale=False
        )

        if location:
            log(f"{C_GREEN}✅ '{name}' 발견! (시도 {attempt + 1}/{MAX_FIND_ATTEMPTS}){C_RESET}")

            x = location.left + location.width / 2
            y = location.top + location.height / 2

            pyautogui.click(x, y, duration=0.1)
            log(f"{C_GREEN}➡️ '{name}' 클릭 완료! ({int(x)}, {int(y)}){C_RESET}")

            save_screenshot(f"click_{name}")
            time.sleep(WAIT_BEFORE_ACTION)
            return True

        log(
            f"{C_YELLOW}👀 '{name}'을 찾지 못함 → "
            f"{FIND_RETRY_INTERVAL}초 후 재시도 ({attempt + 1}/{MAX_FIND_ATTEMPTS}){C_RESET}"
        )
        time.sleep(FIND_RETRY_INTERVAL)

    log(f"{C_RED}❌ '{name}'을(를) 찾는 데 실패했습니다.{C_RESET}")
    save_screenshot(f"fail_find_{name}")
    return False


# ----------------------------------------------------------------------
# 화면 검증
# ----------------------------------------------------------------------
def verify_screen(image_path, name):
    log(f"\n{C_MAGENTA}[검증] '{name}' 화면을 {MAX_VERIFY_TIME}초 간 확인합니다...{C_RESET}")

    start = time.time()

    while time.time() - start < MAX_VERIFY_TIME:
        found = safe_locate(
            image_path,
            confidence=CONFIDENCE_THRESHOLD,
            grayscale=False
        )

        if found:
            log(f"{C_GREEN}🎉 '{name}' 화면 검증 성공!{C_RESET}")
            save_screenshot(f"verify_{name}")
            return True

        time.sleep(VERIFY_CHECK_INTERVAL)

    log(f"{C_RED}❌ '{name}' 화면이 나타나지 않았습니다.{C_RESET}")
    save_screenshot(f"fail_verify_{name}")
    return False


# ----------------------------------------------------------------------
# 스텝 실행
# ----------------------------------------------------------------------
def run_step(step_num, button_file, screen_file, extra_wait=0):
    log(f"\n{C_CYAN}{'=' * 60}")
    log(f"📍 STEP {step_num} 시작")
    log(f"{'=' * 60}{C_RESET}")

    if extra_wait > 0:
        log(f"{C_YELLOW}⏳ 클릭 전 {extra_wait}초 추가 대기...{C_RESET}")
        time.sleep(extra_wait)

    btn_path = os.path.join(SCRIPT_DIR, button_file)
    scr_path = os.path.join(SCRIPT_DIR, screen_file)

    if not find_and_click_image(btn_path, button_file):
        return False

    if not verify_screen(scr_path, screen_file):
        return False

    return True


# ----------------------------------------------------------------------
# 전체 자동화 루틴
# ----------------------------------------------------------------------
def run_all_steps():
    for n, step_data in enumerate(STEPS, 1):
        if len(step_data) == 3:
            btn, scr, wait = step_data
        else:
            btn, scr = step_data
            wait = 0

        if not run_step(n, btn, scr, wait):
            return False

    return True


# ----------------------------------------------------------------------
# 메인
# ----------------------------------------------------------------------
def main():
    log(f"{C_CYAN}{'=' * 60}")
    log("🤖 PyAutoGUI 자동화 스크립트 시작")
    log(f"{'=' * 60}{C_RESET}")

    start_time = time.time()

    for attempt in range(1, MAX_TOTAL_RETRY + 1):
        log(f"\n{C_MAGENTA}🔄 전체 실행 시도 {attempt}/{MAX_TOTAL_RETRY}{C_RESET}")

        if run_all_steps():
            elapsed = time.time() - start_time
            log(f"\n{C_GREEN}✨ 모든 단계 성공! 총 소요 시간: {elapsed:.2f}초 ✨{C_RESET}")
            return

        log(f"{C_RED}🚨 실패 — 전체 프로세스를 다시 시도합니다.{C_RESET}")
        time.sleep(2)

    log(f"{C_RED}\n❌ 모든 재시도 실패. 자동화 종료.{C_RESET}")
    sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log(f"{C_RED}\n⚠️ 사용자가 스크립트를 종료했습니다.{C_RESET}")
        sys.exit(1)
    except Exception as e:
        log(f"{C_RED}\n❌ 치명적 오류 발생: {e}{C_RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

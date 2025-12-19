import pyautogui
import time
import sys
import os
import csv
import pytesseract
from datetime import datetime
from PIL import Image 

# ----------------------------------------------------------------------
# 🌟 Windows 환경 필수 수정 사항: Tesseract OCR 경로 설정 🌟
# 설치된 tesseract.exe 파일의 정확한 경로로 변경해야 합니다.
# ----------------------------------------------------------------------
try:
    # 윈도우 기본 설치 경로 예시 (본인의 설치 경로에 맞게 수정하세요!)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 
    print("Tesseract 경로 설정 완료.")
except Exception as e:
    print(f"⚠️ Tesseract 경로 설정 시 오류 발생. Tesseract 설치 및 경로를 확인해주세요: {e}")
    # 경로 설정 실패 시 스크립트 실행이 중단되지는 않지만, OCR 기능은 작동하지 않습니다.

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

# 테스트 결과 저장소
TEST_RESULTS = []

# ANSI 컬러 (Windows 터미널에서 호환되지만, 일부 환경에서는 제대로 표시되지 않을 수 있습니다.)
C_RESET = "\033[0m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"

# ----------------------------------------------------------------------
# 사용자 설정 (소환 시나리오로 재구성)
# ----------------------------------------------------------------------
SCENARIO_STEPS = [
    {
        'desc': '로비: 소환 메뉴 진입',
        'action': 'Click',
        'target_img': 'step1.png',      # SUMMON 버튼 이미지
        'verification': '10회',          # OCR 검증: 소환창 내부의 '10회' 텍스트 확인
        'wait': 1
    },
    {
        'desc': '소환창: 10회 소환 버튼 클릭',
        'action': 'Click',
        'target_img': 'step2.png',      # 10회 소환하기 버튼 이미지
        'verification': '결과',          # OCR 검증: 결과 화면에 나타나는 '결과' 또는 '획득' 텍스트
        'wait': 1
    },
    {
        'desc': '결과 화면: 연출 대기 후 확인',
        'action': 'Wait_Only',          # 별도 클릭 없이 화면만 확인 (필요시)
        'target_img': 'step2.png',      # (재사용 가능 혹은 아무 이미지나)
        'verification': '닫기',          # OCR 검증: 결과 화면에 '닫기' 버튼이 뜰 때까지 대기
        'wait': 3                       # 소환 연출 시간을 고려해 여유 있게 대기
    },
    {
        'desc': '결과 화면: 닫기 버튼 클릭',
        'action': 'Click',
        'target_img': 'step3.png',      # '닫기'라고 써진 버튼 이미지
        'verification': 'CLOSE',        # OCR 검증: 다음 팝업에 있을 'CLOSE' 텍스트 확인
        'wait': 1
    },
    {
        'desc': '최종 팝업: CLOSE 버튼 클릭',
        'action': 'Click',
        'target_img': 'step4.png',      # 'CLOSE'라고 써진 버튼 이미지
        'verification': 'SUMMON',       # OCR 검증: 다시 메인 소환 화면으로 왔는지 확인
        'wait': 1
    },
]


CONFIDENCE_THRESHOLD = 0.75
WAIT_BEFORE_ACTION = 1
MAX_FIND_ATTEMPTS = 5
FIND_RETRY_INTERVAL = 1
MAX_VERIFY_TIME = 15
VERIFY_CHECK_INTERVAL = 0.5
MAX_TOTAL_RETRY = 3

# ----------------------------------------------------------------------
# 안전한 locate 함수 (예외 방지) - 원본과 동일
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
# 로그 출력 + 파일 기록 - 원본과 동일
# ----------------------------------------------------------------------
def log(msg):
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()

# ----------------------------------------------------------------------
# 📸 스크린샷 저장 - 원본과 동일
# ----------------------------------------------------------------------
def save_screenshot(name):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
    pyautogui.screenshot(filename)
    log(f"{C_CYAN}📸 스크린샷 저장됨: {filename}{C_RESET}")
    return filename 

# ----------------------------------------------------------------------
# 버튼 찾고 클릭 - 원본과 동일
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
# 화면 검증 (이미지 기반) - 원본과 동일
# ----------------------------------------------------------------------
def verify_screen(image_path, name):
    log(f"\n{C_MAGENTA}[이미지 검증] '{name}' 화면을 {MAX_VERIFY_TIME}초 간 확인합니다...{C_RESET}")

    start = time.time()

    while time.time() - start < MAX_VERIFY_TIME:
        found = safe_locate(
            image_path,
            confidence=CONFIDENCE_THRESHOLD,
            grayscale=False
        )

        if found:
            log(f"{C_GREEN}🎉 '{name}' 화면 검증 성공!{C_RESET}")
            return True

        time.sleep(VERIFY_CHECK_INTERVAL)

    log(f"{C_RED}❌ '{name}' 화면이 나타나지 않았습니다.{C_RESET}")
    save_screenshot(f"fail_verify_{name}")
    return False

# ----------------------------------------------------------------------
# 💬 텍스트 인식 및 검증 (OCR 기반) - 원본과 동일
# ----------------------------------------------------------------------
def ocr_and_verify(expected_text, name, max_time=MAX_VERIFY_TIME):
    log(f"\n{C_MAGENTA}[OCR 검증] '{expected_text}' 텍스트를 {max_time}초 간 확인합니다...{C_RESET}")
    start = time.time()
    
    while time.time() - start < max_time:
        # 현재 화면 캡처
        screenshot = pyautogui.screenshot()
        
        # OCR 수행 (한국어 lang='kor' 사용)
        try:
            # 윈도우 환경에서 Tesseract 경로 설정이 필수!
            recognized_text = pytesseract.image_to_string(screenshot, lang='kor')
        except pytesseract.TesseractNotFoundError:
            log(f"{C_RED}❌ Tesseract OCR 실행 파일을 찾을 수 없습니다. 경로를 확인해주세요.{C_RESET}")
            return False
        except Exception as e:
            log(f"{C_YELLOW}⚠️ OCR 중 오류 발생: {e}{C_RESET}")
            recognized_text = ""
            
        # 텍스트 검증
        if expected_text in recognized_text:
            log(f"{C_GREEN}🎉 텍스트 검증 성공! '{expected_text}' 발견.{C_RESET}")
            log(f"{C_YELLOW}--- 인식된 텍스트 일부 (500자 제한) ---\n{recognized_text[:500]}...\n--------------------------{C_RESET}")
            return True
        
        # 텍스트를 찾지 못했으므로 잠시 대기 후 재시도
        time.sleep(VERIFY_CHECK_INTERVAL)

    log(f"{C_RED}❌ '{expected_text}' 텍스트를 화면에서 찾지 못했습니다.{C_RESET}")
    save_screenshot(f"fail_ocr_verify_{name}")
    return False

# ----------------------------------------------------------------------
# 📋 결과 보고서 생성 (CSV) - 원본과 동일
# ----------------------------------------------------------------------
def generate_report():
    report_filename = os.path.join(LOG_DIR, f"report_{time.strftime('%Y%m%d_%H%M%S')}.csv")
    log(f"\n{C_CYAN}📋 테스트 보고서 생성: {report_filename}{C_RESET}")
    
    header = ['Step No.', '재현 스텝 (설명)', '동작 유형', '타겟 파일', '확인 요소/기대 결과', '결과', '결과 스크린샷 파일명']
    
    # 'utf-8-sig'를 사용하여 엑셀에서 한글이 깨지지 않도록 처리
    with open(report_filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        for result in TEST_RESULTS:
            writer.writerow(result)
            
    log(f"{C_GREEN}✅ 보고서 생성이 완료되었습니다. {report_filename}{C_RESET}")


# ----------------------------------------------------------------------
# 스텝 실행 (개선 버전: 이미지/OCR 검증 및 결과 기록) - 원본과 동일
# ----------------------------------------------------------------------
def run_step_v2(step_num, step_data):
    step_desc = step_data['desc']
    target_img = step_data['target_img']
    verification_target = step_data['verification']
    extra_wait = step_data.get('wait', 0)
    
    log(f"\n{C_CYAN}{'=' * 60}")
    log(f"📍 STEP {step_num}: {step_desc}")
    log(f"{'=' * 60}{C_RESET}")

    if extra_wait > 0:
        log(f"{C_YELLOW}⏳ 클릭 전 {extra_wait}초 추가 대기...{C_RESET}")
        time.sleep(extra_wait)

    btn_path = os.path.join(SCRIPT_DIR, target_img)

    # 1. 동작 (Click)
    is_action_success = find_and_click_image(btn_path, target_img)
    final_result = False
    screenshot_path = ""

    if is_action_success:
        # 2. 검증 (Image Verify 또는 OCR Verify)
        if verification_target.endswith('.png') or verification_target.endswith('.jpg'): 
            # 파일 확장자로 이미지 검증 확인
            scr_path = os.path.join(SCRIPT_DIR, verification_target)
            is_verification_success = verify_screen(scr_path, verification_target)
        else:
            # 텍스트로 OCR 검증
            is_verification_success = ocr_and_verify(verification_target, f"text_verify_{step_num}")
            
        final_result = is_action_success and is_verification_success

    # 최종 스크린샷 저장
    if final_result:
        screenshot_path = save_screenshot(f"step_{step_num}_PASS_{target_img.replace('.png', '')}")
    else:
        # 실패 스크린샷은 이미 find_and_click_image/verify_screen/ocr_and_verify에서 저장됨
        screenshot_path = "FAIL_CHECK_LOGS" 
        
    # 결과 기록
    result_text = "PASS" if final_result else "FAIL"
    TEST_RESULTS.append([
        step_num,
        step_desc,
        step_data.get('action', 'Click'), # 기본값 'Click' 추가
        target_img,
        verification_target,
        result_text,
        os.path.basename(screenshot_path) 
    ])

    if not final_result:
        log(f"{C_RED}🚨 STEP {step_num} 실패: {step_desc}{C_RESET}")
        return False
        
    log(f"{C_GREEN}✨ STEP {step_num} 성공! {C_RESET}")
    return True


# ----------------------------------------------------------------------
# 메인 - 원본과 동일
# ----------------------------------------------------------------------
def main():
    log(f"{C_CYAN}{'=' * 60}")
    log("🤖 PyAutoGUI + OCR 자동화 스크립트 시작")
    log(f"{'=' * 60}{C_RESET}")

    start_time = time.time()

    for attempt in range(1, MAX_TOTAL_RETRY + 1):
        log(f"\n{C_MAGENTA}🔄 전체 실행 시도 {attempt}/{MAX_TOTAL_RETRY}{C_RESET}")

        # TEST_RESULTS 초기화 (재시도 시 새로운 결과만 기록되도록)
        global TEST_RESULTS
        if attempt > 1:
            TEST_RESULTS = [] 

        is_success = True
        for n, step_data in enumerate(SCENARIO_STEPS, 1):
            if not run_step_v2(n, step_data):
                is_success = False
                break
                
        if is_success:
            elapsed = time.time() - start_time
            log(f"\n{C_GREEN}✨ 모든 단계 성공! 총 소요 시간: {elapsed:.2f}초 ✨{C_RESET}")
            generate_report()
            return

        log(f"{C_RED}🚨 실패 — 전체 프로세스를 다시 시도합니다.{C_RESET}")
        time.sleep(2)

    log(f"{C_RED}\n❌ 모든 재시도 실패. 자동화 종료.{C_RESET}")
    generate_report()
    sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log(f"{C_RED}\n⚠️ 사용자가 스크립트를 종료했습니다.{C_RESET}")
        generate_report()
        sys.exit(1)
    except Exception as e:
        log(f"{C_RED}\n❌ 치명적 오류 발생: {e}{C_RESET}")
        import traceback
        traceback.print_exc()
        generate_report()
        sys.exit(1)
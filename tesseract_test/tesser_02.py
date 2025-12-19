import pyautogui
import time
import sys
import os
import csv
import pytesseract
import pygetwindow as gw
from datetime import datetime
from PIL import Image 

# ----------------------------------------------------------------------
# 🌟 필수 설정
# ----------------------------------------------------------------------
# Tesseract 설치 경로 (본인의 경로에 맞게 확인)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ----------------------------------------------------------------------
# 📏 scrcpy 창 영역 자동 인식 함수
# ----------------------------------------------------------------------
def get_game_region():
    """scrcpy 창을 찾아 좌표와 크기를 반환합니다."""
    windows = gw.getWindowsWithTitle('scrcpy')
    if windows:
        win = windows[0]
        if win.isMinimized: win.restore()
        # win.activate() # 필요시 창을 맨 앞으로 가져옴
        
        # 실제 게임 화면은 제목 표시줄(약 30~35px) 아래에 있으므로 y값을 보정합니다.
        # 보정값은 환경에 따라 30~40 사이로 조절하세요.
        return (win.left, win.top + 35, win.width, win.height - 35)
    
    print("⚠️ scrcpy 창을 찾을 수 없습니다! 전체 화면 모드로 동작합니다.")
    return None

# ----------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "screenshots")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = os.path.join(LOG_DIR, f"run_{time.strftime('%Y%m%d_%H%M%S')}.log")
log_file = open(log_filename, "w", encoding="utf-8")

TEST_RESULTS = []

C_RESET, C_GREEN, C_RED, C_YELLOW, C_CYAN, C_MAGENTA = "\033[0m", "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[95m"

# ----------------------------------------------------------------------
# 시나리오 설정 (세로 게임 소환 시나리오)
# ----------------------------------------------------------------------
SCENARIO_STEPS = [
    {
        'desc': '로비: 소환 메뉴 진입',
        'target_img': 'step1.png',      # SUMMON 버튼
        'verification': '10회',          # OCR 확인 문구
        'wait': 1
    },
    {
        'desc': '소환창: 10회 소환 버튼 클릭',
        'target_img': 'step2.png',      # 10회 소환 버튼
        'verification': '결과',          # OCR 확인 문구
        'wait': 1
    },
    {
        'desc': '결과 화면: 연출 대기 후 닫기 클릭',
        'target_img': 'step3.png',      # 닫기 버튼
        'verification': 'CLOSE',        # OCR 확인 문구
        'wait': 4
    },
    {
        'desc': '최종 팝업: CLOSE 버튼 클릭',
        'target_img': 'step4.png',      # CLOSE 버튼
        'verification': 'SUMMON',       # 다시 로비 확인
        'wait': 1
    },
]

# 설정값 (인식률 향상을 위해 하향 조정)
CONFIDENCE_THRESHOLD = 0.65 
WAIT_BEFORE_ACTION = 1
MAX_FIND_ATTEMPTS = 5
MAX_VERIFY_TIME = 15
MAX_TOTAL_RETRY = 3

# ----------------------------------------------------------------------
# 실행 함수들
# ----------------------------------------------------------------------

def log(msg):
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()

def save_screenshot(name, region):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
    pyautogui.screenshot(filename, region=region)
    log(f"{C_CYAN}📸 영역 캡처 저장됨: {os.path.basename(filename)}{C_RESET}")
    return filename

def find_and_click_image(image_path, name):
    log(f"\n{C_MAGENTA}[동작] '{name}' 탐색 시작...{C_RESET}")
    
    for attempt in range(MAX_FIND_ATTEMPTS):
        current_region = get_game_region() # 매번 창 위치 갱신
        try:
            location = pyautogui.locateOnScreen(
                image_path,
                confidence=CONFIDENCE_THRESHOLD,
                region=current_region
            )

            if location:
                log(f"{C_GREEN}✅ '{name}' 발견!{C_RESET}")
                x, y = pyautogui.center(location)
                pyautogui.click(x, y, duration=0.2)
                time.sleep(WAIT_BEFORE_ACTION)
                return True
        except:
            pass
        
        log(f"{C_YELLOW}👀 '{name}' 재시도 ({attempt + 1}/{MAX_FIND_ATTEMPTS}){C_RESET}")
        time.sleep(1)
    return False

def ocr_and_verify(expected_text, name):
    log(f"{C_MAGENTA}[OCR] '{expected_text}' 확인 중...{C_RESET}")
    start = time.time()
    
    while time.time() - start < MAX_VERIFY_TIME:
        current_region = get_game_region()
        try:
            screenshot = pyautogui.screenshot(region=current_region)
            recognized_text = pytesseract.image_to_string(screenshot, lang='kor+eng')
            
            if expected_text.lower() in recognized_text.lower():
                log(f"{C_GREEN}🎉 검증 성공!{C_RESET}")
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def generate_report():
    report_filename = os.path.join(LOG_DIR, f"report_{time.strftime('%Y%m%d_%H%M%S')}.csv")
    header = ['No', '설명', '타겟이미지', '검증문구', '결과', '스크린샷']
    with open(report_filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(TEST_RESULTS)
    log(f"\n{C_GREEN}✅ 보고서 생성 완료!{C_RESET}")

def run_step(num, step):
    log(f"\n{C_CYAN}{'='*50}\n📍 STEP {num}: {step['desc']}\n{'='*50}{C_RESET}")
    if step['wait'] > 0: time.sleep(step['wait'])

    img_path = os.path.join(SCRIPT_DIR, step['target_img'])
    success = find_and_click_image(img_path, step['target_img'])
    
    if success:
        success = ocr_and_verify(step['verification'], step['desc'])
    
    res_text = "PASS" if success else "FAIL"
    current_region = get_game_region()
    shot = save_screenshot(f"Step{num}_{res_text}", current_region)
    
    TEST_RESULTS.append([num, step['desc'], step['target_img'], step['verification'], res_text, os.path.basename(shot)])
    return success

def main():
    log(f"{C_CYAN}🤖 세로 게임 자동화 모드 시작 (scrcpy 추적){C_RESET}")
    for attempt in range(1, MAX_TOTAL_RETRY + 1):
        global TEST_RESULTS
        TEST_RESULTS = []
        log(f"\n{C_MAGENTA}🔄 시도 {attempt}/{MAX_TOTAL_RETRY}{C_RESET}")

        all_pass = True
        for i, step in enumerate(SCENARIO_STEPS, 1):
            if not run_step(i, step):
                all_pass = False
                break
        
        if all_pass:
            log(f"\n{C_GREEN}✨ 시나리오 성공!{C_RESET}")
            generate_report()
            return

    log(f"{C_RED}❌ 실패하여 종료합니다.{C_RESET}")
    generate_report()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log(f"{C_RED}\n⚠️ 중단됨{C_RESET}")
        generate_report()
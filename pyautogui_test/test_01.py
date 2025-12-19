import pyautogui
import time
import sys # 프로그램 종료를 위해 sys 모듈을 임포트합니다.
import os

# --- 설정 (필요에 따라 조정) ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

STEP1_BUTTON_FILENAME = 'step1.png'
STEP2_SCREEN_FILENAME = 'step2.png'
STEP3_BUTTON_FILENAME = 'step3.png'
STEP4_SCREEN_FILENAME = 'step4.png'

STEP1_BUTTON_IMAGE = os.path.join(SCRIPT_DIR, STEP1_BUTTON_FILENAME)
STEP2_SCREEN_IMAGE = os.path.join(SCRIPT_DIR, STEP2_SCREEN_FILENAME)
STEP3_BUTTON_IMAGE = os.path.join(SCRIPT_DIR, STEP3_BUTTON_FILENAME)
STEP4_SCREEN_IMAGE = os.path.join(SCRIPT_DIR, STEP4_SCREEN_FILENAME)

CONFIDENCE_THRESHOLD = 0.8 # 이미지 인식 정확도 (0.7~0.9 사이 권장)
WAIT_BEFORE_ACTION = 1     # scrcpy 창 활성화 등을 위한 초기 대기 시간 (초)
MAX_FIND_ATTEMPTS = 5      # step1 버튼을 찾기 위한 최대 시도 횟수
FIND_RETRY_INTERVAL = 1    # step1 버튼 재시도 간격 (초)
MAX_VERIFY_TIME = 10       # step2 화면을 검증하기 위한 최대 대기 시간 (초)
VERIFY_CHECK_INTERVAL = 0.5# step2 화면 검증 시 재확인 간격 (초)

# --- 시작 메시지 ---
print("=========================================")
print("🤖 PyAutoGUI 자동화 스크립트를 시작합니다 🤖")
print(f"   (전체 경로: {STEP1_BUTTON_IMAGE})") # 경로가 잘 생성되었는지 확인
print("=========================================")

# 1. 초기 대기: scrcpy 창이 완전히 준비될 시간을 줍니다.
print(f"\n[초기화] {WAIT_BEFORE_ACTION}초 대기 중...")
time.sleep(WAIT_BEFORE_ACTION)

# 2. 'step1.png' 버튼 찾기 및 클릭
print(f"\n[STEP 1] '{STEP1_BUTTON_IMAGE}' 버튼을 화면에서 찾습니다...")
step1_button_location = None
for attempt in range(MAX_FIND_ATTEMPTS):
    try:
        step1_button_location = pyautogui.locateOnScreen(
            STEP1_BUTTON_IMAGE, 
            confidence=CONFIDENCE_THRESHOLD,
            grayscale=False # 이미지가 컬러인 경우 False 유지. 흑백인 경우 True로 변경
        )
        if step1_button_location:
            print(f"✅ '{STEP1_BUTTON_IMAGE}' 버튼 발견 (시도 {attempt + 1}/{MAX_FIND_ATTEMPTS})")
            break # 찾았으면 루프 종료
    except Exception as e:
        print(f"⚠️ 이미지 검색 중 오류 발생: {e}")
    
    if not step1_button_location:
        print(f"👀 '{STEP1_BUTTON_IMAGE}' 버튼을 찾을 수 없습니다. {FIND_RETRY_INTERVAL}초 후 재시도... (시도 {attempt + 1}/{MAX_FIND_ATTEMPTS})")
        time.sleep(FIND_RETRY_INTERVAL)

# 'step1.png' 버튼을 찾지 못했다면 스크립트 종료
if not step1_button_location:
    print(f"\n❌ 실패: '{STEP1_BUTTON_IMAGE}' 버튼을 지정된 횟수({MAX_FIND_ATTEMPTS}회) 동안 찾을 수 없습니다.")
    sys.exit(1) # 프로그램 종료

# 3. 'step1.png' 버튼 클릭
try:
    center_x = step1_button_location.left + step1_button_location.width / 2
    center_y = step1_button_location.top + step1_button_location.height / 2
    
    pyautogui.click(center_x, center_y, duration=0.1)
    print(f"➡️ '{STEP1_BUTTON_IMAGE}' 버튼 클릭 완료! 위치: ({center_x:.0f}, {center_y:.0f})")
    print(f"    클릭 후 '{STEP2_SCREEN_IMAGE}' 화면 출력을 위해 {WAIT_BEFORE_ACTION}초 대기...")
    time.sleep(WAIT_BEFORE_ACTION) # 클릭 후 화면 전환을 위한 대기
except Exception as e:
    print(f"\n❌ 실패: '{STEP1_BUTTON_IMAGE}' 버튼 클릭 중 오류 발생: {e}")
    sys.exit(1) # 프로그램 종료

# 4. 'step2.png' 화면 검증
print(f"\n[STEP 2] '{STEP2_SCREEN_IMAGE}' 화면 출력을 최대 {MAX_VERIFY_TIME}초 동안 검증합니다...")
step2_screen_found = False
start_time = time.time()

while time.time() - start_time < MAX_VERIFY_TIME:
    try:
        step2_screen_found = pyautogui.locateOnScreen(
            STEP2_SCREEN_IMAGE, 
            confidence=CONFIDENCE_THRESHOLD,
            grayscale=False
        )
        if step2_screen_found:
            print(f"🎉 성공: '{STEP2_SCREEN_IMAGE}' 화면이 출력되었습니다!")
            break # 찾았으면 루프 종료
    except Exception as e:
        pass 
    
    time.sleep(VERIFY_CHECK_INTERVAL) # 잠시 대기 후 재검색

    print()

# 5. 최종 결과 출력
if step2_screen_found:
    print("\n=========================================")
    print("✨ 모든 자동화 단계가 성공적으로 완료되었습니다! ✨")
    print("=========================================")
else:
    print("\n=========================================")
    print(f"🚨 실패: '{STEP2_SCREEN_IMAGE}' 화면이 지정된 시간({MAX_VERIFY_TIME}초) 내에 나타나지 않았습니다.")
    print("=========================================")
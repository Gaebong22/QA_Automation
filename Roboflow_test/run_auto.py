from roboflow import Roboflow
import cv2
from mss import mss
import numpy as np
import pyautogui

# 1. 로보플로우 접속 설정
# [주의] API_KEY는 본인의 Private API Key를 입력하세요.
API_KEY = "3xlNyu7uLkFOg748EzDk" 
rf = Roboflow(api_key=API_KEY)

# 2. 주소창 정보를 바탕으로 ID 수정
# 워크스페이스: cookingdomdata
# 프로젝트: cookierun-kingdom-qa
# 버전: 3
workspace = rf.workspace("cookingdomdata") 
project = workspace.project("cookierun-kingdom-qa")
model = project.version(1).model 

print("--- [성공] 쿠키런 지능형 자동화 가동 중 ---")
print("멈추려면 터미널 창에서 Ctrl + C를 누르세요.")

with mss() as sct:
    # 주 모니터 전체 화면을 캡처 대상으로 설정합니다.
    monitor = sct.monitors[1] 

    while True:
        # 1) 화면 캡처 및 이미지 변환
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        # MSS의 BGRA 형식을 OpenCV의 BGR 형식으로 변환
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # 2) AI 모델에게 화면 분석 요청 (확신도 50% 이상만 추출)
        predictions = model.predict(img, confidence=50).json()

        # 3) 발견된 아이콘이 있다면 클릭 실행
        if 'predictions' in predictions:
            for res in predictions['predictions']:
                label = res['class'] # 예: 'btn_close'
                x = res['x']         # AI가 찾은 좌표
                y = res['y']
                
                print(f"[{label}] 발견! 좌표 ({x}, {y}) 클릭 시도")
                
                # 마우스 실제 이동 및 클릭
                pyautogui.moveTo(x, y, duration=0.2)
                pyautogui.click()
                
                # 다음 동작 전 2초 대기 (로딩 및 중복 클릭 방지)
                pyautogui.sleep(2) 

        # 실시간 화면을 보고 싶다면 아래 주석을 해제하세요. (성능 저하 가능성 있음)
        # cv2.imshow('AI Vision', img)

        # 'q' 키를 누르면 루프 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
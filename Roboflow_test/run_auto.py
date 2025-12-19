from roboflow import Roboflow
import cv2
from mss import mss
import numpy as np
import pyautogui

# 1. 내 모델 정보 (화면에 보이는 정보 입력)
# API Key는 Settings -> API Keys에서 확인 가능합니다.
API_KEY = "3xlNyu7uLkFOg748EzDk" #private api key 넣기
rf = Roboflow(api_key=API_KEY)
project = rf.workspace().project("cookingdomdata") # 프로젝트 ID
model = project.version(3).model # 화면에 'v3'라고 되어 있어서 3으로 설정

print("--- 쿠키런 자동화 시작 ---")

with mss() as sct:
    monitor = sct.monitors[1] # 주 모니터 화면 전체

    while True:
        # 1) 화면 캡처
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # 2) AI 모델로 아이콘 찾기
        predictions = model.predict(img, confidence=50).json()

        # 3) 찾은 아이콘이 있다면 클릭!
        for res in predictions['predictions']:
            label = res['class']
            x, y = res['x'], res['y']
            
            print(f"[{label}] 발견! 좌표 ({x}, {y}) 클릭 시도")
            
            # 마우스 이동 및 클릭
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click()
            
            # 클릭 후 동작 시간 대기 (게임 로딩 고려)
            pyautogui.sleep(2) 

        # 'q'를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
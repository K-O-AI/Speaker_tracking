import cv2
import requests
import numpy as np
import pyaudio
from io import BytesIO
from PIL import Image
import subprocess
import threading
import time

# 서버 URL 설정
server_url = "http://211.228.170.155:8000/api/yolo/"  # 서버의 URL로 수정

# 웹캠 초기화
cap = cv2.VideoCapture(0)  # 웹캠을 사용할 경우 카메라 번호는 0 또는 1일 수 있음

# record-mic.py 파일을 실행하는 함수
def run_record_mic():
    subprocess.run(["python", "record-mic.py"])

def run_direction():
    subprocess.run(["python", "sound-direction.py"])

direction_thread = threading.Thread(target=run_direction)
direction_thread.start()

# record-mic.py 파일 실행
# record-mic.py를 스레드로 실행
record_mic_thread = threading.Thread(target=run_record_mic)
record_mic_thread.start()

# record-mic.py 파일 실행
while True:
    ret, frame = cap.read()
    if not ret:
        break

    _, img_encoded = cv2.imencode('.jpg', frame)
    img_bytes = img_encoded.tobytes()

    # 오디오 데이터 캡처 및 전송
    response = requests.post(server_url, files={'image': img_bytes})

    # 응답 받은 이미지 처리
    if response.status_code == 200:
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imshow('YOLO Detection', img)
    else:
        print("Error:", response.status_code)

    frame = None

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 웹캠, 오디오 스트림, 창 닫기
cap.release()
cv2.destroyAllWindows()

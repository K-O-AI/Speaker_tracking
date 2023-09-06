# Django views.py

import numpy as np
import cv2
import torch
import speech_recognition as sr
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, HttpResponseServerError

class YoloDetection(APIView):
    custom_model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')
    target_image_size = (640, 480)  # 원하는 이미지 크기로 조절

    def post(self, request):
        try:
            # 받은 이미지 처리
            image = request.FILES.get('image')
            if not image:
                return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            nparr = np.fromstring(image.read(), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # 이미지 크기 조절
            resized_frame = cv2.resize(frame, self.target_image_size)

            # YOLO 객체 감지 실행
            results = self.custom_model(resized_frame)
            annotated_frame = results.render()[0]

            # 음성 데이터 처리
            audio = request.FILES.get('audio')
            if not audio:
                return Response({"error": "No audio provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            recognizer = sr.Recognizer()
            audio_data = sr.AudioFile(audio)
            with audio_data as source:
                audio_text = recognizer.recognize_google(source, language='ko-KR')

            # 결과 이미지와 음성 인식 결과를 반환
            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()

            return Response({"image": frame_bytes, "audio_text": audio_text})

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return HttpResponseServerError(error_message)

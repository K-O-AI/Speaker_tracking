from django.urls import path
from .views import YoloDetection

urlpatterns = [
    path('yolo/', YoloDetection.as_view(), name='yolo-detection'),  # URL 패턴 추가
]

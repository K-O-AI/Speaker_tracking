import pyaudio
import numpy as np
import time
import math
import sys

# 오디오 설정
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44000
CHUNK = 1024
DEVICE_1 = 0
DEVICE_2 = 1
THRESHOLD = 0  # 이 민감도 임계값을 조절하세요
MOVING_AVERAGE_SIZE = 5  # 이동 평균 크기

sound_levels_1 = []  # 장치 1의 소리 레벨 저장
sound_levels_2 = []  # 장치 2의 소리 레벨 저장


def rms(data):
    return math.sqrt(sum(int(x) ** 2 for x in data) / len(data))


def moving_average(values, window_size):
    return np.convolve(values, np.ones(window_size) / window_size, mode='valid')


p = pyaudio.PyAudio()

try:
    # 오디오 스트림 열기
    stream1 = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK,
                     input_device_index=DEVICE_1)
    stream2 = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK,
                     input_device_index=DEVICE_2)
except IOError as e:
    print(f"스트림 열기 중 예외 발생: {e}")
    sys.exit(1)

while True:
    try:
        # 오디오 데이터 읽기
        data1 = stream1.read(CHUNK, exception_on_overflow=False)
        data2 = stream2.read(CHUNK, exception_on_overflow=False)
    except (IOError, OSError) as e:
        print(f"데이터 읽기 중 예외 발생: {e}")
        continue

    audio_data_1 = np.frombuffer(data1, dtype=np.int16)
    audio_data_2 = np.frombuffer(data2, dtype=np.int16)

    sound_level_1 = rms(audio_data_1)
    sound_level_2 = rms(audio_data_2)

    sound_levels_1.append(sound_level_1)
    sound_levels_2.append(sound_level_2)

    if len(sound_levels_1) >= MOVING_AVERAGE_SIZE:
        avg_level_1 = np.mean(moving_average(np.array(sound_levels_1), MOVING_AVERAGE_SIZE) * 10000)
        avg_level_2 = np.mean(moving_average(np.array(sound_levels_2), MOVING_AVERAGE_SIZE) * 10000)

        # 왼쪽 또는 오른쪽으로 이동한 것을 감지하여 출력
        if ((avg_level_1 - avg_level_2) > 30):
            print("왼쪽", avg_level_1)
            print("오른쪽", avg_level_2)
            sys.stdout.write("Left      ")
        if ((avg_level_2 - avg_level_1) > 30):
            print("왼쪽", avg_level_1)
            print("오른쪽", avg_level_2)
            sys.stdout.write("Right     ")
            sys.stdout.flush()
        else:
            print("avg1", avg_level_1)
            print("avg2", avg_level_2)
            sys.stdout.write("중앙")
            sys.stdout.flush()

        sound_levels_1 = sound_levels_1[1:]
        sound_levels_2 = sound_levels_2[1:]

    time.sleep(0.6)

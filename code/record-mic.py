import threading
import tkinter as tk
import speech_recognition as sr

class SpeechRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("음성 인식")
        self.exit_event = threading.Event()

        self.text_output = tk.Text(self.root, wrap=tk.WORD, height=10, width=40)
        self.text_output.pack()

        self.start_button = tk.Button(self.root, text="시작", command=self.start_recognition)
        self.start_button.pack()

        self.quit_button = tk.Button(self.root, text="종료", command=self.quit_app)
        self.quit_button.pack()

        self.audio_lock = threading.Lock()
        self.audio_data = ""
        self.text_thread = None

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            self.text_output.insert(tk.END, "마이크 입력 시작...\n")
            while not self.exit_event.is_set():
                try:
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)  # 타임아웃 및 제한 설정
                    with self.audio_lock:
                        self.audio_data = recognizer.recognize_google(audio, language="ko-KR")
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    self.text_output.insert(tk.END, f"음성 인식 오류: {e}\n")

    def start_text_output(self):
        while not self.exit_event.is_set():
            with self.audio_lock:
                if self.audio_data:
                    self.update_output(self.audio_data)
                    self.audio_data = ""
        
    def start_recognition(self):
        self.start_button.config(state=tk.DISABLED)
        self.recognizer_thread = threading.Thread(target=self.recognize_speech)
        self.recognizer_thread.daemon = True
        self.recognizer_thread.start()

        self.text_thread = threading.Thread(target=self.start_text_output)
        self.text_thread.daemon = True
        self.text_thread.start()

    def quit_app(self):
        self.exit_event.set()
        self.root.quit()

    def update_output(self, text):
        self.text_output.insert(tk.END, f"인식된 텍스트: {text}\n")
        self.text_output.see(tk.END)  # 스크롤링

def main():
    root = tk.Tk()
    app = SpeechRecognitionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

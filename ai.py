import os
import json
import queue
import sounddevice as sd
import vosk
from vosk import Model, KaldiRecognizer
import pyttsx3
import pyautogui
import subprocess
import time
import datetime
import platform
import webbrowser

# ----------- Платформа -----------

SYSTEM = platform.system()
print("Система:", SYSTEM)

# ---------- ГОЛОС ----------

#def speak(text):
 #   print("AI:", text)
 #   subprocess.run(["say", text])

engine = pyttsx3.init()

def speak(text):
    print("AI:", text)

    if SYSTEM == "Darwin":  # Mac
        subprocess.run(["say", text])
    else:  # Windows / Linux
        engine.say(text)
        engine.runAndWait()

# ---------- VOSK МОДЕЛЬ ---------
if SYSTEM == "Darwin":
    model = Model("model")  # папка с моделью
    recognizer = KaldiRecognizer(model, 16000)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
    model_path = os.path.join(BASE_DIR, "model","model")
    vosk_model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(vosk_model, 16000)

audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

# ---------- Открытие программ ----------
def open_app(name):
    if "youtube" in name:
        webbrowser.open("https://youtube.com")

    #elif "google" in name:
    #    webbrowser.open("https://google.com")

    elif "браузер" in name:
        webbrowser.open("https://google.com")

    elif "блокнот" in name:
        if SYSTEM == "Windows":
            os.system("notepad")
        elif SYSTEM == "Darwin":
            os.system("open -a TextEdit")

# ----------- Закрытие приложений ----------

def close_app(app):
    if SYSTEM == "Darwin":
        subprocess.run(["osascript", "-e", f'tell application "{app}" to quit'])

    elif SYSTEM == "Windows":
        os.system(f"taskkill /f /im {app}.exe")

# ---------- КОМАНДЫ ----------

# ----------- Закрытие приложений ----------
#def close_app(app_name):
#    subprocess.run([
#        "osascript",
#        "-e",
#       f'tell application "{app_name}" to quit'
#   ])

def run_command(command):
    print("КОМАНДА ПОЛУЧЕНА:", command)
    

    if "открой браузер" in command or "google" in command:
        speak("Открываю браузер")
        webbrowser.open("https://google.com")
        
    elif "закрой браузер" in command:
        speak("Закрываю браузер")
        if open_app == "Google Chrome":
            close_app("Google Chrome")
        elif open_app == "Yandex":
            close_app("Yandex")

    elif "открой ютуб" in command:
        speak("Открываю ютуб")
        webbrowser.open("https://youtube.com")

    elif "закрой ютуб" in command:
        speak("Закрываю ютуб")
        close_app("YouTude")

    elif "текст" in command:
        text = command.replace("напиши", "")
        pyautogui.write(text)
        speak("Пишу текст")

    elif "сделай скриншот" in command:
            folder = os.path.expanduser("PyAI-main\screenshots")
            os.makedirs(folder, exist_ok=True)

            filename = f"screen_{datetime.datetime.now().strftime('%H-%M-%S')}.png"
            path = os.path.join(folder, filename)
            img = pyautogui.screenshot()
            img.save(path)

            print("Сохраняю в:", path)
            print("Папка существует:", os.path.exists(folder))

            try:
                pyautogui.screenshot(path)
                speak("Скриншот сохранён")
            except Exception as e:
                print("Ошибка скриншота:", e)
                speak("Не удалось сделать скриншот")

    elif "стоп" in command or "выход" in command:
        speak("Выключаюсь")
        exit()

    else:
        pass


# ---------- ЗАПУСК ----------
speak("Ассистент запущен")

with sd.RawInputStream(samplerate=16000, blocksize=8000,
                        dtype='int16', channels=1,
                        callback=callback):

    while True:
        data = audio_queue.get()

        if recognizer.AcceptWaveform(data):  # ✅ Правильно
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()

            if text == "":
                continue  # 👈 ПРОСТО ПРОПУСКАЕМ ТИШИНУ

            print("Ты:", text)
            run_command(text)
            time.sleep(1)
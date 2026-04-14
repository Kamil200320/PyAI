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

# ---------- КОМАНДЫ ----------

def open_installed_app(command):
    apps = {
        "телеграм": {
            "mac": "Telegram",
            "win": "Telegram.exe"
        },
        "дискорд": {
            "mac": "Discord",
            "win": "Discord.exe"
        },
        "сафари": {
            "mac": "Safari",
            "win": None
        },
        "хром": {
            "mac": "Google Chrome",
            "win": "chrome.exe"
        },
        "яндекс": {
            "mac": "Yandex",
            "win": "yandex.exe"
        },
        "spotify": {
            "mac": "Spotify",
            "win": "Spotify.exe"
        
        }
    }

    for key in apps:
        if key in command:
            speak(f"Открываю {key}")

            if SYSTEM == "Darwin":
                subprocess.run(["open", "-a", apps[key]["mac"]])

            elif SYSTEM == "Windows":
                os.system(f"start {apps[key]['win']}")

            return True

    return False

# ----------- Закрытие приложений ----------
def close_app(app_name):
     subprocess.run([
        "osascript",
        "-e",
       f'tell application "{app_name}" to quit'
   ])
     
def close_installed_app(command):
    apps = {
        "телеграм": {
            "mac": "Telegram",
            "win": "Telegram.exe"
        },
        "дискорд": {
            "mac": "Discord",
            "win": "Discord.exe"
        },
        "сафари": {
            "mac": "Safari",
            "win": None
        },
        "хром": {
            "mac": "Google Chrome",
            "win": "chrome.exe"
        },
        "яндекс": {
            "mac": "Yandex",
            "win": "yandex.exe"
        },
        "spotify": {
            "mac": "Spotify",
            "win": "Spotify.exe"
        
        }
    }

    for key in apps:
        if key in command:
            speak(f"Закрываю {key}")

            if SYSTEM == "Darwin":
                #subprocess.run(["open", "-a", apps[key]["mac"]])
                close_app(apps[key]["mac"])

            elif SYSTEM == "Windows":
                os.system(f"close {apps[key]['win']}")

            return True

    return False

#------------ Команды -------------

def run_command(command):
    print("КОМАНДА ПОЛУЧЕНА:", command)

    if "открой ютуб" in command:
        speak("Открываю ютуб")
        webbrowser.open("https://youtube.com")

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

    elif "открой" in command:
        if not open_installed_app(command):
            speak("Не знаю как открыть это")

    elif "закрой" in command:
        if not close_installed_app(command):
            speak("Не знаю как закрыть это")

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
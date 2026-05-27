import whisper
import os
from gtts import gTTS
import tempfile
import time
import pygame

pygame.mixer.init()

whisper_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        whisper_model = whisper.load_model("base")
    return whisper_model

def transcribe(audio_file_path: str) -> str:
    model = get_whisper_model()
    result = model.transcribe(audio_file_path)
    return result["text"].strip()

def speak(text: str) -> None:
    tts = gTTS(text=text, lang='en')
    fd, temp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        tts.save(temp_path)
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
    finally:
        time.sleep(0.5)
        try:
            os.remove(temp_path)
        except:
            pass

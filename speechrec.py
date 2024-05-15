import speech_recognition as sr
import pyttsx3
import langid
from app import getApIresponse
from gtts import gTTS
import os

recognizer = sr.Recognizer()

# Initialize the text-to-speech engineapp.py
engine = pyttsx3.init()

# Get a list of available voices
voices = engine.getProperty('voices')

# Set the desired voice for English and Turkish
english_voice = voices[1].id

# Set properties (optional)
engine.setProperty('rate', 150)  # Speed of speech


def speak(text, language='en'):
    if language == 'tr':
        tts = gTTS(text=text, lang='tr')
        tts.save("temp.mp3")
        os.system("start temp.mp3")  # Adjust the command based on your system
    else:
        engine.setProperty('voice', english_voice)  # Change voice for English
        engine.say(text)
        engine.runAndWait()


while True:
    try:
        with sr.Microphone() as mic:

            print("Listening...")
            audio = recognizer.listen(mic)
            print("Recognizing...")

            # Detect language using langid library
            lang, confidence = langid.classify(recognizer.recognize_google(audio, language='tr'))

            # Set the language for speech recognition
            if lang == 'tr':
                text = recognizer.recognize_google(audio, language='tr-TR')
                lang_for_speech = 'tr'  # Set language for speech synthesis
            else:
                text = recognizer.recognize_google(audio, language='en-US')
                lang_for_speech = 'en'  # Set language for speech synthesis

            print("Recognized:", text)

            speak("Getting the Response", language=lang_for_speech)

            response = getApIresponse(text)
            print(response)

            speak(response, language=lang_for_speech)

    except sr.UnknownValueError:
        print("Could not understand audio.")
        continue
    except sr.RequestError:
        print("Speech recognition request failed. Check your internet connection.")
        break

import speech_recognition as sr
import pyttsx3
import googlesearch
import openai

# Configurer le moteur de synthesise vocale
engine = pyttsx3.init()

# Configurer le moteur de reconnaissance vocale
r = sr.Recognizer()

# Configurer les clés API
openai.api_key = "YOUR_OPENAI_API_KEY"


# Fonction pour parler
def speak(text):
    engine.say(text)
    engine.runAndWait()


# Fonction pour écouter et reconnaître la voix
def listen():
    with sr.Microphone() as source:
        print("Je vous écoute...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="fr-FR")
            print(f"Vous avez dit: {text}")
            return text
        except sr.UnknownValueError:
            speak("Désolé, je name pas comprise ce que vous avez dit.")
        except sr.RequestError as e:
            speak(f"Erreur de service ; {e}")


# Fonction pour rechercher sur Google
def google_search(query):
    search_results = googlesearch.search(query, num_results=3)
    summaries = []
    for result in search_results:
        summaries.append(result.description)
    return "\n".join(summaries)


# Fonction pour poser une question à ChatGPT
def ask_chatgpt(query):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=query,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text


# Boucle principale
while True:
    query = listen()
    if query:
        google_summary = google_search(query)
        chatgpt_response = ask_chatgpt(query)
        result = f"Résumé de Google :\n{google_summary}\n\nRéponse de ChatGPT :\n{chatgpt_response}"
        speak(result)

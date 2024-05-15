import random
import json
import pickle

import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

import numpy as np
import speech_recognition as sr
import pyttsx3
import time

lemmatizer = WordNetLemmatizer()
intents = json.loads(open("intents.json").read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')


def clean_up_sentence(sentence):
	sentence_words = nltk.word_tokenize(sentence)
	sentence_words = [lemmatizer.lemmatize(word)
					for word in sentence_words]

	return sentence_words


def bag_of_words(sentence):
	sentence_words = clean_up_sentence(sentence)
	bag = [0] * len(words)

	for w in sentence_words:
		for i, word in enumerate(words):
			if word == w:
				bag[i] = 1
	return np.array(bag)


def predict_class(sentence):
	bow = bag_of_words(sentence)
	res = model.predict(np.array([bow]))[0]

	ERROR_THRESHOLD = 0.25

	results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

	results.sort(key=lambda x: x[1], reverse=True)

	return_list = []

	for r in results:
		return_list.append({'intent': classes[r[0]],
							'probability': str(r[1])})
	return return_list


def get_response(intents_list, intents_json):
	tag = intents_list[0]['intent']
	list_of_intents = intents_json['intents']

	result = ''

	for i in list_of_intents:
		if i['tag'] == tag:
			result = random.choice(i['responses'])
			break
	return result


# This function will take the voice input converted
# into string as input and predict and return the result in both
# text as well as voice format.
def calling_the_bot(txt):
	global res
	predict = predict_class(txt)
	res = get_response(predict, intents)

	engine.say("Found it. From our Database we found that" + res)
	# engine.say(res)
	engine.runAndWait()
	print("Your Symptom was : ", text)
	print("Result found in our Database : ", res)


if __name__ == '__main__':
	print("Bot is Running")

	recognizer = sr.Recognizer()
	mic = sr.Microphone()

	engine = pyttsx3.init()
	rate = engine.getProperty('rate')

	# Increase the rate of the bot according to need,
	# Faster the rate, faster it will speak, vice versa for slower.

	engine.setProperty('rate', 175)

	# Increase or decrease the bot's volume
	volume = engine.getProperty('volume')
	engine.setProperty('volume', 1.0)

	voices = engine.getProperty('voices')

	"""User Might Skip the following Part till the start of While Loop"""
	engine.say(
		"Hello user, I am Bagley, your personal Talking Healthcare Chatbot.")
	engine.runAndWait()

	engine.say(
		"IF YOU WANT TO CONTINUE WITH MALE VOICE PLEASE\
		SAY MALE. OTHERWISE SAY FEMALE.")
	engine.runAndWait()

	# Asking for the MALE or FEMALE voice.
	with mic as source:
		recognizer.adjust_for_ambient_noise(source, duration=0.2)
		audio = recognizer.listen(source)

	audio = recognizer.recognize_google(audio)

	# If the user says Female then the bot will speak in female voice.
	if audio == "Female".lower():
		engine.setProperty('voice', voices[1].id)
		print("You have chosen to continue with Female Voice")
	else:
		engine.setProperty('voice', voices[0].id)
		print("You have chosen to continue with Male Voice")

	"""User might skip till HERE"""

	while True or final.lower() == 'True':
		with mic as symptom:
			print("Say Your Symptoms. The Bot is Listening")
			engine.say("You may tell me your symptoms now. I am listening")
			engine.runAndWait()
			try:
				recognizer.adjust_for_ambient_noise(symptom, duration=0.2)
				symp = recognizer.listen(symptom)
				text = recognizer.recognize_google(symp)
				engine.say("You said {}".format(text))
				engine.runAndWait()

				engine.say(
					"Scanning our database for your symptom. Please wait.")
				engine.runAndWait()

				time.sleep(1)

				# Calling the function by passing the voice inputted
				# symptoms converted into string
				calling_the_bot(text)
			except sr.UnknownValueError:
				engine.say(
					"Sorry, Either your symptom is unclear to me or it is\
					not present in our database. Please Try Again.")
				engine.runAndWait()
				print(
					"Sorry, Either your symptom is unclear to me or it is\
					not present in our database. Please Try Again.")
			finally:
				engine.say(
					"If you want to continue please say True otherwise say\
					False.")
				engine.runAndWait()

		with mic as ans:
			recognizer.adjust_for_ambient_noise(ans, duration=0.2)
			voice = recognizer.listen(ans)
			final = recognizer.recognize_google(voice)

		if final.lower() == 'no' or final.lower() == 'please exit':
			engine.say("Thank You. Shutting Down now.")
			engine.runAndWait()
			print("Bot has been stopped by the user")
			exit(0)

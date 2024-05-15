import os

import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

load_dotenv()

messages = []

user_profiles = {}
app = Flask(__name__, template_folder='templates')
client = OpenAI(api_key="sk-proj-5rmX44MiNWqdfDe9ZmVtT3BlbkFJjc1GbCRZOG3cVaLiCRQS")
openai.api_key ="sk-proj-5rmX44MiNWqdfDe9ZmVtT3BlbkFJjc1GbCRZOG3cVaLiCRQS" # os.getenv("OPEN_API_KEY")


print(openai.api_key)


def getApIresponse(input_text):
    openai.api_key ="sk-proj-5rmX44MiNWqdfDe9ZmVtT3BlbkFJjc1GbCRZOG3cVaLiCRQS"
    messages.append({"role": "user", "content": input_text})
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


def train_classifier():
    data = [
        {"input": "Greeting", "level": "new"},
        {"input": "Common cold symptoms", "level": "beginner"},
        {"input": "Understanding diabetes", "level": "intermediate"},
        {"input": "Signs of heart disease", "level": "intermediate"},
        {"input": "Preventing respiratory infections", "level": "beginner"},
        {"input": "Symptoms of influenza", "level": "intermediate"},
        {"input": "Risk factors for cancer", "level": "intermediate"},
        {"input": "Managing allergies", "level": "beginner"},
        {"input": "Recognizing mental health disorders", "level": "intermediate"},
        {"input": "Exploring autoimmune diseases", "level": "advanced"},
        {"input": "Understanding digestive disorders", "level": "intermediate"},
        {"input": "Preventing cardiovascular diseases", "level": "intermediate"},
        {"input": "Common skin conditions", "level": "beginner"},
        {"input": "Signs of hormonal imbalances", "level": "intermediate"},
        {"input": "Coping with chronic pain", "level": "advanced"},
        {"input": "Early detection of infectious diseases", "level": "intermediate"},
        {"input": "Importance of vaccinations", "level": "beginner"},
        {"input": "Managing mental health challenges", "level": "intermediate"},
        {"input": "Exploring neurological disorders", "level": "advanced"},
        {"input": "Recognizing symptoms of common infections", "level": "beginner"},
        {"input": "Caring for individuals with chronic conditions", "level": "advanced"},
        {"input": "Understanding genetic disorders", "level": "advanced"},
        # Add more health care-related examples based on your actual data
    ]

    # Split data into training and testing sets
    X = [item["input"] for item in data]
    y = [item["level"] for item in data]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a pipeline with CountVectorizer and RandomForestClassifier
    classifier = Pipeline([
        ('vectorizer', CountVectorizer()),
        ('classifier', RandomForestClassifier(random_state=42)),
    ])

    # Train the classifier
    classifier.fit(X_train, y_train)

    # Test the classifier accuracy
    y_pred = classifier.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Classifier Accuracy: {accuracy}")

    return classifier


class Chatbot:
    def __init__(self):
        self.user_levels = {"new": 0, "occasional": 5, "frequent": 10}
        self.user_level = "new"
        self.interactions_count = 0
        self.classifier = train_classifier()
        self.messages = []
        self.user_profile = {}

    def detect_user_level_ml(self, user_input):
        # Use the trained classifier to predict the user level
        predicted_level = self.classifier.predict([user_input])[0]
        self.user_level = predicted_level
        return predicted_level

    def process_user_input(self, input_text):
        # Process user input here
        self.interactions_count += 1

        # Update user level based on interactions
        self.detect_user_level_ml(input_text)

    def generate_response(self, user_id, input_text, knowledge_level):
        if user_id not in self.user_profile:
            self.user_profile[user_id] = {"knowledge_level": knowledge_level, "interactions": []}
        user_profile = self.user_profile[user_id]
        # use self.messages instead of local messages
        self.messages = [{"role": "user", "content": input_text},
                         {"role": "user", "content": f"I am a {knowledge_level}."}]
        if knowledge_level == "beginner":
            self.messages.append({"role": "assistant", "content": "I'll provide answers suitable for beginners."})
            # Add logic for beginner-level responses
        elif knowledge_level == "intermediate":
            self.messages.append(
                {"role": "assistant", "content": "I'll provide answers suitable for intermediate knowledge."})
            # Add logic for intermediate-level responses
        elif knowledge_level == "advanced":
            self.messages.append({"role": "assistant", "content": "I'll provide advanced-level answers."})
            # Add logic for advanced-level responses

        chatbot = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=self.messages
        )
        reply = chatbot.choices[0].message.content

        self.messages.append({"role": "assistant", "content": reply})
        user_profile["interactions"].append({"input": input_text, "output": reply})
        ######################## FEED BACK ##############################
        feedBack = user_profiles.get(user_id, {}).get("feedback", None)
        if feedBack is not None:
            if feedBack == "too_easy":
                'advanced'
            elif feedBack == "too_hard":
                pass
            else:
                pass
            if feedBack in user_profiles[user_id]:
                del user_profiles[user_id][feedBack]
        else:
            print('no feedback provided')

        return reply


chatbot_instance = Chatbot()


@app.route('/')
def home():
    # render the index.html template
    return render_template('index.html', messages=messages)


# the chat is responsible for processing the user's input and generating a response
@app.route('/chatbot', methods=['POST'])
def chat():
    input_text = request.form['message']
    knowledge_level = request.form.get('knowledge_level', 'beginner')
    user_id = request.form.get('user_id')

    # Pass the knowledge_level and user_id to generate_response()
    response = chatbot_instance.generate_response(user_id, input_text, knowledge_level)

    return jsonify(output=response)


# Add a new route for handling feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    user_id = request.form.get('user_id')
    feedBack = request.form.get('feedback')

    # Store the feedback in the user's profile or interaction history
    user_profiles[user_id]["feedback"] = feedBack

    # You can add additional logic based on feedback if needed

    return jsonify(success=True)


# run the app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

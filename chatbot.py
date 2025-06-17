import json
import re
from pdf_generator import generate_pdf  # Correct import
import random
import os
import datetime

expecting_pdf_text = False

def load_intents(file_path="intents.jsonl"):
    intents = []
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    intents.append(json.loads(line))
        return intents
    except json.JSONDecodeError as e:
        print(f"JSON error in intents file: {e}")
        return []

def preprocess_text(text):
    text = text.lower()
    return re.sub(r'[^\w\s]', '', text)

def get_response(user_input, intents):
    global expecting_pdf_text

    preprocessed_input = preprocess_text(user_input)

    if expecting_pdf_text:
        expecting_pdf_text = False
        return "PDF created successfully!"

    for intent in intents:
        for pattern in intent["patterns"]:
            if re.search(r'\b' + re.escape(preprocess_text(pattern)) + r'\b', preprocessed_input):
                if intent["tag"] == "create_pdf_request":
                    expecting_pdf_text = True
                return random.choice(intent["responses"])

    return "I'm not sure how to respond to that."

def chat():
    intents = load_intents()
    if not intents:
        print("Chotu: Cannot start without intents.")
        return

    print("Chotu: Hi! I'm Chotu. Type 'exit' to end. Say 'create pdf' to begin.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chotu: Goodbye!")
            break

        response = get_response(user_input, intents)
        print(f"Chotu: {response}")

if __name__ == "__main__":
    chat()

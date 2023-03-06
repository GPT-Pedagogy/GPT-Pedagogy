from flask import Flask, render_template, request
import json
from Chat import Chat
app = Flask(__name__)
chat = Chat("0000")
lessons = {"lessons": None}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/lessons', methods=['GET'])
def get_lessons():

    if not lessons["lessons"]:
        with open("data/lessons.json", "r") as file:
            lessons["lessons"] = json.loads(file.read())
    tmp = lessons["lessons"].copy()
    for lesson in tmp:
        for question in lesson["quiz"]:
            question.pop("a")

    return tmp


@app.route('/input', methods=['POST'])
def get_input():
    input_text = request.json["inputText"]
    print("Input text", input_text)
    chat.submit(input_text)
    resp = chat.generate()
    return {"content": resp}


@app.route('/evaluate', methods=['POST'])
def evaluate_answer():
    input_text = request.json["inputText"]
    print("Input text", input_text)
    chat.submit(input_text)
    resp = chat.generate()
    return {"content": resp}


if __name__ == '__main__':
    app.run()

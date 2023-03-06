from flask import Flask, render_template, request
import json
import copy
from Chat import Chat
app = Flask(__name__)
chat = Chat("0000")
LESSONS = {}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/lessons', methods=['GET'])
def get_lessons():

    if not len(LESSONS):
        with open("data/lessons.json", "r") as file:
            tmp_lessons = json.loads(file.read())
        for lesson in tmp_lessons:
            LESSONS[lesson["id"]] = lesson

    tmp = copy.deepcopy(LESSONS)
    for lesson in tmp.values():
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
    answered_quiz = request.json
    feedback = {}
    for qId, question in enumerate(answered_quiz["quiz"]):
        if question["selected"] == str(LESSONS[answered_quiz["lessonId"]]["quiz"][qId]["a"]):
            feedback[qId] = "Repic"
        else:
            feedback[qId] = "Not repic"

    print("Quiz", answered_quiz)
    return {"content": feedback}


if __name__ == '__main__':
    app.run()

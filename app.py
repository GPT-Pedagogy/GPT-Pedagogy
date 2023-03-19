from flask import Flask, render_template, request
import json
import copy
from Teacher import Teacher
app = Flask(__name__)
teacher = Teacher("000")
teacher.set_model("text-davinci-003", "text-davinci-003", "text-davinci-003")
LESSONS = {}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/lessons', methods=['GET'])
def get_lessons():
    """Returns lesson information to the front end"""

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
    """Takes in user input and passes it off to the chat"""

    input_text = request.json["inputText"]
    print("Input text", input_text)
    teacher.chat.submit(input_text)
    resp = teacher.chat.generate()
    return {"content": resp}


@app.route('/evaluate', methods=['POST'])
def evaluate_lesson():
    """Evaluates the submitted user information for a lesson"""

    answered_quiz = request.json
    feedback = {}
    for qId, question in enumerate(answered_quiz["quiz"]):
        if LESSONS[answered_quiz["lessonId"]]["quiz"][qId]["type"] == "mc":
            if question["response"] == str(LESSONS[answered_quiz["lessonId"]]["quiz"][qId]["a"]):
                feedback[qId] = "Correct"
            else:
                feedback[qId] = "Incorrect"
        if LESSONS[answered_quiz["lessonId"]]["quiz"][qId]["type"] == "sa":
            ques, resp = LESSONS[answered_quiz["lessonId"]]["quiz"][qId]["q"], question["response"]
            feedback[qId] = teacher.evaluate.eval_short_answer(ques, resp)
            feedback[qId] += "\n"+teacher.evaluate.correct_short_answer(ques, resp)

    print("Quiz", answered_quiz)
    return {"content": feedback}


if __name__ == '__main__':
    app.run()

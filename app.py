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

    tmp = copy.deepcopy(LESSONS["content"])
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
        if LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["type"] == "mc":
            if question["response"] == str(LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["a"]):
                feedback[qId] = "Correct"
            else:
                feedback[qId] = "Incorrect"
        if LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["type"] == "sa":
            ques, resp = LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["q"], question["response"]
            feedback[qId] = teacher.evaluate.eval_short_answer(ques, resp)
            feedback[qId] += "\n"+teacher.evaluate.correct_short_answer(ques, resp)

    print("Quiz", answered_quiz)
    return {"content": feedback}


@app.route('/quiz_candidates', methods=['GET'])
def get_quiz_candidates():
    """Returns several candidate quizzes to be manually reviewed"""

    try:
        batch_num = int(request.args["b"])
        lesson_ids = request.args.get("l", "").split(",")
    except Exception:
        return "Missing or malformed b[int] argument"

    if lesson_ids:
        print(f"Limiting to lessons: {lesson_ids}")

    batches = []
    while len(batches) < batch_num:
        candidates = []
        for lesson in LESSONS["content"]:
            if lesson["id"] not in lesson_ids:
                continue

            # Retrieve question types for quiz
            composition = lesson["quiz_composition"] if lesson.get("quiz_composition") else LESSONS["quiz_composition"]
            quiz = {"lesson_id": lesson["id"], "quiz": teacher.gen_quiz(lesson["core_topics"], composition, randomize=True)}
            candidates.append(quiz)
        batches.append(candidates)

    return batches


@app.route('/modify_quiz_plan', methods=['POST'])
def select_generated_question():
    """Edits the quizzes in the lesson plan after human filtering"""

    # Get added or removed questions
    mods = request.json["mods"]
    # Remove questions first to avoid order corruption
    for question in mods:
        if question["op"] == "rem":
            LESSONS["content"][question["lesson_id"]]["quiz"].pop(question["id"])

    for question in mods:
        if question["op"] == "add":
            LESSONS["content"][question["lesson_id"]]["quiz"].append(question)

    with open("data/lessons.json", "w") as file:
        file.write(json.dumps(LESSONS))


if __name__ == '__main__':
    with open("data/lessons.json", "r") as file:
        LESSONS = json.loads(file.read())

    for lesson in LESSONS["content"]:
        if not LESSONS["content"][lesson].get("id"):
            LESSONS["content"][lesson]["id"] = lesson

    app.run()

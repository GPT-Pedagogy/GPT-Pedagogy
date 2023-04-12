from flask import Flask, render_template, request
import json
import copy
from Teacher import Teacher
app = Flask(__name__)
teacher = Teacher("000")
teacher.set_model("text-davinci-003", "text-davinci-003", "text-davinci-003")
LESSONS = {}
ADMIN_ROLE = 1
STUDENT_ROLE = 0

def get_lessons_base(role: int):
    """Returns lesson information to the front end, taking out the answers if requested by a student

    :param role: The role of the user, either admin or student"""

    tmp = copy.deepcopy(LESSONS["content"])
    if role == STUDENT_ROLE:
        for lesson in tmp.values():
            for question in lesson["quiz"]:
                question.pop("a")
    return tmp


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/lessons', methods=['GET'])
def get_lessons_student():
    """Returns lesson information to the front end for students"""

    return get_lessons_base(STUDENT_ROLE)


@app.route('/admin/lessons', methods=['GET'])
def get_lessons_admin():
    """Returns lesson information to the front end for administrators"""

    return get_lessons_base(ADMIN_ROLE)


@app.route('/admin/grades', methods=['GET'])
def request_grades():
    """Returns the grade information from students"""

    # TODO: Get grade information from students
    return {"grades": "not implemented!"}


@app.route('/input', methods=['POST'])
def get_input():
    """Takes in user input and passes it off to the chat"""

    input_text = request.json["inputText"]
    print("Input text", input_text)
    teacher.chat.submit(input_text)
    resp = teacher.chat.generate()
    return {"content": resp}


@app.route('/save_lessons', methods=['POST'])
def save_lessons():
    """Takes in updated lessons as input and saves them to disk"""

    tmp_content = LESSONS["content"]
    try:
        LESSONS["content"] = request.json
        with open("data/lessons.json", "w") as lesson_file:
            lesson_file.write(json.dumps(LESSONS))
    except Exception:
        LESSONS["content"] = tmp_content
        return {"success": False}
    return {"success": True}


@app.route('/evaluate', methods=['POST'])
def evaluate_lesson():
    """Evaluates the submitted user information for a lesson"""

    answered_quiz = request.json
    feedback = {}
    for qId, question in enumerate(answered_quiz["quiz"]):
        # Multiple choice evaluation
        if LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["type"] == "mc":
            choices = LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["choices"]
            answer_idx = LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["a"]
            if question["response"] == str(answer_idx):
                feedback[qId] = "Correct!"
            else:
                feedback[qId] = f"Incorrect, the correct answer was '{choices[answer_idx]}'"

        # Short answer evaluation
        if LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["type"] == "sa":
            ques, resp = LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["q"], question["response"]
            feedback[qId] = teacher.evaluate.eval_short_answer(ques, resp)
            feedback[qId] += "\n"+teacher.evaluate.correct_short_answer(ques, resp)

    print("Quiz", answered_quiz)
    return {"content": feedback}


@app.route('/generate_questions', methods=['GET'])
def generate_questions():
    """Returns several candidate quizzes to be manually reviewed"""

    #return """
    #{"1.1":{"lesson_id":"1.1","quiz":[{"a":4,"choices":["Fruit Chill","Fire Wave","Bubble Blast","Frost Byte","Fruit Chill"],"q":"Q: What is the flavor of 5 Gum's latest taste sensation?","type":"mc"},{"a":2,"choices":["35 m/s","0 m/s","11 m/s","72 m/s"],"q":"Q: The average airspeed velocity of an unladen European swallow is:","type":"mc"},{"a":"Answer: A woodchuck can chuck around 35 cubic feet of wood in a day.","q":"Question: How much wood can a woodchuck chuck?","type":"sa"}]}}"""
    try:
        lesson_ids = json.loads(request.args.get("l", "[]"))
        custom_comps = json.loads(request.args.get("c", "{}"))
    except Exception:
        return "Malformed arguments"

    if lesson_ids:
        print(f"Limiting to lessons: {lesson_ids}")

    candidates = {}
    for lesson_id in LESSONS["content"]:
        lesson = LESSONS["content"][lesson_id]
        if lesson_ids and lesson["id"] not in lesson_ids:
            continue
        # Retrieve question types for quiz
        if not custom_comps.get(lesson_id):
            composition = lesson["quiz_composition"] if lesson.get("quiz_composition") else LESSONS["quiz_composition"]
        else:
            composition = custom_comps.get(lesson_id)

        quiz = {"lesson_id": lesson_id, "quiz": teacher.gen_quiz_questions(lesson["core_topics"], composition, randomize=True)}
        candidates[lesson_id] = quiz

    return candidates


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

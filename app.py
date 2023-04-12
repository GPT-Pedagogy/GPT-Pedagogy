from flask import Flask, render_template, request, send_file
import json
import copy
import pandas as pd
from Teacher import Teacher
from database import connection, generate_performance


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
    df = generate_performance.generate_performance()
    filename = "students_performance.xlsx"
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    # Return the file as a download to the user
    return send_file(filename, as_attachment=True)

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
    print("Evaluating quiz:", answered_quiz)
    
    evaluation = {}
    for qId, question in enumerate(answered_quiz["quiz"]):
        ques, resp = None, None
        evaluation[qId] = {"feedback": "", "score": 0}
        # Multiple choice preparation
        if LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["type"] == "mc":
            choices = LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["choices"]
            answer_idx = LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["a"]
            ques, resp = LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["q"], choices[int(question["response"])]

            evaluation[qId]["feedback"] = f"The correct answer was '{choices[answer_idx]}'"
            if question["response"] == str(answer_idx):
                evaluation[qId]["score"] = 1
            else:
                evaluation[qId]["score"] = 0

        # Short answer preparation
        elif LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["type"] == "sa":
            ques, resp = LESSONS["content"][answered_quiz["lessonId"]]["quiz"][qId]["q"], question["response"]
            evaluation[qId]["feedback"] = f"The correct answer was '{LESSONS['content'][answered_quiz['lessonId']]['quiz'][qId]['a']}'"
            evaluation[qId]["score"] = teacher.evaluate.eval_short_answer(ques, resp)/100

        if evaluation[qId]["score"] < 1:
            evaluation[qId]["feedback"] += "\nCorrection: "+teacher.evaluate.correct_answer(ques, resp)

        
    rcs_id = answered_quiz["rcs_id"]
    lessonID = answered_quiz['lessonId']
    topic = "Lesson " + lessonID

    data = {}
    for qId, question in enumerate(answered_quiz["quiz"]):
        data[qId] = "Question " + str(qId) + ': '+question['core_topic']

    performance_data = {}
    for id, answer in enumerate(evaluation):
        if evaluation[answer]['score'] == 1:
            performance_data[data[id]] = "Score: 100% " + evaluation[answer]['feedback'] 
        else:
            performance_data[data[id]] = "Score: 0%; Feedback: " + evaluation[answer]['feedback'] 
    
    connection.update_performance(rcs_id, topic, performance_data)

    return {"content": evaluation}


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

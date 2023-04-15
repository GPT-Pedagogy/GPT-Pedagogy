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
    """Returns lesson information to the front end, withholding the answers if requested by a student

    :param role: The role of the user, either admin or student
    :return: The dictionary of lessons"""

    tmp = copy.deepcopy(LESSONS["content"])
    if role == STUDENT_ROLE:
        for lesson in tmp.values():
            for question in lesson["quiz"]:
                question.pop("a")
    return tmp


@app.route('/')
def home():
    """Serves the home page for the website

    :return: The website homepage"""

    return render_template('index.html')


@app.route('/admin')
def admin():
    """Serves the admin page for the website

    :return: The website admin page"""

    return render_template('admin.html')


@app.route('/lessons', methods=['GET'])
def get_lessons_student():
    """Returns lesson information to the front end for students

    :return: A dictionary of lessons with quizzes, censored for students"""

    return get_lessons_base(STUDENT_ROLE)


@app.route('/admin/lessons', methods=['GET'])
def get_lessons_admin():
    """Returns lesson information to the front end for administrators

    :return: A dictionary of lessons with quizzes, without censorship"""

    return get_lessons_base(ADMIN_ROLE)


@app.route('/admin/grades', methods=['GET'])
def request_grades():
    """Returns the grade information from students

    :return: A dictionary of grades from students"""

    # TODO: Get grade information from students
    return {"grades": "not implemented!"}


@app.route('/input', methods=['POST'])
def get_input():
    """Takes in user input and passes it off to the chat

    **JSON Data**

    * inputText (str) - Chat inputted from a student

    :return: The response to the student chat from GPT"""


    input_text = request.json["inputText"]
    print("Input text", input_text)
    teacher.chat.submit(input_text)
    resp = teacher.chat.generate()
    return {"content": resp}


@app.route('/save_lessons', methods=['POST'])
def save_lessons():
    """Takes in updated lessons as input and saves them to disk

    **JSON Data**

    * updatedLessons (dict) - A dictionary of lessons with quizzes to overwrite the previous lessons

    :return: A dictionary containing a boolean success value"""

    tmp_content = LESSONS["content"]
    try:
        LESSONS["content"] = request.json["updatedLessons"]
        with open("data/lessons.json", "w") as lesson_file:
            lesson_file.write(json.dumps(LESSONS))
    except Exception:
        LESSONS["content"] = tmp_content
        return {"success": False}
    return {"success": True}


@app.route('/evaluate', methods=['POST'])
def evaluate_lesson():
    """Evaluates the submitted user quiz for a lesson

    **JSON Data**

    * rcsId (str) - The RCS id of the student that submitted this quiz
    * lessonId (str) - The id of the lesson that this quiz belongs to
    * quiz (dict) - A dictionary representing the quiz that the student has sent in

    :return: The automatic evaluation and feedback from GPT"""

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
    # TODO: Add evaluation to database for student

    return {"content": evaluation}


@app.route('/generate_questions', methods=['GET'])
def generate_questions():
    """Returns several candidate quizzes to be manually reviewed

    **Optional Query Params**

    * l (list) - A list of lesson ids to generate the questions for
    * c (dict) - A dictionary, with the lesson id as the key, containing the composition of the questions for that lesson

    :return: A dictionary containing the generated transactions"""

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


if __name__ == '__main__':
    with open("data/lessons.json", "r") as file:
        LESSONS = json.loads(file.read())

    for lesson in LESSONS["content"]:
        if not LESSONS["content"][lesson].get("id"):
            LESSONS["content"][lesson]["id"] = lesson

    app.run()

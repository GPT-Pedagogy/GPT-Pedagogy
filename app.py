from flask import Flask, render_template, request, send_file
import json
import copy
import pandas as pd
from model.Teacher import Teacher
from database import connection, generate_performance


ADMIN_ROLE = 1
STUDENT_ROLE = 0

app = Flask(__name__)
lessons = {}


def get_lessons_base(role: int):
    """Returns lesson information to the front end, withholding the answers if requested by a student

    :param role: The role of the user, either admin or student
    :return: The dictionary of lessons"""

    tmp = copy.deepcopy(lessons["content"])
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

    df = generate_performance.generate_performance()

    """filename = "students_performance.xlsx"
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)"""

    # Return the file as a download to the user
    # return {"grades": df.to_csv()}

    '''xlsx format'''
    # filename = "students_performance.xlsx"
    # with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    #     df.to_excel(writer, sheet_name='Sheet1', index=False)
    # # Return the file as a download to the user
    # return send_file(filename, as_attachment=True)

    filename = "students_performance.csv"
    # Create a temporary file to store the CSV data
    temp_file = filename
    df.to_csv(temp_file, index=False)

    # Use Flask's send_file function to return the CSV file as a download
    # return send_file(temp_file, mimetype='text/csv', as_attachment=True)
    return {"grades": df.to_csv(index=False)}

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

    tmp_content = lessons["content"]
    try:
        lessons["content"] = request.json["updatedLessons"]
        with open("data/lessons.json", "w") as lesson_file:
            lesson_file.write(json.dumps(lessons))
    except Exception:
        lessons["content"] = tmp_content
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
    titles = {}
    for qId, question in enumerate(answered_quiz["quiz"]):
        titles[qId] = "Question " + str(qId) + ': '+question['core_topic']

        ques, resp = None, None
        evaluation[qId] = {"feedback": "", "score": 0}
        # Multiple choice preparation
        if lessons["content"][answered_quiz["lessonId"]]["quiz"][qId]["type"] == "mc":
            choices = lessons["content"][answered_quiz["lessonId"]]["quiz"][qId]["choices"]
            answer_idx = lessons["content"][answered_quiz["lessonId"]]["quiz"][qId]["a"]
            ques, resp = lessons["content"][answered_quiz["lessonId"]]["quiz"][qId]["q"], choices[int(question["response"])]

            evaluation[qId]["feedback"] = f"The correct answer was '{choices[answer_idx]}'"
            if question["response"] == str(answer_idx):
                evaluation[qId]["score"] = 1
            else:
                evaluation[qId]["score"] = 0

        # Short answer preparation
        elif lessons["content"][answered_quiz["lessonId"]]["quiz"][qId]["type"] == "sa":
            ques, resp = lessons["content"][answered_quiz["lessonId"]]["quiz"][qId]["q"], question["response"]
            evaluation[qId]["feedback"] = f"The correct answer was '{lessons['content'][answered_quiz['lessonId']]['quiz'][qId]['a']}'"
            evaluation[qId]["score"] = teacher.evaluate.eval_short_answer(ques, resp)/100

        if evaluation[qId]["score"] < 1:
            evaluation[qId]["feedback"] += "\nCorrection: "+teacher.evaluate.correct_answer(ques, resp)

    rcs_id = answered_quiz["rcsId"]
    lesson_id = answered_quiz['lessonId']
    topic = "Lesson " + lesson_id

    performance_data = {}
    for qId in evaluation:
        performance_data[titles[qId]] = f"Score: {evaluation[qId]['score']*100}%, Feedback: " + evaluation[qId]['feedback']

    connection.update_performance(rcs_id, topic, performance_data)

    return {"content": evaluation}


@app.route('/generate_questions', methods=['GET'])
def generate_questions():
    """Returns several candidate quizzes to be manually reviewed

    **Optional Query Params**

    * l (list[str]) - A list of lesson ids to generate the questions for
    * pmc (dict) - A dictionary, with the lesson id as the key, containing the probability that any given question will be multiple choice
    * topics (list[int]) - A list of the ids of all the core topics of the lesson that need their questions generated

    :return: A dictionary containing the generated transactions"""

    #return """
    #{"1.1":{"lesson_id":"1.1","quiz":[{"a":4,"choices":["Fruit Chill","Fire Wave","Bubble Blast","Frost Byte","Fruit Chill"],"q":"Q: What is the flavor of 5 Gum's latest taste sensation?","type":"mc"},{"a":2,"choices":["35 m/s","0 m/s","11 m/s","72 m/s"],"q":"Q: The average airspeed velocity of an unladen European swallow is:","type":"mc"},{"a":"Answer: A woodchuck can chuck around 35 cubic feet of wood in a day.","q":"Question: How much wood can a woodchuck chuck?","type":"sa"}]}}"""
    try:
        lesson_ids = json.loads(request.args.get("l", "[]"))
        if request.args.get("topics") is None:
            selected_topic_ids = None
        else:
            selected_topic_ids = json.loads(request.args.get("topics"))
        custom_pmc = json.loads(request.args.get("pmc", "{}"))
    except Exception:
        return "Malformed arguments"

    if lesson_ids:
        print(f"Limiting to lessons: {lesson_ids}")

    candidates = {}
    for lesson_id in lessons["content"]:
        lesson = lessons["content"][lesson_id]
        if lesson_ids and lesson["id"] not in lesson_ids:
            continue
        # Retrieve question types for quiz
        if not custom_pmc.get(lesson_id):
            percent_mc = lesson["percent_mc"] if lesson.get("percent_mc") else lessons["percent_mc"]
        else:
            percent_mc = custom_pmc.get(lesson_id)

        selected_topics = [topic for idx, topic in enumerate(lesson["core_topics"]) if selected_topic_ids is None or idx in selected_topic_ids]
        quiz = {"lesson_id": lesson_id, "quiz": teacher.gen_quiz_questions(selected_topics, percent_mc, randomize=True)}
        candidates[lesson_id] = quiz

    return candidates


if __name__ == '__main__':

    teacher = Teacher("000")
    teacher.set_model("text-davinci-003", "text-davinci-003", "text-davinci-003")

    with open("data/lessons.json", "r") as file:
        lessons = json.loads(file.read())

    for lesson in lessons["content"]:
        if not lessons["content"][lesson].get("id"):
            lessons["content"][lesson]["id"] = lesson

    app.run()

let selected_lesson = null;

function generateQuestions(){
    if(!selected_lesson){
        console.log("You must select a lesson first!");
        return;
    }
    console.log(`Generating questions for lesson ${selected_lesson}...`);
    fetch('/generate_questions?l='+JSON.stringify([selected_lesson]),
        {method: 'GET'}).then(response => response.json()).then(response => {
        console.log("Questions:", JSON.stringify(response));
        let questions = response;
        for(let lessonId of Object.keys(questions)) {
            for (let question of Object.values(questions[lessonId].quiz)) {
                question.id = genPseudorandom();
                console.log("Question:", question);
                addCandidateQuestion(lessonId, question);
            }
        }
    });
}


/** Switches the current view to that of the lesson indicated by {@link lessonId}
 * @param lessonId {String} The id of the lesson to be entered*/
function enterLesson(lessonId){
    console.log("Entering lesson", lessonId);
    selected_lesson = lessonId;
    document.getElementById("genQuestions").innerText = "Generate Questions for "+lessonId;
    let lessonElem = document.getElementById("lessons");
    lessonElem.style.display = "block";
    document.getElementById("lessonTitle").innerText = "Lesson "+lessonId;

    lessonElem.innerHTML = "";
    lessonElem.appendChild(formatQuestions(lessonId, LESSONS[lessonId].quiz, false));
}


window.onload = () => {
    setAdmin();
    loadLessons(enterLesson);
};
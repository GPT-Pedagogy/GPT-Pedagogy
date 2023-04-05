let GEN_LESSONS = {};
let selected_lesson = null;


function generateQuestions(){
    if(!selected_lesson){
        console.log("You must select a lesson first!");
        return;
    }
    console.log(`Generating questions for lesson ${selected_lesson}...`);
    fetch('/generate_questions?l='+JSON.stringify([selected_lesson]),
        {method: 'GET'}).then(response => response.json()).then(response => {
        GEN_LESSONS = JSON.parse(JSON.stringify(LESSONS));
        console.log("Questions:", JSON.stringify(response));
        let questions = response;
        let sidebarRight = document.getElementById("sidebarRight");
        for(let lessonId of Object.keys(questions)) {
            for (let question of Object.values(questions[lessonId].quiz)) {
                question.id = gen_pseudorandom();
                console.log("Question:", question);
                let elem = document.createElement("DIV");
                elem.classList.add("navElement");
                elem.style.marginBottom = "10px";
                elem.innerText = JSON.stringify(question);
                elem.onclick = () => {
                    let lessonElem = document.getElementById(`lessonForm${lessonId}`);
                    formatQuestions(lessonId, [question], false, lessonElem);
                    GEN_LESSONS[lessonId].quiz.push(question);
                    elem.remove();
                };
                sidebarRight.appendChild(elem);
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
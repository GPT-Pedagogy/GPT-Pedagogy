let selected_lesson = null;


/** Sends a request to generate a series of questions based off of the core topics and default
 * composition of a  given lesson*/
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

    if(lessonId === "chat"){
        document.getElementById("lessons").style.display = "none";
        document.getElementById("mainChat").style.display = "block";
        document.getElementById("lessonTitle").innerText = "Main Chat";
        document.getElementById("outputTitle").innerText = "Chat";
        document.getElementById("saveLessonsButton").style.visibility = "hidden";
        document.getElementById("genQuestions").style.visibility = "hidden";
        return;
    }

    document.getElementById("mainChat").style.display = "none";
    document.getElementById("saveLessonsButton").style.visibility = "visible";
    document.getElementById("genQuestions").style.visibility = "visible";
    document.getElementById("genQuestions").innerText = "Generate Questions for "+lessonId;
    let lessonElem = document.getElementById("lessons");
    lessonElem.style.display = "block";
    document.getElementById("lessonTitle").innerText = "Lesson "+lessonId;

    lessonElem.innerHTML = "";
    lessonElem.appendChild(formatQuestions(lessonId, LESSONS[lessonId].quiz, false));
}


/** Saves the current lesson configuration to disk to be retrieved later*/
function saveLessons(){

    if(!selected_lesson){
        console.log("You must select a lesson first!");
        return;
    }

    console.log("Saving lessons as", LESSONS);

    fetch('/save_lessons', {
        method: 'POST',
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify({'updatedLessons': LESSONS})
    }).then(response => response.json()).then(response => {
        console.log(JSON.stringify(response));
        console.log("Success:", response.success);
    });
}


function requestGrades(){
    console.log(`Requesting grades...`);
    fetch('/admin/grades', {method: 'GET'}).then(response => response.json()).then(response => {
        // Create element with <a> tag
        const link = document.createElement("a");
        const file = new Blob([response.grades], { type: 'text/plain' });
        link.href = URL.createObjectURL(file);
        link.download = "grades.csv";

        link.click();
        URL.revokeObjectURL(link.href);
    });
}


window.onload = () => {
    enterLesson('chat');
    let sidebarLeft = document.getElementById("sidebarLeft");
    sidebarLeft.innerHTML = `<div class="navElement" onclick="enterLesson('chat');">Main Chat</div>`;
    setAdmin();
    loadLessons(enterLesson);
};
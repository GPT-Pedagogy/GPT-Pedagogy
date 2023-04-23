

/** A dictionary of lists of candidate quiz questions waiting to be added by an admin*/
let question_candidates = {};



function proposeGenerateQuestions(){
    document.getElementById("confirmationPopup").style.display = "block";
    document.getElementById("popupConfirm").onclick = generateQuestions;
}
/** Sends a request to generate a series of questions based off of the core topics and default
 * composition of a given lesson*/
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
                question_candidates[lessonId].push(question);
                addCandidateQuestionElem(lessonId, question);
            }
        }
    });
}


/** Switches the current view to that of the lesson indicated by {@link lessonId}
 * @param lessonId {String} The id of the lesson to be entered*/
function enterLesson(lessonId){
    console.log("Entering lesson", lessonId);
    selected_lesson = lessonId;
    let sidebarRight = document.getElementById("sidebarRight");
    let candidateHolder = document.getElementById("candidateHolder");
    candidateHolder.innerHTML = "";

    if(lessonId === "chat"){
        document.getElementById("lessons").style.display = "none";
        document.getElementById("mainChat").style.display = "block";
        document.getElementById("lessonTitle").innerText = "Main Chat";
        document.getElementById("outputTitle").style.display = "none";
        document.getElementById("saveLessonsButton").style.visibility = "hidden";
        document.getElementById("genQuestions").style.visibility = "hidden";
        sidebarRight.style.visibility = "hidden";
        return;
    }

    sidebarRight.style.visibility = "visible";
    document.getElementById("mainChat").style.display = "none";
    document.getElementById("outputTitle").style.display = "block";
    document.getElementById("saveLessonsButton").style.visibility = "visible";
    document.getElementById("genQuestions").style.visibility = "visible";
    document.getElementById("genQuestions").innerText = "Generate Questions for "+lessonId;
    let lessonElem = document.getElementById("lessons");
    lessonElem.style.display = "block";
    document.getElementById("lessonTitle").innerText = "Lesson "+lessonId;

    lessonElem.innerHTML = "";
    lessonElem.appendChild(formatQuestions(lessonId, lessons[lessonId].quiz, false, null, onQuestionAdd));
    if(question_candidates[lessonId] === undefined) question_candidates[lessonId] = [];
    for(let ques of question_candidates[lessonId]) addCandidateQuestionElem(lessonId, ques);
}


/** Saves the current lesson configuration to disk to be retrieved later*/
function saveLessons(){

    if(!selected_lesson){
        console.log("You must select a lesson first!");
        return;
    }

    console.log("Saving lessons as", lessons);

    fetch('/save_lessons', {
        method: 'POST',
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify({'updatedLessons': lessons})
    }).then(response => response.json()).then(response => {
        console.log(JSON.stringify(response));
        console.log("Success:", response.success);
    });
}


/** Requests the recorded grades from the backend and downloads them as a file*/
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


/** Adds a question to the list of candidate questions and to the sidebar.  These may be added to a quiz through admin oversight
 * @param lessonId {String} The id of the lesson to add approved questions to
 * @param question {Object} Dictionary containing the question information*/
function addCandidateQuestionElem(lessonId, question){
    let candidateHolder = document.getElementById("candidateHolder");
    let elem = document.createElement("DIV");
    elem.id = `candidate${question.id}`;
    elem.classList.add("navElement");
    elem.style.marginBottom = "10px";
    elem.innerText = JSON.stringify(question);

    let addButton = document.createElement("BUTTON");
    addButton.id = `add${question.id}`;
    addButton.className = "questionEditButton";
    addButton.innerText = "<--";
    addButton.style.backgroundColor = "green";
    addButton.onclick = () => {
        let lessonElem = document.getElementById(`lessonForm${lessonId}`);
        formatQuestions(lessonId, [question], false, lessonElem, onQuestionAdd);
        lessons[lessonId].quiz.push(question);
        for(let i=0; i<question_candidates[lessonId].length; i++)
            if(question_candidates[lessonId][i].id === question.id) {
                question_candidates[lessonId].splice(i, 1);
                break;
            }
        elem.remove();
        addButton.remove();
    };

    candidateHolder.appendChild(addButton);
    candidateHolder.appendChild(elem);
}


/** Removes the quiz with an id of {@link quesId} from the lesson with the id {@link lessonId} and returns the removed element
 * @param lessonId {String} The id of the lesson to remove the question from
 * @param quesId {String} The id of the quiz question to remove
 * @return {Object | null} The removed question element*/
function removeQuizQuestion(lessonId, quesId) {
    let found = null;

    console.log("Removing quiz", quesId, "from lesson", lessonId);
    for(let i=0; i<lessons[lessonId].quiz.length; i++){
        if(lessons[lessonId].quiz[i].id === quesId) {
            found = lessons[lessonId].quiz[i];
            question_candidates[lessonId].push(lessons[lessonId].quiz[i]);
            lessons[lessonId].quiz.splice(i, 1);
        }
    }
    if(found) {
        document.getElementById(`question${quesId}`).remove();
        document.getElementById(`delete${quesId}`).remove();
        return found;
    }
}


/** Called when a question is added to a lesson.  Adds an extra delete button that removes an added
 * question and turns it back into a candidate
 * @param lessonId {String} The id of the lesson the question is being added to
 * @param quesId {String} The id of the question
 * @param quizDiv {HTMLElement} The quiz element that the question is being added to*/
function onQuestionAdd(lessonId, quesId, quizDiv){
    let delButton = document.createElement("BUTTON");
    delButton.id = `delete${quesId}`;
    delButton.className = "questionEditButton";
    delButton.innerText = "-->";
    delButton.style.backgroundColor = "red";
    delButton.onclick = () => {
        let removed = removeQuizQuestion(lessonId, quesId);
        addCandidateQuestionElem(lessonId, removed);
    };

    quizDiv.appendChild(delButton);
}


window.onload = () => {
    enterLesson('chat');
    let sidebarLeft = document.getElementById("sidebarLeft");
    sidebarLeft.innerHTML = `<div class="navElement" onclick="enterLesson('chat');">Main Chat</div>`;
    setAdmin();
    loadLessons(enterLesson);
};
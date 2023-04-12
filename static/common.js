"use strict";

const USER_SPEAKER = 0;
const MATHESIS_SPEAKER = 1;
const TYPING = `<p class="speechBubble mathesisSpeech">...</p>`;
let LESSONS = {};
let QUESTION_CANDIDATES = [];
const CHAT_HISTORY = {};
let RCS_ID = "000";

const ADMIN = 1;
const STUDENT = 0;
let role = STUDENT;

function setAdmin(){
    role = ADMIN;
}

/** Sends the content of the input prompt to the backend and appends the generated response to the chat*/
function sendChat(){
    let inputText = document.getElementById("inputText").value;
    document.getElementById("inputText").value = '';
    addOutput('chat', USER_SPEAKER, inputText);
    // Add typing indicator
    document.getElementById("output").innerHTML += TYPING;

    fetch('/input', {
        method: 'POST',
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify({ "inputText": inputText })
    }).then(response => response.json()).then(response => {
        console.log(JSON.stringify(response));
        // Remove typing indicator
        let tmp = document.getElementById("output").innerHTML;
        document.getElementById("output").innerHTML = tmp.replace(TYPING, "");
        addOutput('chat', MATHESIS_SPEAKER, response.content);
    });
}

/** Sends the user response to a lesson quiz to the backend and appends the evaluation to the chat
 * @param lessonId {String} The id of the lesson the quiz belongs to
 * @return {Boolean} If the quiz has been submitted successfully*/
function sendQuiz(lessonId){
    let quiz = LESSONS[lessonId].quiz.slice();
    for (let qId in quiz) {
        let answer = "";
        if(quiz[qId].type === "mc")
            answer = document.querySelector(`input[name="${lessonId}.${qId}"]:checked`);
        if(quiz[qId].type === "sa")
            answer = document.querySelector(`input[name="${lessonId}.${qId}"]`);
        if(!answer){
            console.log("No answer for question", qId);
            return false;
        }
        quiz[qId].response = answer.value;
    }
    document.getElementById("output").innerHTML += TYPING;

    fetch('/evaluate', {
        method: 'POST',
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify({"rcs_id": RCS_ID, "lessonId": lessonId, "quiz": quiz})
    }).then(response => response.json()).then(response => {
        console.log(JSON.stringify(response));
        // Remove typing
        let tmp = document.getElementById("output").innerHTML;
        document.getElementById("output").innerHTML = tmp.replace(TYPING, "");

        for(let fId of Object.keys(response.content)) {
            let evaluation = `Evaluation for question ${fId}:`+
                `\nScore: ${response.content[fId].score*100}%`+
                `\nFeedback: ${response.content[fId].feedback}`.replace(/\n/g, "<br>");
            addOutput(lessonId, MATHESIS_SPEAKER, evaluation);
        }
    });
    return true;
}

/** Loads in lesson information from the backend and builds the lessons*/
function loadLessons(enterLessonFunc){
    console.log(`Getting lessons ${role === ADMIN ? "as admin" : "as student"}...`);
    fetch(`${role === ADMIN ? "/admin" : ""}/lessons`, {method: 'GET'}).then(response => response.json()).then(response => {
        console.log("Lessons:", JSON.stringify(response));
        let lessons = response;
        let sidebarLeft = document.getElementById("sidebarLeft");
        LESSONS = lessons;
        for(let lesson of Object.values(lessons)){
            console.log("Lesson:", lesson);
            let elem = document.createElement("DIV");
            elem.classList.add("navElement");
            elem.onclick = () => enterLessonFunc(lesson.id);
            elem.innerHTML = `${lesson.name}<br>Core Topics:<br>`;
            for(let topic of lesson.core_topics)
                elem.innerHTML += topic+",<br>";
            sidebarLeft.appendChild(elem);
        }
    });
}


function addCandidateQuestion(lessonId, question){
    let sidebarRight = document.getElementById("sidebarRight");
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
        formatQuestions(lessonId, [question], false, lessonElem);
        LESSONS[lessonId].quiz.push(question);
        elem.remove();
        addButton.remove();
    };

    QUESTION_CANDIDATES.push(question);
    sidebarRight.appendChild(addButton);
    sidebarRight.appendChild(elem);
}


function removeQuizQuestion(lessonId, quesId) {
    let found = null;
    console.log("goodbye to quiz", quesId, "from lesson", lessonId);
    for(let i=0; i<LESSONS[lessonId].quiz.length; i++){
        if(LESSONS[lessonId].quiz[i].id === quesId) {
            found = LESSONS[lessonId].quiz[i];
            QUESTION_CANDIDATES.push(LESSONS[lessonId].quiz[i]);
            LESSONS[lessonId].quiz.splice(i, 1);
        }
    }
    if(found) {
        document.getElementById(`question${quesId}`).remove();
        document.getElementById(`delete${quesId}`).remove();
        return found;
    }
}


/** Creates the quiz detained by the lesson on the front end for the user to interact with
 * @param lessonId {String} The id of the lesson with the quiz to be displayed
 * @return {HTMLElement} The HTML form of the quiz*/
function formatQuestions(lessonId, quiz, enabled=true, quizDiv=null) {
    let addSubmit = false;
    if (!quizDiv) {
        addSubmit = true;
        quizDiv = document.createElement("DIV");
        quizDiv.id = `lessonForm${lessonId}`;
    }
    for (let qId in quiz) {
        if (!quiz[qId].id) quiz[qId].id = genPseudorandom();

        let quesElem = document.createElement("DIV");
        quesElem.className = "quizQuestion";
        let quesId = quiz[qId].id;
        quesElem.id = `question${quiz[qId].id}`;
        quesElem.style.backgroundColor = "#64abc2";
        if (role === ADMIN) {
            let delButton = document.createElement("BUTTON");
            delButton.id = `delete${quiz[qId].id}`;
            delButton.className = "questionEditButton";
            delButton.innerText = "-->";
            delButton.style.backgroundColor = "red";
            delButton.onclick = () => {
                let removed = removeQuizQuestion(lessonId, quesId);
                addCandidateQuestion(lessonId, removed);
            };

            quizDiv.appendChild(delButton);
        }
        quesElem.innerHTML += `<p>Core Topic: ${quiz[qId].core_topic}</p>`;
        quesElem.innerHTML += `<p>${quiz[qId].q}</p>`;
        if (quiz[qId].type === "mc")
            for (let cId in quiz[qId].choices) {
                quesElem.innerHTML += `<input type="radio" name="${lessonId}.${qId}" value="${cId}">
                    <label>${quiz[qId].choices[cId]}</label><br>`;
            }
        if (quiz[qId].type === "sa")
            quesElem.innerHTML += `<input type="text" name="${lessonId}.${qId}" placeholder="Type your answer here" style="width: 400px">`;

        if (role === ADMIN)
            quesElem.innerHTML += `<p>A: ${quiz[qId].a}</p>`;
        quizDiv.appendChild(quesElem);

    }

    if (addSubmit && enabled) {
        let submit = document.createElement("BUTTON");
        submit.innerText = "Submit";
        submit.onclick = () => {
            console.log("Submitting quiz for lesson", lessonId);
            sendQuiz(lessonId);
        };
        quizDiv.appendChild(submit);
    }
    return quizDiv;
}


/** Adds text to the chat from a specified entity
 * @param chatId {String} The id of the chat for saving and loading messages
 * @param speaker {number} The id of the speaker producing the text
 * @param text {String} The text to be sent to the chat
 * @param updateHistory {Boolean} Weather to update the history of the chat with this {@link text}*/
function addOutput(chatId, speaker, text, updateHistory = true){
    let bubbleClass = speaker === USER_SPEAKER ? "userSpeech" : "mathesisSpeech";
    document.getElementById("output").innerHTML += `<p class="speechBubble ${bubbleClass}">
        ${text}
    </p>`;
    if(updateHistory){
        if(!CHAT_HISTORY[chatId]) CHAT_HISTORY[chatId] = [];
        CHAT_HISTORY[chatId].push({"speaker": speaker, "text": text});
    }
}

/** Clears the chat box and loads in the history from the chat with the id {@link chatId}
 * @param chatId {String} The id of the chat to load*/
function loadChat(chatId){
    document.getElementById("output").innerHTML = "";

    if(CHAT_HISTORY[chatId])
        for(let message of CHAT_HISTORY[chatId])
            addOutput(chatId, message.speaker, message.text, false);
}

function genPseudorandom(){
    return `${Date.now()}_${Math.floor(Math.random() * 1000)}`;

}
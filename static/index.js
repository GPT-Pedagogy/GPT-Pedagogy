"use strict";

const USER_SPEAKER = 0;
const MATHESIS_SPEAKER = 1;
const TYPING = `<p class="speechBubble mathesisSpeech">...</p>`;
let LESSONS = {};
const CHAT_HISTORY = {};

function sendChat(){
    let inputText = document.getElementById("inputText").value;
    document.getElementById("inputText").value = '';
    addOutput('chat', USER_SPEAKER, inputText);
    // Add typing
    document.getElementById("output").innerHTML += TYPING;
    fetch('/input', {
        method: 'POST',
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify({ "inputText": inputText })
    }).then(response => response.json()).then(response => {
        console.log(JSON.stringify(response));
        // Remove typing
        let tmp = document.getElementById("output").innerHTML;
        document.getElementById("output").innerHTML = tmp.replace(TYPING, "");
        addOutput('chat', MATHESIS_SPEAKER, response["content"]);
    });
}

function sendQuiz(lessonId){
    let quiz = LESSONS[lessonId]["quiz"].slice();
    for (let qId in quiz) {
        let answer = document.querySelector(`input[name="${lessonId}.${qId}"]:checked`);
        if(!answer){
            console.log("No answer for question", qId);
            return false;
        }
        quiz[qId]["selected"] = answer.value;
    }
    document.getElementById("output").innerHTML += TYPING;
    fetch('/evaluate', {
        method: 'POST',
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify({"lessonId": lessonId, "quiz": quiz})
    }).then(response => response.json()).then(response => {
        console.log(JSON.stringify(response));
        // Remove typing
        let tmp = document.getElementById("output").innerHTML;
        document.getElementById("output").innerHTML = tmp.replace(TYPING, "");
        addOutput(lessonId, MATHESIS_SPEAKER, JSON.stringify(response["content"]));
    });
}

function loadLessons(){
    console.log("Getting lessons...");
    fetch('/lessons', {
        method: 'GET'
    }).then(response => response.json()).then(response => {
        console.log("Lessons:", JSON.stringify(response));
        let lessons = response;
        let sideNav = document.getElementById("sidenav");
        sideNav.innerHTML = `<div class="navElement" onclick="enterLesson('chat');">Main Chat</div>`;
        LESSONS = lessons;
        for(let lesson of Object.values(lessons)){
            console.log("Lesson:", lesson);
            sideNav.innerHTML += `<div class="navElement" onclick="enterLesson('${lesson.id}');">
                ${lesson.name}
            </div>`;
        }
    });
}

function enterLesson(lessonId){
    console.log("Entering lesson", lessonId);
    loadChat(lessonId);
    if(lessonId === "chat"){
        document.getElementById("lessons").style.display = "none";
        document.getElementById("mainChat").style.display = "block";
        document.getElementById("lessonTitle").innerText = "Main Chat";
        document.getElementById("outputTitle").innerText = "Chat";
        return;
    }
    let lessonElem = document.getElementById("lessons");
    lessonElem.style.display = "block";
    document.getElementById("mainChat").style.display = "none";
    document.getElementById("lessonTitle").innerText = "Lesson "+lessonId;
    document.getElementById("outputTitle").innerText = "Feedback";

    lessonElem.innerHTML = "";
    lessonElem.appendChild(formatQuestions(lessonId));
}

function formatQuestions(lessonId){
    let quizForm = document.createElement("FORM");
    quizForm.id = `lessonForm${lessonId}`;
    quizForm.action = "javascript:void(0)";
    quizForm.onsubmit = () => sendQuiz(lessonId);
    let quiz = LESSONS[lessonId]["quiz"];
    for (let qId in quiz) {
        quizForm.innerHTML += `<p>${quiz[qId]["q"]}</p>`;
        for(let cId in quiz[qId]["choices"]){
            quizForm.innerHTML += `<input type="radio" name="${lessonId}.${qId}" value="${cId}">
                <label>${quiz[qId]["choices"][cId]}</label><br>`;
        }
    }

    quizForm.innerHTML += `<br><input type="submit" value="Submit"><br><hr>`;
    return quizForm;
}

function addOutput(chatId, speaker, text, updateHistory = true){
    let speakerName = speaker === USER_SPEAKER ? "Me" : "Mathesis";
    let bubbleClass = speaker === USER_SPEAKER ? "userSpeech" : "mathesisSpeech";
    document.getElementById("output").innerHTML += `<p class="speechBubble ${bubbleClass}">
        ${speakerName}: ${text}
    </p>`;
    if(updateHistory){
        if(!CHAT_HISTORY[chatId]) CHAT_HISTORY[chatId] = [];
        CHAT_HISTORY[chatId].push({"speaker": speaker, "text": text});
    }
}

function loadChat(chatId){
    document.getElementById("output").innerHTML = "";

    if(CHAT_HISTORY[chatId])
        for(let message of CHAT_HISTORY[chatId])
            addOutput(chatId, message["speaker"], message["text"], false);
}

window.onload = () => {
    enterLesson('chat');
    loadLessons();
};
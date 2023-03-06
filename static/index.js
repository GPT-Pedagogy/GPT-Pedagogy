"use strict";

const USER_SPEAKER = 0;
const MATHESIS_SPEAKER = 1;
const TYPING = `<p class="speechBubble mathesisSpeech">...</p>`;
let LESSONS = null;
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
    let lessonForm = document.getElementById(`lessonForm${lessonId}`);
    let answers = {};
    // TODO: Rewrite lessons everywhere as dict instead of list of lessons
    for(let lesson of LESSONS){
        if(lesson["id"] === lessonId) {
            for (let qId in lesson["quiz"]) {
                answers
                for(let cId in lesson["quiz"][qId]["choices"]){
                    quizForm.innerHTML += `<input type="radio" name="${lessonId}".${qId} value="${cId}">
                        <label>${lesson["quiz"][qId]["choices"][cId]}</label><br>`;
                }
            }
            break;
        }
    }
    fetch('/evaluate', {
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

function loadLessons(){
    console.log("Getting lessons...");
    fetch('/lessons', {
        method: 'GET'
    }).then(response => response.json()).then(response => {
        console.log("Lessons:", JSON.stringify(response));
        let lessons = response;
        LESSONS = lessons;
        let sideNav = document.getElementById("sidenav");
        sideNav.innerHTML = `<div class="navElement" onclick="enterLesson('chat');">Main Chat</div>`;
        for(let lesson of lessons){
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
    quizForm.onsubmit = () => sendQuiz(lessonId);
    for(let lesson of LESSONS){
        if(lesson["id"] === lessonId) {
            for (let qId in lesson["quiz"]) {
                quizForm.innerHTML += `<p>${lesson["quiz"][qId]["q"]}</p>`;
                for(let cId in lesson["quiz"][qId]["choices"]){
                    quizForm.innerHTML += `<input type="radio" name="${lessonId}".${qId} value="${cId}">
                        <label>${lesson["quiz"][qId]["choices"][cId]}</label><br>`;
                }
            }
            break;
        }
    }
    quizForm.innerHTML += `<br><input type="submit" value="Submit">`;
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

/** Switches the current view to that of the lesson indicated by {@link lessonId}
 * @param lessonId {String} The id of the lesson to be entered*/
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
    document.getElementById("outputTitle").innerText = "Evaluation";

    lessonElem.innerHTML = "";
    lessonElem.appendChild(formatQuestions(lessonId, LESSONS[lessonId].quiz));
}

window.onload = () => {
    enterLesson('chat');
    let sidebarLeft = document.getElementById("sidebarLeft");
    sidebarLeft.innerHTML = `<div class="navElement" onclick="enterLesson('chat');">Main Chat</div>`;
    loadLessons(enterLesson);
};
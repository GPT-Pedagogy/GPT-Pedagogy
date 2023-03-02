USER_SPEAKER = 0
MATHESIS_SPEAKER = 1
TYPING = `<p class="speechBubble mathesisSpeech">...</p>`

function hello(){
    console.log("Hello there");
    let inputText = document.getElementById("inputText").value;
    document.getElementById("inputText").value = "";
    addOutput(USER_SPEAKER, inputText)
    // Add typing
    document.getElementById("output").innerHTML += TYPING
    fetch('/input', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "inputText": inputText })
    }).then(response => response.json()).then(response => {
        console.log(JSON.stringify(response));
        // Remove typing
        let tmp = document.getElementById("output").innerHTML;
        document.getElementById("output").innerHTML = tmp.replace(TYPING, "");
        addOutput(MATHESIS_SPEAKER, response["content"])
    });
}

function addOutput(speaker, text){
    let speakerName = speaker === USER_SPEAKER ? "Me: " : "Mathesis: ";
    let bubbleClass = speaker === USER_SPEAKER ? "userSpeech" : "mathesisSpeech";
    document.getElementById("output").innerHTML += `<p class="speechBubble ${bubbleClass}">
        ${speakerName+text}
    </p>`;
}
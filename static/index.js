function hello(){
    console.log("Hello there");
    let inputText = document.getElementById("inputText").value;
    document.getElementById("inputText").value = "";
    document.getElementById("output").innerHTML += 'Me: '+inputText+"<br>";
    fetch('/input', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "inputText": inputText })
    }).then(response => response.json()).then(response => {
        console.log(JSON.stringify(response));
        document.getElementById("output").innerHTML += "Mathesis:"+response["content"]+"<br>";
    });
}
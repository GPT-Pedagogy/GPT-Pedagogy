from flask import Flask, render_template, request
from Chat import Chat
app = Flask(__name__)
chat = Chat("0000")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/input', methods=['POST'])
def form_input():
    input_text = request.json["inputText"]
    print("Input text", input_text)
    chat.submit(input_text)
    resp = chat.generate()
    return {"content": resp}


if __name__ == '__main__':
    app.run()

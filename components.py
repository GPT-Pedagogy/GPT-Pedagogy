# Contains chat functionality
# save chats from previous sessions and embedded vectors from models
# recall these vectors when context is needed from previous session and pick similar ones using vector distance
# Feed decoded text into model to answer question with context
# https://community.openai.com/t/a-smarter-chatbot-with-memory-idea/27215
import json
from Model import Model
import time


class Chat:
    """Class representing a chat instance of a user, keeping track of chat history and managing interactions"""
    CHAT_MODE = 0
    MODEL_NAME = "text-davinci-003"
    chat_history = []
    MIN_CHAT_TOKENS = 30

    def __init__(self):
        self.model: Model = Model(self.MODEL_NAME)

    def submit(self, text: str):
        """Submit user text into the chat"""
        text = text.strip()
        # Add punctuation to avoid bad completions
        if text[-1] not in ["?", ".", "!"]:
            text += "."
        self.chat_history.append({"role": "user", "content": text, "timestamp": time.time()})

    def generate(self):
        """Generate an appropriate response from the model"""
        # mode logic
        response = self.model.complete(self.chat_history[-1]["content"],
                       context=self.chat_history[:-1], max_tokens=self.MIN_CHAT_TOKENS)
        self.chat_history.append({"role": "assistant", "content": response, "timestamp": time.time()})
        return response

    def load_from_file(self, file_name: str):
        """Load chat state from a file"""
        with open(file_name, "r") as file:
            raw = file.read()
        chat = json.loads(raw)
        for message in chat[::-1]:
            self.chat_history.insert(0, message)

    def save_to_file(self, file_name: str):
        """Save current chat state into a file"""
        with open(file_name, "w") as file:
            file.write(json.dumps(self.chat_history))

    def clear(self):
        """Clears chat history"""
        self.chat_history = []

    def set_model(self, model_name: str):
        """Sets the model to be used in the chat"""
        self.MODEL_NAME = model_name
        self.model: Model = Model(self.MODEL_NAME)


class Evaluate:
    MODEL_NAME = "text-davinci-003"
    EDITOR_MODEL_NAME = "text-davinci-edit-001"

    def __init__(self):
        self.model: Model = Model(self.MODEL_NAME)
        self.editor_model: Model = Model(self.EDITOR_MODEL_NAME)

    def eval_short_answer(self, question: str, answer: str):
        """Evaluates the answer to a question in the form of a grade"""

        prompt = f"A student was asked {question} and they responded with {answer}.  " \
                 f"Grade this answer on a scale from 0 to 100."
        score = self.model.complete(prompt).strip().split()

        for word in score:
            if word.split(".")[0].isnumeric():
                return int(word.split(".")[0])

        raise ValueError("No string within the response was a score!")

    def correct_answer(self, question: str, answer: str):
        """Takes in an incorrect answer and corrects it to a better response"""

        prompt = f"Make this answer better match the question {question}."
        return self.editor_model.edit(prompt, answer)

    def set_model(self, model_name: str):
        """Sets the model to be used for evaluation"""

        self.MODEL_NAME = model_name
        self.model: Model = Model(self.MODEL_NAME)

# Contains chat functionality
# save chats from previous sessions and embedded vectors from models
# recall these vectors when context is needed from previous session and pick similar ones using vector distance
# Feed decoded text into model to answer question with context
# https://community.openai.com/t/a-smarter-chatbot-with-memory-idea/27215
import json
from model.Model import Model
import time


class Chat:
    """Class representing a chat instance of a user, keeping track of chat history and managing interactions"""

    CHAT_MODE = 0
    MODEL_NAME = "text-davinci-003"
    chat_history = []
    MIN_CHAT_TOKENS = 70

    def __init__(self):
        self.model: Model = Model(self.MODEL_NAME)

    def submit(self, text: str):
        """Submit user text into the chat

        :param text: The text to save to the chat"""

        text = text.strip()
        # Add punctuation to avoid bad completions
        if text[-1] not in ["?", ".", "!"]:
            text += "."
        self.chat_history.append({"role": "user", "content": text, "timestamp": time.time()})

    def generate(self):
        """Generate an appropriate response from the model

        :return: The model's response to the latest chat from the user"""

        if len(self.chat_history[-1]["content"]) < 5:
            response = "I work best when prompts are longer.  Try prefacing your input with 'What is ...' or 'Teach me about ...'"
        else:
            response = self.model.complete(self.chat_history[-1]["content"],
                           context=self.chat_history[:-1], max_tokens=self.MIN_CHAT_TOKENS)
        self.chat_history.append({"role": "assistant", "content": response, "timestamp": time.time()})
        return response

    def load_from_file(self, file_name: str):
        """Load chat state from a file

        :param file_name: The name of the file to load the chat from"""

        with open(file_name, "r") as file:
            raw = file.read()
        chat = json.loads(raw)
        for message in chat[::-1]:
            self.chat_history.insert(0, message)

    def save_to_file(self, file_name: str):
        """Save current chat state into a file

        :param file_name: The name of the file to save the chat to"""

        with open(file_name, "w") as file:
            file.write(json.dumps(self.chat_history))

    def clear(self):
        """Clears chat history"""

        self.chat_history = []

    def set_model(self, model_name: str):
        """Sets the model to be used in the chat

        :param model_name: The name of the model to use for the chat"""

        self.MODEL_NAME = model_name
        self.model: Model = Model(self.MODEL_NAME)


class Evaluate:
    """Class containing evaluation and correction logic for user submitted answers"""

    MODEL_NAME = "text-davinci-003"
    EDITOR_MODEL_NAME = "text-davinci-edit-001"

    def __init__(self):
        self.model: Model = Model(self.MODEL_NAME)
        self.editor_model: Model = Model(self.EDITOR_MODEL_NAME)

    def eval_short_answer(self, question: str, answer: str):
        """Evaluates the answer to a question in the form of a grade

        :param question: The short answer question that the student was asked
        :param answer: The answer that the student provided
        :return: The grade of the answer as an integer score"""

        prompt = f"A student was asked {question} and they responded with {answer}.  " \
                 f"Grade this answer on a scale from 0 to 100."
        score = self.model.complete(prompt).strip().split()

        for word in score:
            if word.split("/")[0].split(".")[0].isnumeric():
                return int(word.split("/")[0].split(".")[0])

        raise ValueError("No string within the response was a score!")

    def correct_answer(self, question: str, answer: str):
        """Takes in an incorrect answer and corrects it to a better response

        :param question: The short answer or multiple choice question that the student was asked
        :param answer: The answer that the student provided
        :return: The model's correction of the student's answer"""

        prompt = f"Make this answer better match the question {question}."
        return self.editor_model.edit(prompt, answer)

    def set_model(self, model_name: str):
        """"Sets the model to be used for evaluation

        :param model_name: The name of the model to use for evaluation"""

        self.MODEL_NAME = model_name
        self.model: Model = Model(self.MODEL_NAME)

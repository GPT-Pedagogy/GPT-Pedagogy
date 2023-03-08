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
    MODEL_NAME = "text-ada-001"
    chat_history = []

    def __init__(self, rcs_id: str):
        self.rcs_id = rcs_id
        self.model: Model = Model(self.MODEL_NAME)

    def submit(self, text: str, mode: str = CHAT_MODE):
        """Submit user text into the chat"""
        text = text.strip()
        # Add punctuation to avoid bad completions
        if text[-1] not in ["?", ".", "!"]:
            text += "."
        self.chat_history.append({"role": "user", "content": text, "timestamp": time.time()})

    def generate(self, mode: str = CHAT_MODE):
        """Generate an appropriate response from the model"""
        # mode logic
        response = self.model.complete(self.chat_history[-1]["content"])
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

from components import Chat, Evaluate
from Model import Model


class Teacher:
    MODEL_NAME = "text-ada-001"

    def __init__(self, rcs_id: str):
        self.rcs_id = rcs_id
        self.model: Model = Model(self.MODEL_NAME)
        self.chat = Chat()
        self.evaluate = Evaluate()

    def gen_multiple_choice(self, topic: str):
        prompt = f"Generate a multiple choice question about {topic}."
        return self.model.complete(prompt)

    def gen_short_answer(self, topic: str):
        prompt = f"Generate a short answer question about {topic}."
        return self.model.complete(prompt)


import random
import re
from components import Chat, Evaluate
from Model import Model


class Teacher:
    MODEL_NAME = "text-ada-001"
    MIN_MC_TOKENS = 60
    MIN_SA_TOKENS = 50

    def __init__(self, rcs_id: str):
        self.rcs_id = rcs_id
        self.model: Model = Model(self.MODEL_NAME)
        self.chat = Chat()
        self.evaluate = Evaluate()

    def gen_multiple_choice(self, topic: str, max_tokens=MIN_MC_TOKENS, **kwargs):
        if kwargs.get("max_tokens", self.MIN_MC_TOKENS) < self.MIN_MC_TOKENS:
            ValueError(f"Arg 'max_tokens' must be at least {self.MIN_MC_TOKENS}!")

        prompt = f"Generate a multiple choice question about {topic} where the first choice is correct."
        question = self.model.complete(prompt, max_tokens=max_tokens, **kwargs).strip("\n").splitlines()
        answer = random.randint(0, len(question)-2)
        # Swap first, correct answer with the randomly generate answer slot
        tmp = question[answer+1]
        question[answer + 1] = question[1]
        question[1] = tmp
        # Get rid of numbering
        for i in range(1, len(question)):
            if len(question[i]) > 2 and question[i][0].isalpha() and question[i][1] in [".", ")"]:
                question[i] = question[i][2:].strip()

        return {"q": question, "type": "mc", "a":  answer, "choices": question[1:]}

    def gen_short_answer(self, topic: str, max_tokens=MIN_SA_TOKENS, **kwargs):
        if kwargs.get("max_tokens", self.MIN_SA_TOKENS) < self.MIN_SA_TOKENS:
            ValueError(f"Arg 'max_tokens' must be at least {self.MIN_SA_TOKENS}!")

        prompt = f"Generate a short answer question about {topic} and an answer."
        question = self.model.complete(prompt, max_tokens=max_tokens, **kwargs).strip("\n").splitlines()
        return {"q": question[0], "type": "sa", "a":  question[1]}

    def set_model(self, teacher_model: str = None, chat_model: str = None, eval_model: str = None):
        if teacher_model:
            self.MODEL_NAME = teacher_model
            self.model: Model = Model(self.MODEL_NAME)
        if chat_model:
            self.chat.set_model(chat_model)
        if eval_model:
            self.evaluate.set_model(eval_model)


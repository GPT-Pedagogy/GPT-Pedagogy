import random
from model.components import Chat, Evaluate
from model.Model import Model


class Teacher:
    """A high-level class that contains both chat and evaluation functionality, along with administrative capabilities"""

    MODEL_NAME = "text-davinci-003"
    MIN_MC_TOKENS = 60
    MIN_SA_TOKENS = 50

    def __init__(self, rcs_id: str):
        """A high-level class that contains both chat and evaluation functionality, along with administrative capabilities

        :param rcs_id: The RCS id of the student that this teacher will interact with"""

        self.rcs_id = rcs_id
        self.model: Model = Model(self.MODEL_NAME)
        self.chat = Chat()
        self.evaluate = Evaluate()

    def gen_quiz_questions(self, topics: list[str], percent_mc: float, randomize=False):
        """Generates a quiz based on a set of topics and a set of question types

        :param topics: A list of topics to generate questions based off of
        :param percent_mc: The percentage of questions that will be multiple choice
        :param randomize: Whether to randomize the order of the questions that will be generated
        :return: A list of generated questions"""

        if randomize:
            random.shuffle(topics)

        quiz = []
        for i, topic in enumerate(topics):
            rand = random.randint(0, 100)
            q_type = "sa"
            if rand < percent_mc:
                q_type = "mc"
            quiz.append(self.gen_multiple_choice(topic) if q_type == "mc" else
                        self.gen_short_answer(topic))

        return quiz

    def gen_multiple_choice(self, topic: str, max_tokens=MIN_MC_TOKENS, **kwargs):
        """Generates a multiple choice question based on the given topic and encodes it into json

        :param topic: The topic to generate a question on
        :param max_tokens: The maximum length of the generated question in tokens
        :return: A generated multiple choice question"""

        if kwargs.get("max_tokens", self.MIN_MC_TOKENS) < self.MIN_MC_TOKENS:
            ValueError(f"Arg 'max_tokens' must be at least {self.MIN_MC_TOKENS}!")

        print(f"Generating multiple choice question about {topic}...")

        prompt = f"Generate a multiple choice question about {topic} where the first choice is correct."
        question = self.model.complete(prompt, max_tokens=max_tokens, **kwargs).strip("\n").splitlines()
        # Remove empty elements
        question = list(filter(None, question))

        answer = random.randint(0, len(question)-2)
        # Swap first, correct answer with the randomly generated answer slot
        tmp = question[answer+1]
        question[answer + 1] = question[1]
        question[1] = tmp
        # Get rid of numbering
        for i in range(1, len(question)):
            question[i] = question[i].strip()
            while len(question[i]) > 2 and question[i][0].isalpha() and question[i][1] in [".", ")", ":"]:
                question[i] = question[i][2:].strip()

        question = [elem for elem in question if elem]

        print("Generated!")
        return {"q": question[0], "type": "mc", "core_topic": topic, "a":  answer, "choices": question[1:]}

    def gen_short_answer(self, topic: str, max_tokens=MIN_SA_TOKENS, **kwargs):
        """Generates a short question based on the given topic and encodes it, and its answer, into json

        :param topic: The topic to generate a question on
        :param max_tokens: The maximum length of the generated question in tokens
        :return: A generated short answer question"""

        if kwargs.get("max_tokens", self.MIN_SA_TOKENS) < self.MIN_SA_TOKENS:
            ValueError(f"Arg 'max_tokens' must be at least {self.MIN_SA_TOKENS}!")

        print(f"Generating short answer question about {topic}...")

        prompt = f"Generate a short answer question about {topic} and an answer."
        question = self.model.complete(prompt, max_tokens=max_tokens, **kwargs).strip("\n").splitlines()
        question[1] = question[1].strip()

        for label in ["a", "answer"]:
            for sep in [".", ")", ":"]:
                if question[1].lower().startswith(label+sep):
                    question[1] = question[1][len(label+sep):].strip()
                    break

        print("Generated!")
        return {"q": question[0], "type": "sa", "core_topic": topic, "a":  question[1]}

    def set_model(self, teacher_model: str = None, chat_model: str = None, eval_model: str = None):
        """Sets the model name for the specified object(s)

        :param teacher_model: The model to use for the teacher
        :param chat_model: The model to use for the chat
        :param eval_model: The model to use for the evaluator"""

        if teacher_model:
            self.MODEL_NAME = teacher_model
            self.model: Model = Model(self.MODEL_NAME)
        if chat_model:
            self.chat.set_model(chat_model)
        if eval_model:
            self.evaluate.set_model(eval_model)

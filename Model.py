import openai
import torch
import json


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Model(metaclass=Singleton):

    def __init__(self, model_name: str):
        self.model_name = model_name
        if not openai.api_key:
            with open("OPENAI_API_KEY.json", "r") as file:
                openai.api_key = json.loads(file.read())["main"]

    def complete_chat(self, prompt: str, chat_history: list[dict[str, str]] = None):
        if self.model_name != "gpt-3.5-turbo":
            raise AttributeError(f"The model type {self.model_name} is not compatible with the chat API.  Try using gpt-3.5-turbo")

        if not chat_history:
            chat_history = []
        if not len(chat_history) or chat_history[0]["role"] != "system":
            chat_history.insert(0, {"role": "system", "content": "You are a helpful assistant."})

        chat_history.append({"role": "user", "content": prompt})

        return openai.ChatCompletion.create(model=self.model_name, messages=chat_history)["choices"][0]["message"]["content"]

    def complete(self, prompt: str, context: dict[str, str] = None, **kwargs):
        """Completes the prompt with additional context considered"""
        if not self.model_name.startswith("text-"):
            raise AttributeError(f"The model type {self.model_name} is not compatible with the complete API.  Try using a base model")

        if not context:
            return openai.Completion.create(model=self.model_name, prompt=prompt, **kwargs)["choices"][0]["text"]

        # Add context values to prompt so model can include them in current response
        context_prompt = "Please complete using the following information:\n\n"
        for ctx_prompt, ctx_completion in context.items():
            context_prompt += f"Q: {ctx_prompt[0]}\nA:{ctx_completion[1]}\n\n"
        context_prompt += f"Q: {prompt}\nA:"

        return openai.Completion.create(model=self.model_name, prompt=context_prompt, **kwargs)["choices"][0]["text"]

    def edit(self, instruction: str, editable: str, **kwargs):
        return openai.Edit.create(model=self.model_name, instruction=instruction, input=editable, **kwargs)

    def embed(self, text: str):
        return torch.tensor(openai.Embedding.create(model=self.model_name, input=text)["data"]["embedding"], dtype=torch.float)

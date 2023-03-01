import openai
import torch
import json


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class Model(Singleton):

    def __init__(self, model_name: str):
        self.model_name = model_name

    def complete(self, prompt: str, context: dict[str, str] = None, **kwargs):
        """Completes the prompt with additional context considered"""
        if not context:
            return openai.Completion.create(model=self.model_name, prompt=prompt, **kwargs)

        # Add context values to prompt so model can include them in current response
        context_prompt = "Please complete using the following information:\n\n"
        for ctx_prompt, ctx_completion in context.items():
            context_prompt += f"Q: {ctx_prompt[0]}\nA:{ctx_completion[1]}\n\n"
        context_prompt += f"Q: {prompt}\nA:"

        return openai.Completion.create(model=self.model_name, prompt=context_prompt, **kwargs)

    def edit(self, instruction: str, editable: str, **kwargs):
        return openai.Edit.create(model=self.model_name, instruction=instruction, input=editable, **kwargs)

    def embed(self, text: str):
        return torch.tensor(openai.Embedding.create(model=self.model_name, input=text)["data"]["embedding"], dtype=torch.float)

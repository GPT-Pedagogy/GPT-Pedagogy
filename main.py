import openai
import json

# main: file-Ol4t15mr9T3Wb7cUl4bEtRDj, ft-zJk1gHZzIgGjnNJjMEs7Zbk8
# test: file-u34CD1bxZx1muf8xwtk4KHr9, ft-c7sHj9Jbg47g7SxfebDE5fJ9


def model_completion(model: str, prompt: str, **kwargs):
    return openai.Completion.create(model=model, prompt=prompt, **kwargs)


def fine_tune_request(model: str, tuning_file: str):
    response = openai.FineTune.create(training_file=tuning_file, model=model)
    print("Fine tuning request response:", response)


if __name__ == "__main__":
    with open("OPENAI_API_KEY.json", "r") as file:
        openai.api_key = json.loads(file.read())["main"]

    # response = openai.Completion.create(model="text-davinci-003", prompt="Say this is a test", temperature=0, max_tokens=7)
    # response = openai.FineTune.list()
    # response = openai.File.create(file=open("data/training.jsonl", "rb"), purpose='fine-tune')
    # response = openai.FineTune.create(training_file="file-u34CD1bxZx1muf8xwtk4KHr9", model="ada") # main: file-Ol4t15mr9T3Wb7cUl4bEtRDj
    # response = openai.FineTune.list_events(id="ft-zJk1gHZzIgGjnNJjMEs7Zbk8")
    # response = openai.Completion.create(model="ada:ft-529-2023-02-19-22-00-52", prompt="oliver", temperature=0, max_tokens=7)
    response = openai.File.list()
    print(response)

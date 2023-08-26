import openai
import json 
import os
# Lisa, make sure to install python-dotenv in the new version
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai.api_key = os.environ['OPENAI_API_KEY']

def chat_completion(prompt,
                    model='gpt-3.5-turbo',
                    api_key=None,
                    system_prompt="You are a helpful assistant",
                    temperature=0.1,
                    top_p=1.0,
                    max_tokens=500):

    if api_key is not None:
      openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model=model,
        temperature = temperature,
        top_p=top_p,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}]
        )

    return response['choices'][0]['message']['content']

def spelling_mistakes(user_writing):
  system_prompt = '''Given the following piece of writing, find all the spelling mistakes and the index positions of each mistake. Output the mistakes as a JSON as such:
  {{"spelling": [<spelling mistake 1>, <spelling mistake 2>, ...]'''

  user_prompt = f"{user_writing}"
  result = chat_completion(prompt=user_prompt, system_prompt=system_prompt, model="gpt-4")
  try:
    mistakes_json = json.loads(result)
  except json.JSONDecodeError:
    print("JSONDecodeError")
    mistakes_json = result
  return mistakes_json

def find_positions(text, words): 
  """find positions of words in text"""
  positions = []
  for word in words:
    p_start = text.index(word)
    p_end = p_start + len(word)
    mistake = text[p_start: p_end]
    print(mistake)
    positions.append((p_start, p_end))
  return position


def mc_questions_json(text, n=5):
  system_prompt = """Given the corpus of text, \
  generate {n} multiple choice questions\
  based on the contents of the text. The goal of the these questions is to \
  quiz the reader. Make sure to randomize \
  the order of the answers for each question and evenly distribute the correct \
  answer across the options. Each question should be different and not repeated. \
  Format the questions in JSON as follows, make sure to use double quotes:\n \
  {{\
    "questions": [\
      {{\
        "question": "Who did X?",\
        "options": [\
         "A) Answer 1",\
         "B) Answer 2",\
         "C) Answer 3",\
         "D) Answer 4"
        ],\
        "correct_answer": "C) Answer 3", \
        "explanation": "Explanation of the correct answer" \
      }},\
      // More questions...\
    ]\
  }}
  """
  user_prompt = f"The text delimited in triple backticks:```{text}```"
  result = chat_completion(prompt=user_prompt,
                           system_prompt=system_prompt,
                           temperature=0)
  # result = chat_model(chat_prompt.format_prompt(n=n, text=text).to_messages())
  try:
    json_result = json.loads(result)
  except Exception as e:
    print(f"Error: {e}")
    json_result = result
  return json_result

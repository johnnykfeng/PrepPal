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
  system_prompt = '''Given the following piece of writing, \
    find all the spelling mistakes and the index positions of each mistake. \
      Output the mistakes as a JSON as such:
  {{"spelling": [<spelling mistake 1>, <spelling mistake 2>, ...]'''

  user_prompt = f"{user_writing}"
  result = chat_completion(prompt=user_prompt, system_prompt=system_prompt, model="gpt-4")
  try:
    mistakes_json = json.loads(result)
  except json.JSONDecodeError:
    print("JSONDecodeError")
    mistakes_json = result
  return mistakes_json

def find_word_positions(text, words):
  """find positions of words in text"""
  positions = []
  for word in words:
    p_start = text.index(word)
    p_end = p_start + len(word)
    mistake = text[p_start: p_end]
    print(mistake)
    positions.append((p_start, p_end))
  return positions

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

def fitb_generate(reading_task, n=3, test_choice='ielts'):
  system_prompt = f'''Given the reading task for {test_choice.upper()} \
  english proficiency test delimted in \
  triple backticks ```, generate {n} fill in the blank exercises \
  based on the contents of the text. The intent of these exercises \
  is to quiz the reader. Format the output as a JSON file as follows:\
  [{{"incomplete_sentence": "<sentence with missing word as blank `___`>", "correct_word": \
  [<list of correct word or words>]}}]
  '''
  user_prompt = f'Here is the reading task: ```{reading_task}```'
  result = chat_completion(prompt=user_prompt,
                            system_prompt=system_prompt,
                            temperature=0)
  try:
    fitb = json.loads(result)
  except Exception as e:
    print("JSONDecodeError")
    return result

  return fitb

def get_writing_score(writing_text, task_question, test_choice="ielts"):
  """
  Calculate the writing score based on a given test type (IELTS or CELPIP).

  Parameters:
  - writing_text (str): The writing sample to be evaluated.
  - task_question (str): The specific question or task related to the writing test.
  - test_choice (str, optional): The type of the test being used for evaluation. Default is "ielts".
    Supported test types are "ielts" and "celpip".

  Returns:
  - result: The score or evaluation result for the provided writing test.

  Note:
  - If an unsupported test type is provided, the function will indicate "Invalid test choice".
  """

  # 2 different tests
  ielts_test = """
  You are a profesional IELTS writing task examer for General Training.
  Score the following text and provide subscore for each of the 4 IELTS criteria.Criterias:"Task achievement", \
  "Coherence and cohesion","Lexical resource","Grammatical range and accuracy".
  Writing task questions:\n{question_text}
  Writing task answer:\n{answer_text}"
  Output overall score and subscore in a dictionary format. Round the score to one decimal place with the first decimal digit only being 0 or 5.
  """
  celpip_test = """
  You are a professional CELPIP writing task examer.
  Score the following text and provide subscore for each of the 4 criteria.Criterias:"Content/Coherence", \
  "Vocabulary","Readability","Task Fulfillment".\
  Writing task questions:\n{question_text}
  Writing task answer:\n{answer_text}
  Output the overall score and subscore in a dictionary format. Round the score to integer.
  """

  # Switch between tests based on test_choice value
  if test_choice.lower() == "ielts":
      prompt_template = ielts_test
  elif test_choice.lower() == "celpip":
      prompt_template = celpip_test
  else:
      prompt_template = "Invalid test choice"

  # Apply the selected test, insert the writing text, and print the result
  scoring_prompt = prompt_template.format(question_text=task_question, answer_text=writing_text)
  # print(f"{scoring_prompt = }")
  result = chat_completion(scoring_prompt)

  try: # convert string to JSON
    result = json.loads(result)
  except JSONDecodeError:
    print("JSONDecoderError")

  return result
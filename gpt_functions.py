import json 
import os
import re
import pandas as pd
from pydantic import BaseModel
from openai import OpenAI

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def chat_completion(prompt,
                    model='gpt-4o',
                    api_key=None,
                    system_prompt="You are a helpful assistant",
                    temperature=0.1,
                    top_p=1.0,
                    max_tokens=500):

    if api_key is not None:
      openai.api_key = api_key

    response = client.chat.completions.create(
        model=model,
        temperature = temperature,
        top_p=top_p,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}]
        )

    # return response['choices'][0]['message']['content']
    return response.choices[0].message.content

def spelling_finder(user_writing, chat_model="gpt-3.5-turbo"):
  # helper function, find spelling mistakes
  # works much better with gpt-4
  system_prompt = '''Given the following piece of writing, \
  find all the spelling mistakes in the text. \
  Output the mistakes as JSON with the following format:\
  {{"mistakes": ["<spelling mistake 1>", "<spelling mistake 2>", ...]\
    "correction":["<correct spelling 1>", "<correct spelling 2>, ...]}}'''

  user_prompt = f"{user_writing}"
  result = chat_completion(prompt=user_prompt, 
                           system_prompt=system_prompt, 
                           model=chat_model)
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

def wrap_words_in_text(text, word_list):
    for word in word_list:
        text = text.replace(word, f"**[{word}]**")
        # text = text.replace(word, f"<ins>{word}</ins>")
    return text

def contains_word(s, word):
    return re.search(f'\\b{word}\\b', s) is not None

def same_meaning(word1, word2, model ='gpt-3.5-turbo'):

  system = """You are a helpful assistant that helps students practice for their english proficieny exams. \
  Given the following two words enclosed in double square brackets [[]], \
  determine if they are synonyms or have the similar meaning. \
  Format the output as 'True' or 'False', nothing else. 'True' if they have the similar meaning, \
  'False' otherwise."""

  user_prompt = f"Two words to compare: [[{word1}]], [[{word2}]]"
  result = chat_completion(user_prompt, system_prompt = system, model = model)

  if contains_word(result, "True"):
    return True
  else:
    return False

class MCQuestion(BaseModel):
  question: str
  options: list[str]
  correct_answer: str
  explanation: str

def mc_questions_json(text, n=5):
  """Generate multiple choice questions based on the contents of the text.
  """
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

def fitb_generate(reading_task, 
                  n=3, 
                  test_choice='ielts', 
                  model='gpt-3.5-turbo',
                  temperature = 0.4):
  """Generate fill in the blank exercises based on the contents of the text.

  Args:
      reading_task (str): long form text like a reading task.
      n (int, optional): Number of exercises to generate. Defaults to 3.
      test_choice (str, optional): _description_. Defaults to 'ielts'.
      model (str, optional): _description_. Defaults to 'gpt-3.5-turbo'.
      temperature (float, optional): _description_. Defaults to 0.4.

  Returns:
      _type_: _description_
  """
  
  system_prompt = f'''Given the reading task for {test_choice.upper()} \
  english proficiency test delimted in \
  triple backticks ```, generate {n} fill in the blank exercises \
  based on the contents of the text. The intent of these exercises \
  is to quiz the reader. Do not copy sentences from the given reading task, \
  create new sentence that relate to the content of the reading. \
  Format the output as a JSON file as follows:\
  [{{"incomplete_sentence": "<sentence with missing word as `___`>", "missing_word": \
  <missing word from the incomplete sentence>}}]
  '''
  user_prompt = f'Here is the reading task: ```{reading_task}```'
  result = chat_completion(prompt=user_prompt,
                            system_prompt=system_prompt,
                            model=model,
                            temperature=temperature)
  try:
    fitb = json.loads(result)
  except Exception as e:
    print("JSONDecodeError")
    return result

  return fitb

# TODO: fix this function, use the new structured output feature
class WritingScoreIELTS(BaseModel):
    task_achievement_score: int
    coherence_and_cohesion_score: int
    lexical_resource_score: int
    grammatical_range_and_accuracy_score: int
    overall_score: int
    
class WritingScoreCELPIP(BaseModel):
    content_coherence_score: int
    vocabulary_score: int
    readability_score: int
    task_fulfillment_score: int
    overall_score: int


def get_writing_score(writing_text, task_question, test_choice="ielts"):
  system_prompt = f"""
  You are a professional {test_choice.upper()} writing task examiner. You are given a writing task question and a writing task answer.
  You need to score the writing task answer based on the {test_choice.upper()} writing task criteria: 
  Task achievement, Coherence and cohesion, Lexical resource, Grammatical range and accuracy, and Overall score.
  Each score should be between 0 and 10.
  """
  user_prompt = f"Writing task questions: {task_question}\nWriting task answer: {writing_text}"
  response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages = [
      {'role': 'system', 'content': system_prompt},
      {'role': 'user', 'content': user_prompt}
    ],
    response_format=(WritingScoreIELTS if test_choice == "ielts" else WritingScoreCELPIP),
    temperature=0
  )
  return response.choices[0].message.parsed

def grammar_judge(sentence, model = "gpt-3.5-turbo"):
  # herlper function, find grammar error.
    system_prompt = '''
                    Determine if the sentence has grammar mistakes. /
                    If the sentence has grammar mistakes, output 'True' , /
                    otherwise output 'False'. Only output true or false, nothing else.
                    '''
    user_prompt = f"{sentence}"
    result = chat_completion(prompt = user_prompt,
                             system_prompt = system_prompt,
                             model = model,
                             temperature=0)

    return result
  
def correct_sentence(sentence):
  # helper function, correct the sentences from grammar error.
    system_prompt = '''
                    You are an ai assistant that helps students \
                    correct and practice their english writing, \
                    the following sentence has grammar mistakes, \
                    correct them and output only the corrected sentence, nothing else.
                    '''
    user_prompt = f"{sentence}"
    result = chat_completion(prompt = user_prompt,
                             system_prompt = system_prompt,
                             model = "gpt-3.5-turbo",
                             temperature=0)

    return result
  
def find_sentence_positions(para, sentence):
  # helper function, help find the position of the sentences
    """find positions of words in text"""
    positions = []
    p_start = para.index(sentence)
    p_end = p_start + len(sentence)
    mistake = para[p_start: p_end]
    # print(mistake)
    positions.append((p_start, p_end))
    return positions
  
def split_into_sentences(text):
    sentences = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', text)
    return sentences
  
def full_grammar_corrector(text):
  # main function
  # split text into sentences
  # run the grammar_judge on each sentence
    sentence = text.split('\n')

    sentences = []
    sentence_lst = []
    for i in sentence:
        s = re.findall(r"[^.!?]+", i)
        sentences = sentences + s
    for s in sentences:
        if s != ' ':
            sentence_lst.append(s)
            
    sentences = split_into_sentences(text)

    df = []
    for s in sentence_lst:
        grammar = grammar_judge(s)
        if grammar == "True":
            corrected = correct_sentence(s)
            if corrected == s + ".":
                corrected = 'None'
                grammar = 'False'
        else:
            corrected = 'None'
            grammar = 'False'
        sentence_positions = find_sentence_positions(text, s)
        df.append({
                        'Sentences': s,
                        'Error': grammar,
                        'Corrected': corrected,
                        'Position': sentence_positions})
    return pd.DataFrame(df)
  
  
class SuggestionsIELTS(BaseModel):
    task_achievement_improvements: str
    coherence_and_cohesion_improvements: str
    lexical_resource_improvements: str
    grammatical_range_and_accuracy_improvements: str
    
class SuggestionsCELPIP(BaseModel):
    content_coherence_improvements: str
    vocabulary_improvements: str
    readability_improvements: str
    task_fulfillment_improvements: str
    
  
def create_suggestions(user_writing, test_choice = "ielts", model = "gpt-4o-mini"):
    if test_choice == "ielts":
      criteria = "Task achievement, Coherence and cohesion, Lexical resource, and Grammatical range and accuracy."
      response_format = SuggestionsIELTS
    elif test_choice == "celpip":
      criteria = "Content/Coherence, Vocabulary, Readability, and Task Fulfillment."
      response_format = SuggestionsCELPIP
    system_prompt = f'''
                    You are a professional {test_choice.upper()} writing examiner, \
                    provide suggestions for improving writing on the following paragraph \
                    based on the four criteria in {test_choice.upper()} writing, \
                    {criteria} \
                    Output only one paragraph of suggestions for each criteria.
                    '''
    user_prompt = f"{user_writing}"
    response = client.beta.chat.completions.parse(
      model=model,
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ],
      response_format=response_format,
      temperature=0)  

    return response.choices[0].message.parsed
   
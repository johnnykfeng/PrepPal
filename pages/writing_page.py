import random
import json
import pandas as pd
import openai
import streamlit as st
from PIL import Image
from gpt_functions import (get_writing_score, 
                           spelling_finder, 
                           find_word_positions, 
                           wrap_words_in_text,
                           full_grammar_corrector,
                           create_suggestions)

from components.user_apikey import user_input_apikey

image = Image.open(r'logo.jpeg')

st.image(image)

# module that allows user to enter API key on the sidebar
st.session_state['api_key'], st.session_state['api_key_check'] = user_input_apikey()

openai.api_key = st.session_state['api_key']


st.title("Writing test")
st.subheader("Pass your English Proficiency test with the power of AI")

test_choice = st.radio("What are you studying for?",
                       options=["IELTS", "CELPIP"])

subject = test_choice

st.markdown(f"PrepPal will help you study for **{test_choice}**")

def writing_task(sample):
    task_container.caption(
        "Write an essay based on the following topic. Keep it under 250 words.")
    task_container.write("**Essay Topic:**")
    task_container.write(sample.read())
    return sample

if 'show_task' not in st.session_state:
    st.session_state['show_task'] = False

if 'task_question' not in st.session_state:
    st.session_state['task_question'] = None
    
if 'user_writing' not in st.session_state:
    st.session_state['user_writing'] = None

if 'count' not in st.session_state:
	st.session_state.count = 0
 
if 'score_json' not in st.session_state:
    st.session_state['score_json'] = None

with st.sidebar:
    with st.expander("Debug session state"):
        st.write(st.session_state)

def increment_counter():
	st.session_state.count += 1
 
if st.button("Get writing task", on_click=increment_counter):
    st.session_state['show_task'] = True
    
if st.session_state['show_task']:
    if st.session_state.count > 5:
        st.session_state.count = 1
    # grabs sample based on {subject} and {n}
    n = st.session_state.count
    sample = open(f'tasks_dataset/{subject}_writing_tasks/task{n}.txt', 'r',
              encoding="utf8")
    task_container = st.container()
    writing_task(sample)
    st.session_state["task_question"] = open(f'tasks_dataset/{subject}_writing_tasks/task{n}.txt', 'r',
            encoding="utf8").read()
    
else:
    st.markdown("Push button")

input_text = st.text_area("Enter your writing here", height = 200)
st.session_state["user_writing"] = input_text


st.subheader(f"Score based on {test_choice} criteria")

if st.button("Evaluate my writing"):
    score_json = get_writing_score(st.session_state.user_writing,
                               st.session_state.task_question,
                               test_choice=test_choice)
    st.session_state['score_json'] = score_json

if st.session_state['score_json'] is not None:
    st.write(st.session_state['score_json'])


st.subheader("Spelling")
spelling_err = None

find_spelling_errors = st.checkbox("Find Spelling Errors")
if find_spelling_errors:
    if st.session_state.user_writing != "None" or st.session_state.user_writing != "":
        spelling_err = spelling_finder(st.session_state.user_writing)

    with st.expander("List"):
        if spelling_err is not None:
            st.write(pd.DataFrame(spelling_err))

    with st.expander("Highlighted"):
        writing = st.session_state.user_writing
        highlighted = wrap_words_in_text(writing, spelling_err['mistakes'])
        st.markdown(highlighted)
    
st.subheader("Grammar Errors")
grammar_err = None
find_grammar_errors = st.checkbox("Find Grammar Errors")
if find_grammar_errors:
    if st.session_state.user_writing != "None" or st.session_state.user_writing != "":
        grammar_err = full_grammar_corrector(st.session_state.user_writing)
    
    with st.expander("List"):
        if grammar_err is not None:
            st.dataframe(grammar_err[["Sentences", "Corrected"]])


st.subheader("Suggestion Improvements")
generate_suggestions = st.checkbox("Generate suggestions")

if generate_suggestions:
    if st.session_state.user_writing != "None" or st.session_state.user_writing != "":
        
        suggestions = create_suggestions(st.session_state.user_writing, 
                                         model="gpt-4o-mini")
        
        st.write(suggestions)
        
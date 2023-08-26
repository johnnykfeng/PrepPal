import streamlit as st
import random
import json
from gpt_functions import get_writing_score

from st_pages import Page, show_pages, add_page_title

show_pages(
    [
        Page("app.py", "Writing test", "📝"),
        Page("pages/reading.py", "Reading test", "📖")
    ]
)

st.title("PrepPal")
st.subheader("Pass your English test with the power of AI")

test_choice = st.radio("What are you studying for?",
                       options=["IELTS", "CELPIP"])

subject = test_choice

st.markdown(f"PrepPal will help you study for **{test_choice}**")

# s = "0"

def writing_task(sample):
    task_container.write("Write an essay based on the following topic")
    # ar_container.subheader(f"Academic Reading test 1 - section 1 practice test")
    task_container.caption(
        "You are allocated 40 minutes to write it. \
            Your essay must contain at least 250 words.")
    task_container.write(sample.read())
    return sample

if 'task_question' not in st.session_state:
    st.session_state['task_question'] = "None"
    
if 'user_writing' not in st.session_state:
    st.session_state['user_writing'] = "None"

if 'count' not in st.session_state:
	st.session_state.count = 0

def increment_counter():
	st.session_state.count += 1
 
if st.button("Get writing task", on_click=increment_counter):
    if st.session_state.count > 5:
        st.session_state.count = 1
    # grabs sample based on {subject} and {n}
    n = st.session_state.count
    st.text(f"{n = }")
    sample = open(f'{subject}_writing_tasks/task{n}.txt', 'r',
              encoding="utf8")
    # n += 1
    task_container = st.container()
    writing_task(sample)
    st.session_state["task_question"] = open(f'{subject}_writing_tasks/task{n}.txt', 'r',
            encoding="utf8").read()
    # n += 1
    
else:
    st.markdown("Push button")

input_text = st.text_area("Enter your writing here", height = 200)
st.session_state["user_writing"] = input_text


st.subheader("Score")
with st.expander("Writing Task"):
    st.write(st.session_state.task_question)
with st.expander("Submitted writing"):
    st.write(st.session_state.user_writing)

if st.button("Evaluate my writing"):
    score_json = get_writing_score(st.session_state.user_writing,
                               st.session_state.task_question,
                               test_choice=test_choice)
    st.write(score_json)

    
    
st.subheader("List of mistakes")
with st.expander("expand list"):
    st.write("list of mistakes")
st.subheader("Suggestions")







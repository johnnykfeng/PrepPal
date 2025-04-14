import streamlit as st
import random
import json
from gpt_functions import (generate_mc_questions,
                           fitb_generate, 
                           find_word_positions,
                           same_meaning)

if 'sample_text' not in st.session_state:
    st.warning("---> Resetting sample_text")
    st.session_state.sample_text = None
    
if 'count' not in st.session_state:
	st.session_state.count = 0

def increment_counter():
	st.session_state.count += 1
    
st.title("Reading Comprehension")
st.subheader("Pass your English test with the power of AI")

test_choice = st.radio("What are you studying for?",
                       options=["IELTS", "CELPIP"])


def get_reading_task(sample, test_choice):
    ar_container.caption(f"Spend about 20 minutes reading the following {test_choice.upper()} reading task.")
    ar_container.write(sample.read())
    return sample.read()

if st.button("Get reading task", on_click=increment_counter):
    if st.session_state.count > 5:
        st.session_state.count = 1
        
    n = st.session_state.count
    sample = open(f'tasks_dataset/{test_choice}_reading_tasks/sample_{n}.txt', 'r',
              encoding="utf8")
    task_container = st.container()
    ar_container = st.container()
    get_reading_task(sample, test_choice)
    
    st.session_state.sample_text = open(f'tasks_dataset/{test_choice}_reading_tasks/sample_{n}.txt', 'r',
            encoding="utf8").read()
    
else:
    if st.session_state.sample_text is not None:
        with st.expander("OPEN LAST READING TASK", expanded=True):
            st.write(st.session_state.sample_text)
    else: 
        st.markdown("☝️ **Push button to start**")

#####################################
## MULTIPLE CHOICE QUESTIONS ##
##################################
st.subheader("Multiple Choice Quiz")

# maps integers to letters for keeping track of answers
int2letter = {0:"A", 1:"B", 2:"C", 3:"D"}
letter2int = {"A":0, "B":1, "C":2, "D":3}
if "current_question" not in st.session_state:
    st.session_state.questions_json = None
    st.session_state.answers = {} 
    st.session_state.current_question = 1 # keeps track of current question number
    st.session_state.questions = [] 
    st.session_state.right_answers = 0 # count of right answers
    st.session_state.wrong_answers = 0 # count of wrong answers

def reset_answers():
    st.session_state.answers = {} 
    st.session_state.right_answers = 0 # count of right answers
    st.session_state.wrong_answers = 0 # count of wrong answers
    st.session_state.current_question = 1 # keeps track of current question number

if "questions_json" not in st.session_state:
    st.session_state.questions_json = None

if st.session_state.sample_text is not None:
    column1, column2 = st.columns([1, 1])
    with column2:
        n_input = st.number_input("Number of questions to generate.", 
                                min_value=1,
                                max_value=8, 
                                value=5)
    n_int = int(n_input)

    @st.cache_data(show_spinner = f"Generating {n_int} questions from summary...")
    def generate_questions(sample_text, n_int):
        return generate_mc_questions(sample_text, n=n_int)

    with column1:
        if st.button("Generate Multiple Choice Questions"):
            questions_json = generate_questions(st.session_state.sample_text, n_int)
            st.session_state.questions_json = questions_json
   
def display_question():
    # Handle first case
    questions_json = st.session_state.questions_json
    if len(st.session_state.questions) == 0:
        try:
            first_question = questions_json.questions[0]
        except Exception as e:
            st.error(e)
            return
        st.session_state.questions.append(first_question)

    # Disable the submit button if the user has already answered this question
    submit_button_disabled = st.session_state.current_question in st.session_state.answers

    # Get the current question from the questions list
    MCObject = st.session_state.questions[st.session_state.current_question-1]

    # Display the question prompt
    st.subheader(f"{st.session_state.current_question}. {MCObject.question}")

    # Use an empty placeholder to display the radio button question_container
    question_container = st.empty()

    # Display the radio button question_container and wait for the user to select an answer
    user_answer = question_container.radio("Please select an answer:", 
                                            options = ["A", "B", "C", "D"],
                                            format_func=lambda x: f"{x} - {MCObject.options[letter2int[x]].option_text}",
                                            key=st.session_state.current_question)
    st.write(f"**You selected:** {user_answer} - {MCObject.options[letter2int[user_answer]].option_text}")

    # Display the submit button and disable it if necessary
    submit_button = st.button("Submit", disabled=submit_button_disabled)

    # If the user has already answered this question, display their previous answer
    if st.session_state.current_question in st.session_state.answers:
        user_choice = st.session_state.answers[st.session_state.current_question]
        question_container.radio(
            "Your answer:",
            [f"{int2letter[option.index]} - {option.option_text}" for option in MCObject.options],
            key=float(st.session_state.current_question),
            index=letter2int[user_choice],
        )

    user_answer_index = letter2int[user_answer] # answer_index is an int (1-4)
    # st.write(f"MCObject: {MCObject}")
    # st.write(f"answer_index: {user_answer_index}")
    # st.write(f"MCObject.correct_answer_index: {MCObject.correct_answer_index}")
    def count_answer():
        if user_answer_index == MCObject.correct_answer_index:  # match the whole answer string
            st.session_state.right_answers += 1
        else:
            st.session_state.wrong_answers += 1

    def show_answer():
        # Check if the user's answer is correct and update the score
        if user_answer_index == MCObject.correct_answer_index:
            st.success("Correct!")
        else:
            st.error(f"Sorry, the correct answer was {int2letter[MCObject.correct_answer_index]}.")

        # Show an expander with the explanation of the correct answer
        with st.expander("Explanation"):
            st.write(MCObject.explanation_of_correct_answer)

    # If the user clicks the submit button, check their answer and show the explanation
    if submit_button:
        # Record the user's answer in the session state
        st.session_state.answers[st.session_state.current_question] = int2letter[user_answer_index]
        st.caption(f"You submitted choice {int2letter[user_answer_index]}")
        count_answer()
        show_answer()

    elif submit_button_disabled:
        show_answer()

def next_question():
    questions_json = st.session_state.questions_json
    # Move to the next question in the questions list
    if st.session_state.current_question == n_int:
        st.caption("No more questions")
        return
    
    st.session_state.current_question += 1

    # If we've reached the end of the questions list, get a new question
    if st.session_state.current_question > len(st.session_state.questions) - 1:
        try:
            next_question = questions_json.questions[st.session_state.current_question-1]
        except Exception as e:
            st.error(e)
            st.session_state.current_question -= 1
            return
        st.session_state.questions.append(next_question)
        # st.experimental_rerun()
        
# Define a function to go to the previous question
def prev_question():
    # Move to the previous question in the questions list
    if st.session_state.current_question > 1:
        st.session_state.current_question -= 1

if st.session_state.questions_json is not None:
    # Create a 3-column layout for the Prev/Next buttons and the question display
    col1, col2, col3 = st.columns([1, 4, 1])

    # Add a Prev button to the left column that goes to the previous question
    with col1:
        if col1.button("⬅️ Prev"):
            prev_question()

    # Add a Next button to the right column that goes to the next questionG
    with col3:
        if col3.button("Next ➡️"):
            next_question()

    # Display the actual quiz question
    with col2:
        display_question()
    
with st.sidebar: # update sidebar with newly submitted answers
    st.subheader("Multiple choice score:")
    # display counter for right and wrong answers
    st.caption(f"Right answers: {st.session_state.right_answers}")
    st.caption(f"Wrong answers: {st.session_state.wrong_answers}")

# if st.button("Clear All Cache"):
#     st.cache_data.clear()
#     st.rerun()

if st.sidebar.button("🔄 Reset quiz"):
    reset_answers()
    st.rerun()

####################################
####  END OF MULTIPLE CHOICE QUESTIONS ####
##################################

###########################################
#### FILL IN THE BLANK (FITB) EXERICES ####
###########################################
st.subheader("Fill-In-The-Blank Exercises")

if "fitb" not in st.session_state:
    print("---> resetting FITB")
    st.session_state["fitb"] = None

if st.session_state.sample_text is not None:
    column1, column2 = st.columns([1, 1])
    with column2:
        n_fitb = st.number_input("How many FITB questions to generate.", 
                                min_value=1,
                                max_value=5, 
                                value=3)
    n_fitb = int(n_fitb)

    with column1:
        if st.button("Generate FITB questions"):
            fitb_json = fitb_generate(st.session_state.sample_text, n=n_fitb)
            st.session_state["fitb"] = fitb_json

if st.session_state["fitb"] is not None:
    synonyms_allowed = st.checkbox("Similar words allowed", value=True)
    for i, exercise in enumerate(st.session_state["fitb"].questions):
        st.markdown(f"**Exercise #{i+1}**")
        st.write(exercise.incomplete_sentence)
        answer = st.text_input(f"Input correct word", key=f"fitb_answer_{i}")
        if answer == "":
            pass
        elif answer == exercise.missing_word:
            st.success("✅ Correct")
        else:
            if synonyms_allowed and same_meaning(answer, exercise.missing_word):
                st.info("✅ Good Enough")
            else:
                st.warning("⭕ Try again")


with st.sidebar:
    with st.expander("Debug session state"):
        st.write(st.session_state)

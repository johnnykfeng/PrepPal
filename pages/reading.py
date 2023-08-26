import streamlit as st
import random
from langchain.chat_models import ChatOpenAI
from gpt_functions import mc_questions_json

st.title("Reading Comprehension")
st.subheader("Pass your English test with the power of AI")

test_choice = st.radio("What are you studying for?",
                       options=["IELTS", "CELPIP"])

subject = test_choice
n = random.randint(1, 5)

st.text(f"We will help you study for {test_choice}")

s = "0"

# Random Sample of chosen subject
sample = open(f'{subject}_reading_tasks/sample_{n}.txt', 'r', encoding="utf8")
# sample = random.choice

def reading_task(sample):
    task_container.write("Read the article below to start your assessment")
    # ar_container.subheader(f"Academic Reading test 1 - section 1 practice test")
    ar_container.caption(
        "This is the first section of your IELTS Reading test. \
            You should spend about 20 minutes on Questions 1–13, \
                which are based on Reading Passage 1 below.")
    ar_container.write(sample.read())
    return sample

# text_for_making_quiz = None
if st.button("Get reading task"):
    # display reading task
    # load the reading into a variable
    task_container = st.container()
    ar_container = st.container()
    sample = reading_task(sample)
#    text_for_making_quiz = sample.read()
else:
    st.markdown("Push button")

st.subheader("Score Form")

with st.form("my_form"):
   st.write("Please enter your answer below, kindly separate by commas")
   st.text_input("Please enter the answer of questions 1-6")
   st.text_input("Please enter the answer of questions 7-12")
   st.text_input("Please enter the answer of questions 13-18")
   st.text_input("Please enter the answer of questions 19-25")

   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
       s = random.randint(8, 22)
       st.write("Your score is:", s)

"""if st.button("Get Score"):
        s = random.randint(8, 22)
        ar_container.write(f"{s}")
"""
#####################################
## MC QUESTIONS ##
##################################


n_input = st.number_input("Number of questions to generate.", 
                              min_value=1,
                              max_value=10, 
                              value=3)
n_int = int(n_input)

@st.cache_data(show_spinner = f"Generating {n_int} questions from summary...")
def generate_questions(text, n_int):
    return mc_questions_json(text, n=n_int)

# maps integers to letters for keeping track of answers
int2letter = {0:"A", 1:"B", 2:"C", 3:"D"}
letter2int = {"A":0, "B":1, "C":2, "D":3}
if "current_question" not in st.session_state:
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

questions_json = generate_questions(sample.read(), n_int)

def display_question():
    # Handle first case
    if len(st.session_state.questions) == 0:
        try:
            first_question = questions_json['questions'][0]
        except Exception as e:
            st.error(e)
            return
        st.session_state.questions.append(first_question)

    # Disable the submit button if the user has already answered this question
    submit_button_disabled = st.session_state.current_question in st.session_state.answers

    # Get the current question from the questions list
    question = st.session_state.questions[st.session_state.current_question-1]

    # Display the question prompt
    st.subheader(f"{st.session_state.current_question}. {question['question']}")

    # Use an empty placeholder to display the radio button question_container
    question_container = st.empty()

    # Display the radio button question_container and wait for the user to select an answer
    user_answer = question_container.radio("Please select an answer:", 
                                            question["options"],
                                            key=st.session_state.current_question)

    # Display the submit button and disable it if necessary
    submit_button = st.button("Submit", disabled=submit_button_disabled)

    # If the user has already answered this question, display their previous answer
    if st.session_state.current_question in st.session_state.answers:
        user_choice = st.session_state.answers[st.session_state.current_question]
        question_container.radio(
            "Your answer:",
            question["options"],
            key=float(st.session_state.current_question),
            index=letter2int[user_choice],
        )

    answer_index = question["options"].index(user_answer) # answer_index is an int (1-4)
    def count_answer():
        if user_answer == question["correct_answer"]:  # match the whole answer string
            st.session_state.right_answers += 1
        else:
            st.session_state.wrong_answers += 1

    def show_answer():
        # Check if the user's answer is correct and update the score
        if user_answer == question["correct_answer"]:
            st.write("Correct!")
        else:
            st.write(f"Sorry, the correct answer was {question['correct_answer']}.")

        # Show an expander with the explanation of the correct answer
        with st.expander("Explanation"):
            st.write(question["explanation"])

    # If the user clicks the submit button, check their answer and show the explanation
    if submit_button:
        # Record the user's answer in the session state
        st.session_state.answers[st.session_state.current_question] = int2letter[answer_index]
        st.caption(f"You submitted choice {int2letter[answer_index]}")
        count_answer()
        show_answer()

    elif submit_button_disabled:
        show_answer()

    # Display the current score


    # Define a function to go to the next question
def next_question():
    # Move to the next question in the questions list
    if st.session_state.current_question == n_int:
        st.caption("No more questions")
        return
    
    st.session_state.current_question += 1

    # If we've reached the end of the questions list, get a new question
    if st.session_state.current_question > len(st.session_state.questions) - 1:
        try:
            next_question = questions_json['questions'][st.session_state.current_question-1]
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
    with st.expander("Questions JSON"):
        st.json(questions_json)
    with st.expander(f"Submitted answers"):
        st.write(st.session_state.answers)
    # display counter for right and wrong answers
    st.success(f"Right answers: {st.session_state.right_answers}")
    st.error(f"Wrong answers: {st.session_state.wrong_answers}")

if st.sidebar.button("🔄 Reset quiz"):
    reset_answers()
    st.experimental_rerun()
    
####################################
####  END_OF_QUIZ
##################################




st.subheader("List of mistakes")
with st.expander("expand list"):
    st.write("Question 3")

st.subheader("Suggestions")
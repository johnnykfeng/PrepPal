import streamlit as st

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

st.text(f"We will help you study for {test_choice}")

sidebar_container = st.sidebar.empty()
task_container = st.container()
# empty_text = st.markdown()
if st.button("Get writing task"):
    
    task_container.markdown("Write an essay about the awesomeness of Canada")
else:
    task_container.markdown("Push button")

input_text = st.text_area("Enter your writing here", height = 200)

st.subheader("Score")
with st.container():
    st.empty()
    
st.subheader("List of mistakes")
with st.expander("expand list"):
    st.write("list of mistakes")
st.subheader("Suggestions")







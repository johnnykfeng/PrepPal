import streamlit as st


pg = st.navigation([st.Page("pages/writing_page.py", title="Writing test", icon="📝"),
                   st.Page("pages/reading_page.py", title="Reading test", icon="📖")])
pg.run()
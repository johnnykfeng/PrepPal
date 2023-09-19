import streamlit as st
import openai

def api_test(api_key, model="gpt-3.5-turbo"): 
    try:
        output = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            api_key=api_key,
            temperature=0,
            messages=[{"role": "user", "content": "Hello"}]
        )
    except Exception as e:
        print(f"{str(e)}")
        return False
    
    return True

# --- Displaying session state info on sidebar --- #
# sidebar_placeholder = st.sidebar.empty()
# def sidebar_session_state(sidebar_placeholder=sidebar_placeholder):
def sidebar_session_state():
    sidebar_placeholder = st.sidebar.empty()
    
    with sidebar_placeholder.expander("Session State", expanded=False):

        st.markdown(f"🔑 **API Key**:\n{st.session_state['api_key'][:5]}... ")
        
        if st.session_state['api_key_check']:
            st.markdown("✅ Key is valid ")
        else:
            st.markdown("❌ Key is invalid ")

def user_input_apikey():
    # --- ENTERING API KEY --- #
    with st.sidebar.form('myform', clear_on_submit=False):
        # initialize session states
        if "api_key" not in st.session_state:
            st.session_state['api_key'] = "None"
            st.session_state['api_key_check'] = False

        input_key = st.text_input('🔑 Enter your OpenAI API Key', 
                                    type='password', 
                                    disabled=False)
        
        submitted = st.form_submit_button('Submit your key',
                                        help = "Click here to submit your API key.",  
                                        disabled=False )

        if submitted: # trigger when submit button is clicked
            st.session_state['api_key'] = input_key
            # test if API key is valid
            if api_test(st.session_state['api_key']): 
                st.session_state['api_key_check'] = True
                st.success("✅ API Key is valid")
            else:
                st.session_state['api_key_check'] = False
                st.error("❌ API Key is invalid")
                
        # give warning message if not valid
        # if (not st.session_state['api_key_check']) and (st.session_state['api_key'] != "None"):
        #     st.warning("Please enter a valid OpenAI API Key")
        
        sidebar_session_state() # display new session state info on sidebar

        return st.session_state['api_key'], st.session_state['api_key_check']
        
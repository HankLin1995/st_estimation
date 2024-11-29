import streamlit as st
import requests
import time

@st.dialog("回饋表單")
def Feedback():

    # with st.expander(":mega: 意見回饋"):

        if 'submitted' not in st.session_state:
            st.session_state.submitted = False

        with st.form("feedback",True):

            username = st.text_input(":small_blue_diamond: 姓名")
            email = st.text_input(":small_blue_diamond: 電子郵件")
            txt = st.text_area(":small_blue_diamond: 內容")

            if st.form_submit_button("送出"):

                # print(storeMSG(username, email, txt))
                # st.balloons()
                st.info("功能開發中~")#謝你的意見回復!")

                time.sleep(2)
                st.rerun()


def storeMSG(username, email, txt):

    GAS_URL = st.secrets.GAS_URL_NOTIFY

    data = {
        'username': username,
        'email': email,
        'content': txt
    }

    try:
        response = requests.post(GAS_URL, json=data)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        # print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return {'success': False, 'error': str(http_err)}
    except Exception as err:
        print(f'Other error occurred: {err}')
        return {'success': False, 'error': str(err)}

with open("./md/SP.md", "r", encoding="utf-8") as file:
    markdown_text = file.read()

with st.container(border=True):
    st.markdown(markdown_text)

if st.sidebar.button("回饋表單", type="primary"):
    Feedback()


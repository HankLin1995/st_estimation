import streamlit as st

with open("./md/SP.md", "r", encoding="utf-8") as file:
    markdown_text = file.read()

with st.container(border=True):
    st.markdown(markdown_text)


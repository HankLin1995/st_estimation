import streamlit as st

col1,col2,col3=st.columns([5,1,5])

with col1:

    with open("./md/SP.md", "r", encoding="utf-8") as file:
        markdown_text = file.read()

    st.markdown(markdown_text)


with col3:

    with open("./md/log.md", "r", encoding="utf-8") as file:
        markdown_text = file.read()

    st.markdown(markdown_text,True) 
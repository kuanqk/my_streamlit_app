import streamlit as st

st.title("Мое Streamlit приложение")
st.write("Привет из AI")

name = st.text_input("Введите ваше имя:")
if name:
    st.success(f"Добро пожаловать, {name}!")
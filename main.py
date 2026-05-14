import os
import streamlit as st
import anthropic

st.title("ChatBot (Claude)")

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Anthropic API Key", type="password")

if not api_key:
    st.info("サイドバーに Anthropic API キーを入力してください。")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("メッセージを入力..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("考え中..."):
            response = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1024,
                messages=st.session_state.messages,
            )
            reply = response.content[0].text
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

import streamlit as st
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from utils import persona, assessment

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=API_KEY)

st.set_page_config(page_title="Auo-Didact", page_icon="🧑‍🏫", layout="wide")
st.title('Auto-Didact')

st.markdown("""Hi there! I'm Auto-Didactabot. I'm here to help accelerate and focus your Ultralearning journey.
        \nfor more information about Ultralearning check out Scott Young's site [here](https://www.scotthyoung.com/blog/ultralearning/)
""")

topic = st.text_input("What do you want to learn?", placeholder="E.g. computer science, playing the piano, riding a bike")
motivation = st.text_input("Why do you want to learn this?", placeholder="E.g. to impress my friends, to advance in my career")
context = st.text_input("How do you intend to apply this skill?", placeholder="E.g. at work, for leisure")
time = st.text_input("How much time do you have to learn this skill?", placeholder="E.g. 3 months, 1 year")

button = st.empty()
response = st.empty()

if button.button("Generate"):

  with client.messages.stream(
    model='claude-3-haiku-20240307',
    temperature=0.5,
    max_tokens=1000,
    system=persona + assessment,
    messages=[
      {
        "role": "user",
        "content" : [
          {
            "type": "text",
            "text": f"TOPIC: {topic}\nMOTIVATION: {motivation}\nCONTEXT: {context}\nTIME: {time}"
          }
        ]
      }
    ]
  ) as stream:
    text = ""
    for chunk in stream.text_stream:
      text += chunk
      response.info(text)

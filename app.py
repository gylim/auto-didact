import streamlit as st
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
llm = ChatAnthropic(model='claude-3-haiku-20240307', anthropic_api_key=API_KEY, temperature=0.5)

st.set_page_config(page_title="Auo-Didact", page_icon="🧑‍🏫", layout="wide")
st.title('Auto-Didact')

system_prompt = st.text_input("System Prompt", "You are a world-class instructor and trainer who has spent many decades helping adults to learn and teach themselves about new topics. Generate a brief syllabus and learning plan for the given topic using not more than 500 words.")
user_prompt = st.text_input("User Prompt", "Machine Learning")

button = st.empty()
response = st.empty()

if button.button("Generate"):
  prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "I'd like to learn more about {topic}")
  ])
  parser = StrOutputParser()
  chain = prompt | llm | parser

  for chunk in chain.stream({"topic": user_prompt}):
    if chunk is not None:
      chunks = chunks + chunk
      response.info(chunks)

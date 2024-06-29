import streamlit as st
import os, requests
from dotenv import load_dotenv
from anthropic import Anthropic
from utils import persona, assessment, research, research2, tools

# Set-up
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_SEARCH = os.getenv("SCRAPING_DOG_KEY")
client = Anthropic(api_key=API_KEY)
def get_search_result(query):
  url = "https://api.scrapingdog.com/google/"
  payload = {
    "api_key": GOOGLE_SEARCH,
    "query": query,
  }
  response = requests.get(url, params=payload)
  if response.status_code == 200:
    data = response.json()
    return data
  else:
    return f"Request failed with status code: {response.status_code}"

def extract_data(result):
  search_result = "\n".join(["Webpage = "+x["title"]+"; Summary = "+x["snippet"] for x in result['organic_data']])
  also_ask = "\n".join(["Question = "+y["question"]+"; Answer = "+y["answers"] for y in result['people_also_ask']])
  return {"search": search_result, "similar_results": also_ask}

# Page metadata
st.set_page_config(page_title="Auo-Didact", page_icon="🧑‍🏫", layout="wide")
st.title('Auto-Didact')

st.markdown("""Hi there! I'm Auto-Didactabot. I'm here to help accelerate and focus your Ultralearning journey.
        \nfor more information about Ultralearning check out Scott Young's site [here](https://www.scotthyoung.com/blog/ultralearning/)
""")

# Initial onboarding
topic = st.text_input("What do you want to learn?", placeholder="E.g. computer science, playing the piano, riding a bike")
motivation = st.text_input("Why do you want to learn this?", placeholder="E.g. to impress my friends, to advance in my career")
context = st.text_input("How do you intend to apply this skill?", placeholder="E.g. at work, for leisure")
time = st.text_input("How much time do you have to learn this skill?", placeholder="E.g. 3 months, 1 year")
onboard = st.empty()
response = st.empty()

# Analyse query
analyse = st.empty()
syllabus = st.empty()

if onboard.button("Generate"):

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

if analyse.button("Analyse"):

  message = client.messages.create(
    model='claude-3-haiku-20240307',
    temperature=0.5,
    max_tokens=1000,
    system=persona + research,
    tools=tools,
    tool_choice= {"type": "auto"},
    messages=[
      {
        "role": "user",
        "content" : [
          {
            "type": "text",
            "text": f"TOPIC: {topic}\nCONTEXT: {context}"
          }
        ]
      }
    ]
  )
  if message.stop_reason != "tool_use":
    syllabus.info(message.content[0].text)
  elif message.stop_reason == "tool_use":
    tool_params = message.content[1].input
    tool_name = message.content[1].name

    if tool_name == "get_search_result":
      result = get_search_result(tool_params["query"])
      if "Request failed" not in result:
        message = client.messages.create(
          model='claude-3-haiku-20240307',
          temperature=0.5,
          max_tokens=1000,
          system=persona + research2,
          messages=[
            {
              "role": "user",
              "content" : [
                {
                  "type": "text",
                  "text": f"## SEARCH RESULT ## \n{extract_data(result)} \n\n ## USER INPUT ##\nTOPIC: {topic}\nCONTEXT: {context}"
                }
              ]
            }
          ]
        )
        syllabus.info(message.content[0].text)

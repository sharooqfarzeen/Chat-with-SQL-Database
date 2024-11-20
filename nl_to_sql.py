import os
from dotenv import load_dotenv

import google.generativeai as genai

# Loading all environment variables
load_dotenv()

# Fetching the API KEY
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

system_instruction = """Return only the SQL Query as a string response and nothing else, without any headings, prefixes or suffixes,
                        even if the query is multi-line.
                        Also replace apostrophes within text elements in the query with 2 single quotes, to avoid Syntax Error when
                        executing SQL Commands.
                        You are a data engineer. Your task is to convert natural language queries into SQL Commands,
                        which can be used to query an SQLite database. You will be given table names and columns names.
                        If table name is not given in the prompt, see if the table name was mentioned earlier in the chat history.
                        """
# Setting model to be used
model = genai.GenerativeModel("gemini-1.5-flash",
                             system_instruction=system_instruction)

# starting chat_session
chat_session = model.start_chat()

# Function to convert natural language to SQL
def nl_to_sql(prompt: str, chat=chat_session) -> str:
    sql = chat.send_message(prompt).text
    return sql   
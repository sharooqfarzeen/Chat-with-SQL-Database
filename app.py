import streamlit as st
import pandas as pd
import sqlite3
import os 
from dotenv import load_dotenv

from nl_to_sql import nl_to_sql, start_chat_session
from retrieve_data import retrieve_data


# Streamlit app

# Title
st.set_page_config(page_title="Chat with DB - CRUD")

# Function to get api key from user if not already set
@st.dialog("Enter Your API Key")
def get_api():
    api_key = st.text_input("Google Gemini API Key", type="password", help="Your API key remains secure and is not saved.")
    if st.button("Submit"):
        if api_key:
            st.session_state["GOOGLE_API_KEY"] = api_key
            st.success("API key set successfully!")
            st.session_state["chat_session"] = start_chat_session()
            st.rerun()
        else:
            st.error("API key cannot be empty.")
    st.markdown("[Create your Gemini API Key](https://aistudio.google.com/apikey)", unsafe_allow_html=True)

# Loading API Keys
load_dotenv(override=True)

# Check if the API key is set
if "GOOGLE_API_KEY" not in st.session_state:
    if "GOOGLE_API_KEY" not in os.environ:
        get_api()
    else:
        st.session_state["GOOGLE_API_KEY"] = os.environ["GOOGLE_API_KEY"]
        st.session_state["chat_session"] = start_chat_session()


if "GOOGLE_API_KEY" in st.session_state:
    # Header
    st.title("Chat with SQL DB")

    # Initializing chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Initializing db_name to None
    if "db_name" not in st.session_state:
        st.session_state["db_name"] = None

    # Display chat history on re-run
    for message in st.session_state.chat_history:
        st.chat_message(message["role"]).write(message["content"])

    # Sidebar - for user input
    with st.sidebar:
        with st.container():
            #Sidebar Header
            st.header("Create, Retrieve, Update, Delete Tables")

        # Container for Table Operations
        with st.container():
            with st.form(key="chat_form", clear_on_submit=True):
                # Choosing the DB to connect to
                db = st.file_uploader(label="Connect to a database", help="Select the SQLite Database you want to connect to.", type="db")
                # Submit Button
                submit = st.form_submit_button(label="Connect", help="Click or press Enter to submit")

        # Container to create new database
        with st.container():
            st.header("Create new database")
            with st.form(key="database_form", clear_on_submit=True):
                # Fetching name from user
                name = st.text_input(label="Database Name", placeholder="Enter name for new DB")
                submit_db = st.form_submit_button(label="Create", help="Click or press Enter to submit")


    # User query in natural language
    user_query = st.chat_input(placeholder="Eg. Show all tables")

    # User wants to create a new database
    if submit_db:
        if name:
            name += ".db"
            # Creating the new database
            connection = sqlite3.connect(name)
            # Closing the connection
            connection.close()
            # Show assistant response in app
            st.chat_message("assistant").markdown(f"Database {name} created.")
            # Adding to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": f"Database {name} created."})

    # On submit
    if submit or user_query:
        # If a new db has been uploaded
        if submit and db:
            with st.spinner("Storing database..."):
                # Store DB name in session_state
                st.session_state.db_name = db.name
                st.chat_message("assistant").markdown(f"Connected to {st.session_state.db_name[:-3]} database.")
                # Adding to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": f"Connected to {st.session_state.db_name[:-3]} database."})
        
        # If user enters a new query
        if user_query:
            # Show user query in app
            st.chat_message("user").markdown(user_query)
            # Adding to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            
            # Retrieve data only if a db has been connected
            if st.session_state.db_name:
                # Convert Natural Language to SQL Query
                query = nl_to_sql(prompt=user_query, chat=st.session_state["chat_session"])
                # Retrieve data as a pandas dataframe from the DB
                table, success = retrieve_data(db_name=st.session_state.db_name, query=query)
                # If Operation was unsuccessful
                if not success:
                    # Show message in app
                    st.chat_message("assistant").markdown("Operation is not supported")
                    # Adding to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": "Operation is not supported"})
                # If Query was for retrieval and a dataframe was returned
                elif table is not None:
                    # Show dataframe in app
                    st.chat_message("assistant").table(data=table)
                    # Adding to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": table})
                # If query was a create/update operation
                else :
                    # Show assistant response in app
                    st.chat_message("assistant").markdown("Operation Success.")
                    # Adding to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": "Operation Success."})

                
            # If db was not connected
            else:
                st.chat_message("assistant").markdown("Please connect to a Database first.")
                # Adding to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": "Please connect to a Database first."})
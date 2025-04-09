# import streamlit as st
# from pathlib import Path
# from langchain_community.agent_toolkits.sql.base import create_sql_agent
# from langchain_community.utilities import SQLDatabase
# from langchain.agents.agent_types import AgentType
# from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# from sqlalchemy import create_engine
# import sqlite3
# from langchain_groq import ChatGroq

# st.set_page_config(page_title="Chat with SQL DB", page_icon="🦜")
# st.title("🦜 Chat with SQL DB")

# LOCALDB = "USE_LOCALDB"
# MYSQL = "USE_MYSQL"
# radio_opt = ["Use SQLLite 3 Database- Student.db", "Connect to you MySQL Database"]
# selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)

# if radio_opt.index(selected_opt) == 1:
#     db_uri = MYSQL
#     mysql_host = st.sidebar.text_input("Provide MySQL Host")
#     mysql_user = st.sidebar.text_input("MYSQL User")
#     mysql_password = st.sidebar.text_input("MYSQL password", type="password")
#     mysql_db = st.sidebar.text_input("MySQL database")
# else:
#     db_uri = LOCALDB

# api_key = st.sidebar.text_input(label="Groq API Key", type="password")

# if not api_key:
#     st.info("Please add the Groq API key")

# # LLM model
# llm = ChatGroq(groq_api_key=api_key, model_name="Llama3-8b-8192", streaming=True)

# @st.cache_resource(ttl="2h")
# def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
#     try:
#         if db_uri == LOCALDB:
#             dbfilepath = (Path(__file__).parent / "student.db").absolute()
#             creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
#             return SQLDatabase(create_engine("sqlite:///", creator=creator)), create_engine("sqlite:///", creator=creator)
#         elif db_uri == MYSQL:
#             if not (mysql_host and mysql_user and mysql_password and mysql_db):
#                 return None, None
#             engine = create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}")
#             return SQLDatabase(engine), engine
#     except Exception as e:
#         st.error(f"Database connection error: {str(e)}")
#         return None, None

# if db_uri == MYSQL and (not mysql_host or not mysql_user or not mysql_password or not mysql_db):
#     st.error("Please provide all MySQL connection details.")
#     db = None
#     engine = None
# else:
#     db, engine = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)

# # Function to get table info
# def get_db_info(db):
#     if not db:
#         return "Database not connected"
    
#     return db.get_table_info()

# # Function to generate SQL query from natural language
# def generate_sql_query(user_query, db_info):
#     prompt = f"""
# You are an expert SQL query generator. Generate a single SQL query that answers the user's question.
# Do not explain your reasoning, just provide the SQL query itself.

# Database information:
# {db_info}

# User question: {user_query}

# SQL query:
# """
#     try:
#         response = llm.invoke(prompt)
#         # Extract SQL from response
#         sql_query = response.content.strip()
#         if sql_query.lower().startswith("```sql"):
#             sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
#         elif "```" in sql_query:
#             sql_query = sql_query.split("```")[1].strip()
#         return sql_query
#     except Exception as e:
#         return f"Error generating SQL query: {str(e)}"

# # Function to execute SQL query
# def execute_query(query, engine):
#     try:
#         with engine.connect() as conn:
#             result = conn.execute(text(query))
#             columns = result.keys()
#             data = result.fetchall()
#             return pd.DataFrame(data, columns=columns)
#     except Exception as e:
#         error_msg = str(e)
#         tb = traceback.format_exc()
#         if "no such table" in error_msg.lower():
#             return f"Error: The requested table does not exist in the database."
#         elif "no such column" in error_msg.lower():
#             return f"Error: One of the requested columns does not exist in the database."
#         elif "syntax error" in error_msg.lower():
#             return f"Error: There was a syntax error in the SQL query."
#         else:
#             return f"Error executing query: {error_msg}"

# # Function to generate natural language response from SQL results
# def generate_response(user_query, sql_query, results, db_info):
#     if isinstance(results, str) and results.startswith("Error"):
#         prompt = f"""
# User question: {user_query}

# I tried to execute the following SQL query:
# {sql_query}

# But I got this error:
# {results}

# Based on the database schema:
# {db_info}

# Please explain the error in simple terms and suggest what the user might be looking for instead.
# """
#     else:
#         result_str = results.to_markdown() if isinstance(results, pd.DataFrame) else str(results)
#         prompt = f"""
# User question: {user_query}

# I executed the following SQL query:
# {sql_query}

# Here are the results:
# {result_str}

# Based on these results, provide a clear and concise answer to the user's question. If the results are empty,
# explain that the data they're looking for doesn't exist in the database. Include relevant numbers from the results.
# """
    
#     try:
#         response = llm.invoke(prompt)
#         return response.content
#     except Exception as e:
#         return f"Error generating response: {str(e)}"

# # Initialize or clear chat history
# if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
#     st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you with the database today?"}]

# # Summarize database button
# if st.sidebar.button("Summarize Database"):
#     if db:
#         with st.spinner("Loading database schema..."):
#             db_info = get_db_info(db)
            
#         prompt = f"""
# Based on this database schema information, provide a concise summary of:
# 1. Tables in the database and their purpose
# 2. Key columns in each table
# 3. Important relationships between tables

# Database schema:
# {db_info}
# """
        
#         with st.spinner("Analyzing database structure..."):
#             try:
#                 response = llm.invoke(prompt)
#                 summary = response.content
#                 st.session_state.messages.append({"role": "assistant", "content": f"**Database Summary:**\n\n{summary}"})
#             except Exception as e:
#                 st.error(f"Error generating summary: {str(e)}")
#     else:
#         st.error("Please connect to a database first.")

# # Display chat messages
# for msg in st.session_state.messages:
#     st.chat_message(msg["role"]).write(msg["content"])

# # Handle user input
# user_query = st.chat_input(placeholder="Ask anything from the database")
# if user_query and db and engine:
#     st.session_state.messages.append({"role": "user", "content": user_query})
#     st.chat_message("user").write(user_query)
    
#     with st.chat_message("assistant"):
#         with st.spinner("Analyzing your question..."):
#             db_info = get_db_info(db)
            
#         with st.spinner("Generating SQL query..."):
#             sql_query = generate_sql_query(user_query, db_info)
#             st.code(sql_query, language="sql")
            
#         with st.spinner("Executing query..."):
#             results = execute_query(sql_query, engine)
            
#             if isinstance(results, pd.DataFrame):
#                 st.dataframe(results)
#             else:
#                 st.error(results)
                
#         with st.spinner("Interpreting results..."):
#             response = generate_response(user_query, sql_query, results, db_info)
#             st.write(response)
            
#         st.session_state.messages.append({"role": "assistant", "content": f"{response}\n\n```sql\n{sql_query}\n```"})
# elif user_query:
#     st.session_state.messages.append({"role": "user", "content": user_query})
#     st.chat_message("user").write(user_query)
    
#     with st.chat_message("assistant"):
#         st.error("Please ensure the database is properly connected and your API key is entered.")
#         st.session_state.messages.append({"role": "assistant", "content": "Please ensure the database is properly connected and your API key is entered."})


import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine , text
import sqlite3
from langchain_groq import ChatGroq
import traceback
import pandas as pd


st.set_page_config(page_title="Chat with SQL DB", page_icon="🦜")
st.title("🦜 Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"
radio_opt = ["Use SQLLite 3 Database- Student.db", "Connect to you MySQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)

# Initialize variables
mysql_host = None
mysql_user = None
mysql_password = None
mysql_db = None

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MYSQL User")
    mysql_password = st.sidebar.text_input("MYSQL password", type="password")
    mysql_db = st.sidebar.text_input("MySQL database")
else:
    db_uri = LOCALDB

api_key = st.sidebar.text_input(label="Groq API Key", type="password")

if not api_key:
    st.info("Please add the Groq API key")

# LLM model
@st.cache_resource(ttl="2h")
def get_llm(api_key):
    if not api_key:
        return None
    try:
        return ChatGroq(groq_api_key=api_key, model_name="Llama3-8b-8192", streaming=True)
    except Exception as e:
        st.error(f"Error initializing LLM: {str(e)}")
        return None

llm = get_llm(api_key)

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    try:
        if db_uri == LOCALDB:
            dbfilepath = (Path(__file__).parent / "student.db").absolute()
            creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
            return SQLDatabase(create_engine("sqlite:///", creator=creator)), create_engine("sqlite:///", creator=creator)
        elif db_uri == MYSQL:
            if not (mysql_host and mysql_user and mysql_password and mysql_db):
                return None, None
            engine = create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}")
            return SQLDatabase(engine), engine
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None, None

# Check database connection parameters
if db_uri == MYSQL and (not mysql_host or not mysql_user or not mysql_password or not mysql_db):
    st.error("Please provide all MySQL connection details.")
    db = None
    engine = None
else:
    db, engine = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)

# Function to get table info
def get_db_info(db):
    if not db:
        return "Database not connected"
    
    return db.get_table_info()

# Function to generate SQL query from natural language
def generate_sql_query(user_query, db_info):
    if not llm:
        return "LLM not initialized. Please check your API key."
        
    prompt = f"""
You are an expert SQL query generator. Generate a single SQL query that answers the user's question.
Do not explain your reasoning, just provide the SQL query itself.

Database information:
{db_info}

User question: {user_query}

SQL query:
"""
    try:
        response = llm.invoke(prompt)
        # Extract SQL from response
        sql_query = response.content.strip()
        if sql_query.lower().startswith("```sql"):
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql_query:
            sql_query = sql_query.split("```")[1].strip()
        return sql_query
    except Exception as e:
        return f"Error generating SQL query: {str(e)}"

# Function to execute SQL query
def execute_query(query, engine):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            columns = result.keys()
            data = result.fetchall()
            return pd.DataFrame(data, columns=columns)
    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        if "no such table" in error_msg.lower():
            return f"Error: The requested table does not exist in the database."
        elif "no such column" in error_msg.lower():
            return f"Error: One of the requested columns does not exist in the database."
        elif "syntax error" in error_msg.lower():
            return f"Error: There was a syntax error in the SQL query."
        else:
            return f"Error executing query: {error_msg}"

# Function to generate natural language response from SQL results
def generate_response(user_query, sql_query, results, db_info):
    if not llm:
        return "LLM not initialized. Please check your API key."
        
    if isinstance(results, str) and results.startswith("Error"):
        prompt = f"""
User question: {user_query}

I tried to execute the following SQL query:
{sql_query}

But I got this error:
{results}

Based on the database schema:
{db_info}

Please explain the error in simple terms and suggest what the user might be looking for instead.
"""
    else:
        result_str = results.to_markdown() if isinstance(results, pd.DataFrame) else str(results)
        prompt = f"""
User question: {user_query}

I executed the following SQL query:
{sql_query}

Here are the results:
{result_str}

Based on these results, provide a clear and concise answer to the user's question. If the results are empty,
explain that the data they're looking for doesn't exist in the database. Include relevant numbers from the results.
"""
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Initialize or clear chat history
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you with the database today?"}]

# Summarize database button
if st.sidebar.button("Summarize Database"):
    if db and llm:
        with st.spinner("Loading database schema..."):
            db_info = get_db_info(db)
            
        prompt = f"""
Based on this database schema information, provide a concise summary of:
1. Tables in the database and their purpose
2. Key columns in each table
3. Important relationships between tables

Database schema:
{db_info}
"""
        
        with st.spinner("Analyzing database structure..."):
            try:
                response = llm.invoke(prompt)
                summary = response.content
                st.session_state.messages.append({"role": "assistant", "content": f"**Database Summary:**\n\n{summary}"})
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")
    else:
        if not db:
            st.error("Please connect to a database first.")
        if not llm:
            st.error("Please check your API key.")

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
user_query = st.chat_input(placeholder="Ask anything from the database")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)
    
    with st.chat_message("assistant"):
        if not db or not engine:
            st.error("Please ensure the database is properly connected.")
            st.session_state.messages.append({"role": "assistant", "content": "Please ensure the database is properly connected."})
        elif not llm:
            st.error("Please check your API key.")
            st.session_state.messages.append({"role": "assistant", "content": "Please check your API key."})
        else:
            with st.spinner("Analyzing your question..."):
                db_info = get_db_info(db)
                
            with st.spinner("Generating SQL query..."):
                sql_query = generate_sql_query(user_query, db_info)
                st.code(sql_query, language="sql")
                
            with st.spinner("Executing query..."):
                results = execute_query(sql_query, engine)
                
                if isinstance(results, pd.DataFrame):
                    st.dataframe(results)
                else:
                    st.error(results)
                    
            with st.spinner("Interpreting results..."):
                response = generate_response(user_query, sql_query, results, db_info)
                st.write(response)
                
            st.session_state.messages.append({"role": "assistant", "content": f"{response}\n\n```sql\n{sql_query}\n```"})
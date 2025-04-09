# Chat with SQL Database

This project is a Streamlit-based interactive application that allows users to communicate with their relational databases (SQLite or MySQL) using natural language. By leveraging Groq's LLaMA 3 language model, the application converts user questions into SQL queries, executes them on the selected database, and returns both the raw data and a human-readable explanation.

---

## Overview

The goal of this project is to simplify data exploration and querying for users who may not be familiar with SQL. By asking questions in natural language, users can:

- Automatically generate relevant SQL queries.
- Retrieve data from their database without writing SQL manually.
- View results in a structured format.
- Get concise interpretations of the results.
- Understand the structure and relationships in their database through summaries.

This makes it a useful tool for analysts, developers, educators, and business users who work with databases but prefer natural language interfaces.

---

## Features

- Supports both SQLite (`student.db`) and external MySQL databases.
- Uses Groq's LLaMA 3 (8B) model for generating SQL queries and summarizing results.
- Interactive Streamlit interface for chatting with your database.
- Secure input of sensitive credentials (API keys, database passwords).
- Ability to summarize the database schema and relationships between tables.
- Maintains chat history within the session for a conversational experience.

---

## Requirements

- Python 3.8 or later
- A valid Groq API key
- SQLite or MySQL database with accessible schema

### Installation Dependencies

Install required Python packages using:

```bash
pip install -r requirements.txt

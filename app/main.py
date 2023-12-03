import os
import openai
import streamlit as st
from streamlit_chat import message

from neo4j_driver import run_query
from english2cypher import generate_cypher
from graph2text import generate_response

import os
from neo4j import GraphDatabase

def initialize_session_state():
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None

initialize_session_state()

# if 'generated' not in st.session_state:
#     st.session_state['generated'] = None

# Hardcoded UserID
USER_ID = "neo4j"

# On the first execution, we have to create a user node in the database.
run_query("""
MERGE (u:User {id: $userId})
""", {'userId': USER_ID})

st.set_page_config(layout="wide")
st.title("DM Thesis with context : DM + Neo4j")


cypher_test = """MATCH path = (a:Property {value: 'promotion_711'})-[:INIT]->(b:Promotion)
RETURN path"""

def generate_context(prompt, context_data='generated'):
    context = []
    # If any history exists
    if st.session_state['generated']:
        # Add the last three exchanges
        size = len(st.session_state['generated'])
        for i in range(max(size-3, 0), size):
            context.append(
                {'role': 'user', 'content': st.session_state['user_input'][i]})
            context.append(
                {'role': 'assistant', 'content': st.session_state[context_data][i]})
    # Add the latest user prompt
    context.append({'role': 'user', 'content': str(prompt)})
    return context


# Generated natural language
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
# Neo4j database results
if 'database_results' not in st.session_state:
    st.session_state['database_results'] = []
# User input
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []
# Generated Cypher statements
if 'cypher' not in st.session_state:
    st.session_state['cypher'] = []


def get_text():
    input_text = st.text_input(
        "Ask away", "", key="input")
    return input_text


# Define columns
col1, col2 = st.columns([2, 1])

with col2:
    another_placeholder = st.empty()
with col1:
    placeholder = st.empty()
user_input = get_text()


if user_input:
    # cypher = generate_cypher(generate_context(user_input, 'database_results'))
    # If not a valid Cypher statement
    # if not "MATCH" in cypher:
    #     print('No Cypher was returned')
    #     st.session_state.user_input.append(user_input)
    #     st.session_state.generated.append(
    #         cypher)
    #     st.session_state.cypher.append(
    #         "No Cypher statement was generated")
    #     st.session_state.database_results.append("")
    # else:
        # Query the database, user ID is hardcoded
    results = run_query(cypher_test, {'userId': USER_ID})
    # Harcode result limit to 10
    results = results[:10]
    # Graph2text
    answer = generate_response(generate_context(
            f"Question was {user_input} and the response should include only information that is given here: {str(results)}"))
    st.session_state.database_results.append(str(results))
    st.session_state.user_input.append(user_input)
    st.session_state.generated.append(answer),
    st.session_state.cypher.append(cypher_test)


# Message placeholder
with placeholder.container():
    if st.session_state['generated']:
        size = len(st.session_state['generated'])
        # Display only the last three exchanges
        for i in range(max(size-3, 0), size):
            message(st.session_state['user_input'][i],
                    is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))


# Generated Cypher statements
with another_placeholder.container():
    if st.session_state['cypher']:
        st.text_area("Latest generated Cypher statement",
                     st.session_state['cypher'][-1], height=240)
        



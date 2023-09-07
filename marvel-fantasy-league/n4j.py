from neo4j import GraphDatabase
import streamlit as st

host = st.secrets['NEO4J_HOST']
user = st.secrets['NEO4J_USER']
password = st.secrets['NEO4J_PASSWORD']

# driver = GraphDatabase.driver(host, auth=(user, password))

# Experimental query
def execute_query(query, params={}):
    # Returns a tuple of records, summary, keys
    with GraphDatabase.driver(host, auth=(user, password)) as driver:
        records, summary, keys =  driver.execute_query(query, params)
        # Only interested in list of result records
        return records
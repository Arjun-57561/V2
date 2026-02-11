import pytest
from agents.query_processor import QueryProcessor

def test_query_processor():
    agent = QueryProcessor()
    assert agent.name == "QueryProcessor"

# Add more tests

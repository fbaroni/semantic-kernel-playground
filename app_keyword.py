from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt  
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.models import Vector  
from azure.search.documents.indexes.models import (  
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    PrioritizedFields,  
    SemanticField,  
    SearchField,  
    SemanticSettings,  
    VectorSearch,  
    VectorSearchAlgorithmConfiguration,  
)  


# logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
# Set up the search client
search_url = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
admin_key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
credential = AzureKeyCredential(admin_key)
client = SearchClient(endpoint=search_url, index_name=index_name, credential=credential)
openai.api_key = os.environ["AZURE_OPENAI_API_KEY"]
openai.api_type = "azure"
openai.api_version = "2023-05-15" 
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 

def run_query(query):
    
    return client.search(  
        search_text=query,  
        select=["title", "content"] 
    )  

# Define the Streamlit app
def app():
    st.title("Search query - Keyword")
    query = st.text_input("Enter your query here: ")
    if st.button("Search"):
        results = client.search(search_text=query, top=5)
        if results:  # Check if results is not empty
            for result in results:
                st.write(f"<h4>{result['title']}</h4>", unsafe_allow_html=True)
                st.write(f"<p>{result['content'][:2000]}</p>", unsafe_allow_html=True)
                st.write('------------------------')
        else:  # This block will execute if results is empty
            st.write("No results found.")

if __name__ == "__main__":
    app()
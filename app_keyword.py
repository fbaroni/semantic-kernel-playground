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
openai.api_key = os.environ["AZURE_OPENAI_KEY"]
openai.api_type = "azure"
openai.api_version = "2023-05-15" 
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 

def run_query(query):
    
    return client.search(  
        search_text=query,  
        select=["title", "content"] 
    )  
def get_highlighted_text(query, content):

    messages = [
        {
            "role": "system",
            "content": os.environ["AZURE_OPENAI_SYSTEM_MESSAGE"]
        }
    ]
    prompt = """
        Can you highlight the part that is relevant to my query?
        Dont return me an answer. I just need the paragraph with the highlighted text. I will print it as a search result.
        If nothing is relevant, please return the first paragraph.
        Please return the "highlighted text" in the paragraph between <b> and </b>.
        The result should be html
    """

    messages.append({
        "role": "user" ,
        "content": prompt
    })

    messages.append({
        "role": "user" ,
        "content": "The query is " + query
    })

    messages.append({
        "role": "user" ,
        "content": "The content is " + content
    })

    response = openai.ChatCompletion.create(
        engine=os.environ["AZURE_OPENAI_MODEL_NAME"],
        messages = messages,
        temperature=float(os.environ["AZURE_OPENAI_TEMPERATURE"]),
        max_tokens=int(os.environ["AZURE_OPENAI_MAX_TOKENS"]),
        top_p=float(os.environ["AZURE_OPENAI_TOP_P"]),
        stop=None
    )

    return response.choices[0].message['content']

# Define the Streamlit app
def app():
    st.title("Search query")
    query = st.text_input("Enter your query here: ")
    if st.button("Search"):
        results = client.search(search_text=query, top=3)
        for result in results:
            text = get_highlighted_text(query, result['content'])
            st.write("<a href='#'>Go to the document</a>", unsafe_allow_html=True)
            st.write(text, unsafe_allow_html=True)
            st.write('------------------------')

if __name__ == "__main__":
    app()
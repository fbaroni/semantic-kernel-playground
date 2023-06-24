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

def generate_embeddings(text):
    response = openai.Embedding.create(
        input=text, engine="text-embedding-ada-002")
    embeddings = response['data'][0]['embedding']
    return embeddings

def run_query(query):
    
    return client.search(  
        search_text="",  
        vector=Vector(value=generate_embeddings(query), k=3, fields="contentVector"),  
        select=["title", "content"] 
    )

def get_highlighted_text(query, content):

    prompt = """
        Can you highlight the sentence that is most relevant to my search term? 
        Please return the "highlighted text" in the paragraph between <p style="color:blue;"> and </p> and translated to the language in which the search term was written. 
        The result must be html
    """

    messages = [
        {
            "role": "system",
            "content": "You are an assitant for a lawyer. You are given contracts and you need to try to response based on the provided data." # prompt #os.environ["AZURE_OPENAI_SYSTEM_MESSAGE"]
        }
    ]

    messages.append({
        "role": "user" ,
        "content": prompt
    })

    messages.append({
        "role": "user" ,
        "content": "The search term is '" + query + "'"
    })

    messages.append({
        "role": "user" ,
        "content": "The content is '" + content + "'"
    })
    print("---------PROMPT---------")
    print(messages)
    print("---------PROMPT---------")
    response = openai.ChatCompletion.create(
        engine=os.environ["AZURE_OPENAI_MODEL_NAME"],
        messages = messages,
        temperature=float(os.environ["AZURE_OPENAI_TEMPERATURE"]),
        max_tokens=int(os.environ["AZURE_OPENAI_MAX_TOKENS"]),
        top_p=float(os.environ["AZURE_OPENAI_TOP_P"]),
        stop=None
    )
    print("---------RESPONSE---------")
    print(response)
    print("---------RESPONSE---------")
    return response.choices[0].message['content']

# Define the Streamlit app
def app():
    st.title("Search query")
    query = st.text_input("Enter your query here: ")
    if st.button("Search"):
        results = run_query(query)
    
        for result in results:
            text = get_highlighted_text(query, result['content'])  
            st.write(f"<h4>Title: {result['title']}</h4>", unsafe_allow_html=True)  
            st.write(f"Score: {result['@search.score']}")  
            st.write(f"Highlight: {text}", unsafe_allow_html=True)
            st.write(f"Content: <p>{result['content'][:1000]}</p>", unsafe_allow_html=True)
                
        # st.write('------------------------')

if __name__ == "__main__":
    app()
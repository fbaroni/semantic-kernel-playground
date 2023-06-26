from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import semantic_kernel as sk
import asyncio
from concurrent.futures import ThreadPoolExecutor
import semantic_kernel.connectors.ai.open_ai as sk_oai
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.models import Vector  
import openai

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
_executor = ThreadPoolExecutor(1)

def generate_embeddings(text):
    response = openai.Embedding.create(
        input=text, engine="text-embedding-ada-002")
    embeddings = response['data'][0]['embedding']
    return embeddings

# Define the query function
async def run_query(query):
    return client.search(  
        search_text=query,  
        vector=Vector(value=generate_embeddings(query), k=3, fields="contentVector"),  
        select=["title", "content"] 
    )  

async def get_highlighted_text(query, content):

    system_message = """
    You are an assitant for a lawyer. You are given contracts and you need to try to response based on the provided data.
    """
    kernel = sk.Kernel()
    deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
    kernel.add_chat_service(
        "gpt-35-turbo", sk_oai.AzureChatCompletion(deployment, endpoint, api_key)
    )

    prompt_config = sk.PromptTemplateConfig.from_completion_parameters(
        max_tokens=3000, temperature=0.9, top_p=0.8
    )

    prompt_template = sk.ChatPromptTemplate(
        "{{$user_input}}", kernel.prompt_template_engine, prompt_config
    )

    prompt_template.add_system_message(system_message)
    prompt = """
        Can you highlight the sentence that is most relevant to my search term? 
        Please return the "highlighted text" in the paragraph between <p style="color:blue;"> and </p>. 
        The result must be html
    """
    prompt_template.add_user_message(prompt) 

    prompt_template.add_user_message("The query is \"{}\"".format(query) + " and the content is: " + content) 

    function_config = sk.SemanticFunctionConfig(prompt_config, prompt_template)
    chat_function = kernel.register_semantic_function("ChatBot", "Chat", function_config)
    context_vars = sk.ContextVariables()
    bot_answer = await kernel.run_async(chat_function, input_vars=context_vars)
    return str(bot_an
               swer)
# Define the Streamlit app
async def app():
    st.title("Search query")
    query = st.text_input("Enter your query here: ")
    if st.button("Search"):
        results = await run_query(query)
        for result in results:
            text = await get_highlighted_text(query, result['content'])  
            st.write(f"<h4>{result['title']}</h4>", unsafe_allow_html=True)  
            st.write(f"{text}", unsafe_allow_html=True)
            st.write(f"Content: <p>{result['content'][:1000]}</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    asyncio.run(app())
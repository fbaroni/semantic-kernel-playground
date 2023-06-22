from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
# Set up the search client
search_url = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
admin_key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
credential = AzureKeyCredential(admin_key)
client = SearchClient(endpoint=search_url, index_name=index_name, credential=credential)

# Define the query function
def run_query(query):
    # TODO vector search
    results = client.search(search_text=query, top=3)
    return results.get_results()

# Define the Streamlit app
def app():
    st.title("Search query")
    query = st.text_input("Enter your query here: ")
    if st.button("Search"):
        results = client.search(search_text=query)
        for result in results:
            # TODO highlight with chatgpt
            st.write(result['content'][:500])
            st.write('------------------------')

        st.write("Total number of documents found: {}\n".format(results.get_count()))
if __name__ == "__main__":
    app()
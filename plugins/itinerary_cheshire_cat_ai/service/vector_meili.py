from .BaseService import BaseService
from dotenv import load_dotenv, find_dotenv
import os 
import meilisearch
from langchain_community.vectorstores import Meilisearch
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader


path = find_dotenv(filename=".env")
print(load_dotenv(path))

class VectorMeiliService(BaseService):

    def __init__(self,index):
        self.MEILISEARCH_URL = os.environ.get("MEILISEARCH_URL")
        self.MEILISEARCH_MASTER_KEY = os.environ.get("MEILISEARCH_MASTER_KEY")
        self.OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY")
        self.client = meilisearch.Client(self.MEILISEARCH_URL, self.MEILISEARCH_MASTER_KEY)
        self.index = index

        self.embeddings = OpenAIEmbeddings(openai_api_key=self.OPEN_AI_KEY)
        self.embedders = {
            "default": {
                "source": "userProvided",
                "dimensions": 1536,
                }
        }      
        self.embedder_name = "default"
        self.vector_store = Meilisearch(
            embedding=self.embeddings,
            embedders=self.embedders,
            client=self.client,
            index_name=index,
            text_key="text",
        )

    def search(self, query, limit):
        embedding_vector = self.embeddings.embed_query(query)
        docs_and_scores = self.vector_store.similarity_search_by_vector_with_scores(
            embedding_vector, embedder_name=self.embedder_name
        )
        return docs_and_scores[:limit]
    
    def save(self, form_model):
        raise Exception("Funzione non implementa")
    
    def get_filter_by_dict(self, model):
        raise Exception("Funzione non implementata")
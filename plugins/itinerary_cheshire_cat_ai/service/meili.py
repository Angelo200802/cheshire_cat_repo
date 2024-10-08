import meilisearch
from .BaseService import BaseService
from ..model.itinerarymodel import Itinerary
import os 
from cat.log import log

class MeiliService(BaseService):
    
    def __init__(self):
        self.MEILISEARCH_URL = "http://meilisearch:7700"
        self.MEILISEARCH_MASTER_KEY = 'A6Tw7yTI37T4Rx5NINnoG2ScZssgy911qaDvSbx7oyY'
        self.client = meilisearch.Client(self.MEILISEARCH_URL, self.MEILISEARCH_MASTER_KEY)
        if 'itinerary' not in self.client.get_indexes()['results']:
            self.client.create_index('itinerary')
            self.client.index('itinerary').update_filterable_attributes([field_name for field_name, field in Itinerary.__fields__.items()])
    
    def save(self,form_model) -> bool:
        try:
            if not 'id' in form_model:
                form_model['id'] = hash(form_model[x] for x in form_model)
            self.client.index('itinerary').add_documents([form_model])
            return True
        except Exception as e:
            return False

    def search(self,query:any,limit:int) -> any:
        results = self.client.get_index('itinerary').search('',{'filter':query, 'limit':limit})
        return results
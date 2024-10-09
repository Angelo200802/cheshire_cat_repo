import meilisearch
from pydantic import BaseModel
from .BaseService import BaseService
import os 
from cat.log import log
class MeiliService(BaseService):
    
    def __init__(self,index:str=None,model_class:BaseModel=None):
        self.MEILISEARCH_URL = "http://meilisearch:7700"
        self.MEILISEARCH_MASTER_KEY = 'A6Tw7yTI37T4Rx5NINnoG2ScZssgy911qaDvSbx7oyY'
        self.client = meilisearch.Client(self.MEILISEARCH_URL, self.MEILISEARCH_MASTER_KEY)
        if index is None or model_class is None:
            return
        self.index = index
        if index not in self.client.get_indexes()['results']:
            self.client.create_index(index)
        self.client.index(index).update_filterable_attributes([field_name for field_name, field in model_class.__fields__.items()])
    
    def save(self,form_model) -> bool:
        try:
            if not 'id' in form_model:
                form_model['id'] = hash(form_model[x] for x in form_model)
            self.client.index(self.index).add_documents([form_model])
            return True
        except Exception as e:
            return False

    def search(self,query:any,limit:int) -> any:
        results = self.client.get_index(self.index).search('',{'filter':query, 'limit':limit})
        return results
    
    def get_filter_by_dict(self, model:dict) -> list:
        query_filter = []
        for field in model:
            if isinstance(model[field],list):
                query_string = ""
                for i,step in enumerate(self._model[field]):
                    query_string += f"{field} = {step}"
                    if i < len(model[field])-1:
                        query_string+=" OR "
                query_filter.append(query_string)
            else:
                value = model[field]
                query_filter.append(f'{field} = "{value}"')
        return query_filter
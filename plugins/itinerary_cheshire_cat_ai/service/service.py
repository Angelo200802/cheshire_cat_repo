from .BaseService import BaseService
#from ..utility import load_service
from .meili import MeiliService
class Service:

    service : BaseService 

    def __init__(self):
        #self.service = load_service()
        from ..model.itinerarymodel import Itinerary
        self.service = MeiliService('itinerary',Itinerary)

    def save(self,form_model):
        return self.service.save(form_model)
    
    def search(self,query,limit):
        return self.service.search(query,limit)
    
    def get_filter_by_dict(self,model):
        return self.service.get_filter_by_dict(model)
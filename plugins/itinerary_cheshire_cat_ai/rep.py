import meilisearch
MEILISEARCH_URL = "http://meilisearch:7700"
MEILISEARCH_MASTER_KEY = "A6Tw7yTI37T4Rx5NINnoG2ScZssgy911qaDvSbx7oyY"
client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_MASTER_KEY)
#x
if len(client.get_indexes()['results']) == 0:
    client.create_index('itinerary')
    client.index('itinerary').update_filterable_attributes(['country','start_date','finish_date', 'description', 'budget'])

def save(form_model) -> bool:
    try:
        res = client.index('itinerary').add_documents([{
            'id' : hash(form_model[x] for x in form_model),
            'country' : form_model['country'],
            'start_date' : form_model['start_date'],
            'finish_date' : form_model['finish_date'],
            'budget' : form_model['budget'],
            'description' : form_model['description']
        }])
        return True
    except Exception as e:
        return False

def search(query:[]) -> any:
    try:
        results = client.get_index('itinerary').search('',{'filter':query, 'limit':2})
    except Exception as e:
        print(e)
    return results
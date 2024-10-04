import meilisearch
from cat.mad_hatter.decorators import tool,hook
from cat.log import log
import random

MEILISEARCH_URL = "http://calabriastraordinaria.it:7700/"
MEILISEARCH_API_KEY = "v8DtMZ_plHqY2S52rCfYGClUtjp--6fcb6l7KzldD_M"
param = "Cosenza"

@tool(examples = ['Cerca su meilisearch'], return_direct = True)
def do_search(param,cat):
    """
        Restituisce i risultati della ricerca di param su meilisearch. Param è l'input.
    """
    client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_API_KEY)
    results = client.index("mp_it").search(param)
    return str(results)

@tool(examples = ['Cerca il documento con id: '], return_direct = True)
def search_document_by_id(document_id, cat):
    """ 
        Cerca su meilisearch un documento dal titolo. Il document_title è l'input
    """
    client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_API_KEY)
    query = f'id = {document_id}'
    results = client.index("mp_it").search('', {'filter':[query]})
    log.info(results)
    return "I risultati della ricerca: \n"+str(results['hints'][1]['description'])

def gen_new_param(lista):
    pos = random.randint(0,len(lista))
    return lista[pos]

def random_search():
    client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_API_KEY)
    results = client.index("mp_it").search(param)
    param = gen_new_param(results['hints'][1]['description'].split())
    log.info(results['hints'][1]['description'])
    return str(results)

@hook("before_cat_reads_message")
def cron_scheduler(user_input,cat):
    if user_input.text == "Avvia schedule":
        cat.white_rabbit.schedule_cron_job(random_search, job_id="nightly_upgrade_plugins", hour=9, minute=36)
        print("Job schedulato.")
    


import meilisearch

MEILISEARCH_URL = "http://meilisearch:7700"
MEILISEARCH_MASTER_KEY = 'A6Tw7yTI37T4Rx5NINnoG2ScZssgy911qaDvSbx7oyY'
client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_MASTER_KEY)

client.index('itinerary').delete()
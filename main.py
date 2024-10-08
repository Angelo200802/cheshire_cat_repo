from dotenv import load_dotenv

print(load_dotenv())

import os
print(os.getenv('MEILI_MASTER_KEY'))

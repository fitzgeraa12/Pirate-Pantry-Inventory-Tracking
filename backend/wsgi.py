import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import api
import database

db = database.connect(locally=False)
application = api.create_app(db, is_local=False)

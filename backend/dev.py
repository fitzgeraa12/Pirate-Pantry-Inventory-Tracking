import sys
import os
from flask.cli import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

import api  # now imports backend/api/api.py correctly

# import .env
load_dotenv()

if __name__ == '__main__':
    api.app.run(debug=True)


import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

import api  # now imports backend/api/api.py correctly

if __name__ == '__main__':
    api.app.run(debug=True)


from typing import Optional
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath('/workspaces/Pirate-Pantry-Inventory-Tracking/backend/api'))
from db import query, rows_to_list

def get_checkout():
    rows = query('SELECT * FROM checkout')
    return rows_to_list(rows)
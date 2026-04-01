from typing import Optional
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath('/workspaces/Pirate-Pantry-Inventory-Tracking/backend/api'))
from db import query, rows_to_list


def get_checkout():
    rows = query('SELECT * FROM total_checkouts')
    return rows


def new_checkout(
        checkout_id: Optional[list[str]] = None,
        id: Optional[int] = None,
        name: str = '',
        brand: Optional[str] = '',
        num_checked_out: int = 0,
        checkout_time: str = ''
):
    query('INSERT INTO total_checkouts VALUES (?, ?, ?, ?, ?, ?)', [checkout_id, id, name, brand, checked_out, checkout_time])
    


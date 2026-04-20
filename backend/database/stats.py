from typing import Optional
import os
import sys
from datetime import datetime, timedelta
from collections import Counter
import matplotlib.pyplot as plt # pip install matplotlib

sys.path.append(os.path.abspath('/workspaces/Pirate-Pantry-Inventory-Tracking/backend/api'))
from db import query, rows_to_list, get_tags_for_item

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
    query('INSERT INTO total_checkouts VALUES (?, ?, ?, ?, ?, ?)', [checkout_id, id, name, brand, num_checked_out, checkout_time])

def parse_date(date:str):
    return datetime.strptime(date, '%m-%d-%Y').strftime('%Y-%m-%d')

# TODO: Total number of items checked out weekly
def total_range(start: str, end: str) -> int:
    s, e = parse_date(start), parse_date(end)
    rows = query("SELECT SUM(num_checked_out)\
                 FROM total_checkouts\
                 WHERE checkout_time >= ? AND checkout_time <= ?", [s,e])
    total = rows[0][0] if rows and rows[0][0] else 0

    fig = plt.figure(figsize=(8, 1))
    plt.figtext(0.5, 0.5, f'Total Items Taken From {start} To {end}:  {total}',
                ha='center', va='center', fontsize=14, fontweight='bold')
    return fig


# TODO: Top 10 items that got checked out weekly
def top_item(start:str, end:str):
    s, e = parse_date(start), parse_date(end)
    rows = query("SELECT name, SUM(num_checked_out) AS total\
                FROM total_checkouts\
                WHERE checkout_time >= ? AND checkout_time <= ?\
                GROUP BY name\
                ORDER BY total DESC\
                LIMIT 10", [s, e])
    rows = rows_to_list(rows)
    if not rows:
        return None

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')
    ax.set_title(f'Top 10 Items From {start} To {end}', fontsize=14, fontweight='bold', pad=20)

    table = ax.table(
        cellText=[[i+1, row[0], row[1]] for i, row in enumerate(rows)],
        colLabels=['Rank', 'Name', 'Checkout Quantity'],
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width([0, 1, 2])

    plt.tight_layout()
    return fig

# TODO: Percentage of item tags checked out weekly (pie chart). Item tags represent categories of items, including food types, allergy free groups, toiletries, etc
def tag_range(start:str, end:str):
    s, e = parse_date(start), parse_date(end)
    rows = query("SELECT id\
                  FROM total_checkouts\
                  WHERE checkout_time >= ? AND checkout_time <= ?", [s,e])
    tags = []

    for row in rows:
        id_tag = get_tags_for_item(id=row[0])
        tags.extend(id_tag)

    if not tags:
        return {}, None
    
    freq = Counter(tags)
    for key in list(freq.keys()):
        freq[key] = freq[key]/len(tags)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(freq.values(), labels=freq.keys(), autopct='%1.1f%%', startangle=140)
    ax.set_title(f'Percentage of Item Tags Taken From {start} To {end}', fontsize=14, fontweight='bold')
    plt.tight_layout() 

    return fig

# TODO: Number of checkouts per weekday (bar graph)
def checkout_daily(start:str, end:str):
    s, e = parse_date(start), parse_date(end)
    rows = query(
        "SELECT DATE(checkout_time) AS day, COUNT(DISTINCT checkout_id) AS total "
        "FROM total_checkouts "
        "WHERE checkout_time >= ? AND checkout_time <= ? "
        "GROUP BY day "
        "ORDER BY day", [s, e]
    )
    counts = {row[0]: row[1] for row in (rows or [])}

    result = {}
    current = datetime.strptime(s, '%Y-%m-%d')
    ed = datetime.strptime(e, '%Y-%m-%d')
    while current <= ed:
        key = current.strftime('%A %m-%d-%Y')
        result[key] = counts.get(current.strftime('%Y-%m-%d'), 0)
        current += timedelta(days=1)

    fig, ax = plt.subplots(figsize=(max(8, len(result) * 1.2), 6))
    bars = ax.bar(result.keys(), result.values(), color='steelblue')
    ax.set_title(f'Checkouts per Day From {start} To {end}', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Checkouts')
    ax.bar_label(bars)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()

    return fig

# TODO: Number of checkouts per hour (separate bar graphs for each day of the week)
def checkout_hourly(start:str, end:str):
    s, e = parse_date(start), parse_date(end)
    rows = query("SELECT strftime('%H', checkout_time) AS hour, COUNT(DISTINCT checkout_id) AS total\
                  FROM total_checkouts\
                  WHERE checkout_time >= ? AND checkout_time <= ?\
                  GROUP BY hour\
                  ORDER BY hour", [s,e])
    counts = {row[0]: row[1] for row in (rows or [])}
    result = {f'{h:02d}:00': counts.get(f'{h:02d}', 0) for h in range(24)}

    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(result.keys(), result.values(), color='steelblue')
    ax.set_title(f'Checkouts per Hour From {start} To {end}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Hours')
    ax.set_ylabel('Number of Checkouts')
    ax.bar_label(bars)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    return fig


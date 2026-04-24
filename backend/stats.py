from typing import Optional
import os
import sys
import uuid
from datetime import datetime, timedelta
from collections import Counter
import matplotlib.pyplot as plt # pip install matplotlib

from backend.database import Database

_db: Optional[Database] = None

def init(db: Database) -> None:
    global _db
    _db = db

def query(sql: str, params: list = []) -> list:
    assert _db is not None, "stats.init(db) must be called before using stats"
    return _db.query(sql, params)

def rows_to_list(rows: list) -> list:
    return [list(row.values()) for row in rows]

def get_tags_for_item(id: str) -> list[str]:
    assert _db is not None, "stats.init(db) must be called before using stats"
    rows = _db.query("SELECT tag_label FROM product_tags WHERE product_id = ?", [id])
    return [row['tag_label'] for row in rows]

def next_checkout_id() -> str:
    '''Return a unique checkout_id (UUID).'''
    return str(uuid.uuid4())

def new_checkout(
        checkout_id: str,
        id: Optional[str] = None,
        name: str = '',
        brand: Optional[str] = '',
        num_checked_out: int = 0,
        checkout_time: str = ''
):
    if not checkout_time:
        checkout_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query('INSERT INTO total_checkouts (checkout_id, product_id, name, brand, num_checked_out, checkout_time) VALUES (?, ?, ?, ?, ?, ?)', [checkout_id, id, name, brand or '', num_checked_out, checkout_time])

def parse_date(date:str):
    '''Convert MM-DD-YYYY to YYYY-MM-DD for SQL comparisons '''
    return datetime.strptime(date, '%m-%d-%Y').strftime('%Y-%m-%d')

def total_range(start: str, end: str):
    '''Text figure of total number of items checked out from start to end date'''
    s, e = parse_date(start), parse_date(end)
    rows = query("SELECT SUM(num_checked_out) AS total\
                 FROM total_checkouts\
                 WHERE checkout_time >= ? AND checkout_time <= ?", [s,e])
    total = rows[0]['total'] if rows and rows[0]['total'] else 0
    fig = plt.figure(figsize=(8, 1))
    plt.figtext(0.5, 0.5, f'Total Items Taken From {start} To {end}:  {total}',
                ha='center', va='center', fontsize=14, fontweight='bold')
    return fig


def top_item(start:str, end:str):
    '''Table of top 10 items that got checked out from start to end date'''
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

def tag_range(start:str, end:str):
    '''Pie chart of percentage of item tags checked out from start to end date'''
    s, e = parse_date(start), parse_date(end)
    rows = query("SELECT product_id\
                  FROM total_checkouts\
                  WHERE checkout_time >= ? AND checkout_time <= ?", [s,e])
    tags = []
    for row in rows:
        id_tag = get_tags_for_item(id=row['product_id'])
        tags.extend(id_tag)
    if not tags:
        return None
    freq = Counter(tags)
    for key in freq:
        freq[key] = freq[key]/len(tags)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(freq.values(), labels=freq.keys(), autopct='%1.1f%%', startangle=140)
    ax.set_title(f'Percentage of Item Tags Taken From {start} To {end}', fontsize=14, fontweight='bold')
    plt.tight_layout() 
    return fig

def checkout_daily(start:str, end:str):
    '''Bar graph of the number of checkouts from start to end date'''
    s, e = parse_date(start), parse_date(end)
    rows = query(
        "SELECT DATE(checkout_time) AS day, COUNT(DISTINCT checkout_id) AS total "
        "FROM total_checkouts "
        "WHERE checkout_time >= ? AND checkout_time <= ? "
        "GROUP BY day "
        "ORDER BY day", [s, e]
    )
    counts = {row['day']: row['total'] for row in (rows or [])}

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
    ax.set_ylim(bottom=0)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()
    return fig

# def checkout_hourly(start:str, end:str):
#     '''Number of checkouts per hour (separate bar graphs for each day of the week)'''
#     s, e = parse_date(start), parse_date(end)
#     rows = query("SELECT strftime('%H', checkout_time) AS hour, COUNT(DISTINCT checkout_id) AS total\
#                   FROM total_checkouts\
#                   WHERE checkout_time >= ? AND checkout_time <= ?\
#                   GROUP BY hour\
#                   ORDER BY hour", [s,e])
#     counts = {row['hour']: row['total'] for row in (rows or [])}
#     result = {f'{h:02d}:00': counts.get(f'{h:02d}', 0) for h in range(24)}
#     fig, ax = plt.subplots(figsize=(14, 6))
#     bars = ax.bar(result.keys(), result.values(), color='steelblue')
#     ax.set_title(f'Checkouts per Hour From {start} To {end}', fontsize=14, fontweight='bold')
#     ax.set_xlabel('Hours')
#     ax.set_ylabel('Number of Checkouts')
#     ax.set_ylim(bottom=0)
#     ax.bar_label(bars)
#     plt.xticks(rotation=45, ha='right')
#     plt.tight_layout()
#     return fig


def checkout_hourly(start: str, end: str):
   '''Number of checkouts per hour (separate bar graph for each day in range)'''
   s, e = parse_date(start), parse_date(end)
    
   rows = query("""
      SELECT DATE(checkout_time) AS day,
               strftime('%H', checkout_time) AS hour,
               COUNT(DISTINCT checkout_id) AS total
      FROM total_checkouts
      WHERE checkout_time >= ? AND checkout_time <= ?
      GROUP BY day, hour
      ORDER BY day, hour
   """, [s, e])

   # Group counts by day
   from collections import defaultdict
   daily_counts: dict[str, dict[str, int]] = defaultdict(dict)
   for row in (rows or []):
      daily_counts[row['day']][row['hour']] = row['total']

   # Build list of all days in range
   days = []
   current = s
   while current <= e:
      days.append(current.strftime('%Y-%m-%d'))
      current += timedelta(days=1)

   hours = [f'{h:02d}:00' for h in range(24)]

   fig, axes = plt.subplots(
      nrows=len(days), ncols=1,
      figsize=(14, 5 * len(days)),
      sharey=False
   )

   if len(days) == 1:
      axes = [axes]  # make iterable if only one day

   for ax, day in zip(axes, days):
      counts = daily_counts.get(day, {})
      values = [counts.get(f'{h:02d}', 0) for h in range(24)]
      bars = ax.bar(hours, values, color='steelblue')
      ax.set_title(day, fontsize=12, fontweight='bold')
      ax.set_xlabel('Hour')
      ax.set_ylabel('Checkouts')
      ax.set_ylim(bottom=0)
      ax.bar_label(bars)
      ax.tick_params(axis='x', rotation=45)

   fig.suptitle(f'Checkouts per Hour: {start} to {end}', fontsize=14, fontweight='bold')
   plt.tight_layout()
   return fig

    


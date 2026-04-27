from typing import Optional
import os
import sys
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import Counter
import matplotlib.pyplot as plt # pip install matplotlib
from collections import defaultdict 
from backend.database import Database

_db: Optional[Database] = None

# --------------------------------------------------
# Styles
# --------------------------------------------------
plt.rcParams.update({
    'figure.dpi': 150,
    'figure.facecolor': '#F5F5F5',
    'axes.facecolor': 'white',
    'axes.grid': True,
    'axes.grid.axis': 'y',
    'grid.color': '#E0E0E0',
    'grid.linestyle': '--',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'font.family': 'DejaVu Sans',
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'text.color': '#111111',
})

BAR_COLOR = '#FFCD00'
PIE_COLORS = [
    '#FFCD00', '#222222', '#A0A0A0', '#C8A200',
    '#444444', '#E6B800', '#666666', '#FFE066'
]

# --------------------------------------------------
# Database
# --------------------------------------------------

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
        checkout_time = datetime.now(ZoneInfo('America/Chicago')).strftime('%Y-%m-%d %H:%M:%S')
    query('INSERT INTO total_checkouts (checkout_id, product_id, name, brand, num_checked_out, checkout_time) VALUES (?, ?, ?, ?, ?, ?)', [checkout_id, id, name, brand or '', num_checked_out, checkout_time])

def parse_date(date:str):
    '''Convert MM-DD-YYYY to YYYY-MM-DD for SQL comparisons '''
    return datetime.strptime(date, '%m-%d-%Y').strftime('%Y-%m-%d')

# --------------------------------------------------
# Graphs and Charts
# --------------------------------------------------
def total_range(start: str, end: str):
    '''Text figure of total number of items checked out from start to end date'''
    s, e = parse_date(start), parse_date(end)
    rows = query("SELECT SUM(num_checked_out) AS total\
                 FROM total_checkouts\
                 WHERE checkout_time >= ? AND checkout_time <= ?", [s,e])
    total = rows[0]['total'] if rows and rows[0]['total'] else 0
    fig = plt.figure(figsize=(8, 2))
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
    for col in range(3):
        table[0, col].set_facecolor('#000000')
        table[0, col].set_text_props(color='white', fontweight='bold')
    for col in range(3):
        table[1, col].set_facecolor('#FFCD00')
        table[1, col].set_text_props(fontweight='bold')
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

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(list(freq.values()), labels=freq.keys(), autopct='%1.1f%%', startangle=140, 
           colors=PIE_COLORS, wedgeprops=dict(edgecolor='white', linewidth=1.5))
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
    bars = ax.bar(result.keys(), result.values(), color=BAR_COLOR)
    ax.set_title(f'Checkouts per Day From {start} To {end}', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Checkouts')
    labels = [v if v > 0 else '' for v in result.values()]  # only label nonzero bars
    ax.bar_label(bars, labels=labels, padding=3)
    ax.set_ylim(bottom=0)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()
    return fig



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
   daily_counts: dict[str, dict[str, int]] = defaultdict(dict)
   for row in (rows or []):
      daily_counts[row['day']][row['hour']] = row['total']

   days = []
   current = datetime.strptime(s, '%Y-%m-%d')  
   ed = datetime.strptime(e, '%Y-%m-%d')
   while current <= ed:
      days.append(current.strftime('%Y-%m-%d'))
      current += timedelta(days=1)

   hours = [f'{h:02d}:00' for h in range(24)]

   fig, axes = plt.subplots(
      nrows=len(days), ncols=1,
      figsize=(14, 5 * len(days)),
      sharey=False
   )

   if len(days) == 1:
      axes = [axes]  

   for ax, day in zip(axes, days):
      counts = daily_counts.get(day, {})
      values = [counts.get(f'{h:02d}', 0) for h in range(24)]
      bars = ax.bar(hours, values, color=BAR_COLOR)
      ax.set_title(day, fontsize=12, fontweight='bold')
      ax.set_xlabel('Hour')
      ax.set_ylabel('Checkouts')
      ax.set_ylim(bottom=0)
      # only label nonzero bars
      labels = [v if v > 0 else '' for v in values]
      ax.bar_label(bars, labels=labels, padding=3)
      ax.tick_params(axis='x', rotation=45)

   fig.suptitle(f'Checkouts per Hour: {start} to {end}', fontsize=14, fontweight='bold')
   plt.tight_layout()
   return fig

    


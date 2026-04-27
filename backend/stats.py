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
    'axes.edgecolor': '#DDDDDD',
    'axes.linewidth': 1,
    'grid.alpha': 0.5,
})

BAR_COLOR = '#FFCD00'

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
def report_title(start: str, end: str):
    fig, ax = plt.subplots(figsize=(12, 2.5))
    ax.axis('off')

    fig.patch.set_facecolor('white')

    ax.text(
        0.5, 0.65,
        'Pirate Pantry Statistics Report',
        ha='center',
        fontsize=20,
        fontweight='bold',
        color='#111111'
    )

    ax.text(
        0.5, 0.3,
        f'{start} → {end}',
        ha='center',
        fontsize=12,
        color='#666666'
    )

    return fig

def total_range(start: str, end: str):
    '''Text figure of total number of items checked out from start to end date'''
    s, e = parse_date(start), parse_date(end)
    rows = query("SELECT SUM(num_checked_out) AS total\
                 FROM total_checkouts\
                 WHERE checkout_time >= ? AND checkout_time <= ?", [s,e])
    total = rows[0]['total'] if rows and rows[0]['total'] else 0
    
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    ax.text(0.5, 0.65, f'Total Items Taken From {start} To {end}:',
            ha='center', fontsize=14, fontweight='bold', color='#111111')

    ax.text(0.5, 0.3, f'{total}',
            ha='center', fontsize=28, fontweight='bold', color='#FFCD00')
    
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
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')
    ax.set_title(f'Top 10 Items From {start} To {end}', fontsize=14, fontweight='bold', pad=20)
    table = ax.table(
        cellText=[[i+1, row[0], row[1]] for i, row in enumerate(rows)],
        colLabels=['Rank', 'Name', 'Checkout Quantity'],
        cellLoc='center',
        loc='center'
    )
    table.scale(1.5,2)
    table.auto_set_font_size(True)
    # table.set_fontsize(10)
    table.auto_set_column_width([0, 1, 2])
    for col in range(3):
        table[0, col].set_facecolor('#000000')
        table[0, col].set_text_props(color='white', fontweight='bold')
    for col in range(3):
        table[1, col].set_facecolor('#FFCD00')
        table[1, col].set_text_props(fontweight='bold')
    plt.tight_layout(pad=3)
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

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.pie(list(freq.values()), labels=freq.keys(), autopct='%1.1f%%', 
           startangle=140, wedgeprops=dict(edgecolor='white', linewidth=1.5), textprops={'fontsize': 12})
    ax.set_title(f'Percentage of Item Tags Taken From {start} To {end}', fontsize=14, fontweight='bold')
    plt.tight_layout(pad=2) 
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

    fig, ax = plt.subplots(figsize=(max(10, len(result) * 1.5), 6))
    bars = ax.bar(result.keys(), result.values(), color=BAR_COLOR)
    ax.set_title(f'Checkouts per Day From {start} To {end}', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Checkouts')
    labels = [v if v > 0 else '' for v in result.values()]  # only label nonzero bars
    ax.bar_label(bars, labels=labels, padding=3)
    ax.set_ylim(bottom=0)
    ax.margins(x=0.02)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout(pad=2)
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
        figsize=(12, 5 * len(days)),
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
        if all(v == 0 for v in values):
            ax.set_title(
                datetime.strptime(day, '%Y-%m-%d').strftime('%A, %b %d'),
                fontsize=11, pad=10
            )

            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])

            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color('#DDDDDD')

            ax.text(
                0.5, 0.5,
                'No checkout activity',
                ha='center', va='center',
                fontsize=11,
                color='#999999',
                transform=ax.transAxes
            )
            continue

    fig.suptitle(f'Checkouts per Hour: {start} to {end}', fontsize=16, fontweight='bold',y=0.995)
    plt.subplots_adjust(hspace=0.5)
    plt.tight_layout()
    return fig

    


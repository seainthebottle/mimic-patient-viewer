import psycopg2
import json

with open('connection.json', 'r') as f:
    config = json.load(f)

conn = psycopg2.connect(**config)
cursor = conn.cursor()

# Keywords for settings
settings_keywords = {
    'MV': ['PEEP', 'FiO2', 'Tidal Volume', 'Respiratory Rate'],
    'CRRT': ['Blood Flow', 'Ultrafiltrate', 'Replacement Rate'],
    'ECMO': ['Flow', 'Sweep', 'RPM', 'P1', 'P2']
}

all_keywords = [k for v in settings_keywords.values() for k in v]
query = "SELECT itemid, label, abbreviation, category FROM mimiciv_icu.d_items WHERE "
query += " OR ".join([f"label ILIKE '%{k}%'" for k in all_keywords])

cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()

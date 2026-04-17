import psycopg2
import json

with open('connection.json', 'r') as f:
    config = json.load(f)

conn = psycopg2.connect(**config)
cursor = conn.cursor()

keywords = ['Ventilator', 'CRRT', 'ECMO', 'Extracorporeal']
query = "SELECT itemid, label, abbreviation, category FROM mimiciv_icu.d_items WHERE "
query += " OR ".join([f"label ILIKE '%{k}%'" for k in keywords])

cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()

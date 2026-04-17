import sys
import os
import json
import psycopg2

# Add src to sys.path
sys.path.append(os.path.abspath('src'))

from data_manage.data_model import DataModel

with open('connection.json', 'r') as f:
    config = json.load(f)

dm = DataModel(config)
dm.connect_db()

# Try to find a patient with some treatments
query = """
SELECT hadm_id, count(*) 
FROM mimiciv_icu.procedureevents 
WHERE itemid IN (225792, 225794, 225802, 224660) 
GROUP BY hadm_id 
LIMIT 5
"""
dm.cursor.execute(query)
rows = dm.cursor.fetchall()
print("Patients with treatments:", rows)

if rows:
    hadm_id = rows[0][0]
    # Get a date for this patient
    dm.cursor.execute("SELECT starttime::DATE FROM mimiciv_icu.procedureevents WHERE hadm_id = %s LIMIT 1", (hadm_id,))
    chart_date = dm.cursor.fetchone()[0]
    print(f"Testing for HADM_ID: {hadm_id}, Date: {chart_date}")
    
    intervals = dm.fetch_treatment_intervals(hadm_id, str(chart_date))
    print("Intervals:", intervals)
    
    settings = dm.fetch_treatment_settings(hadm_id, str(chart_date))
    print("Settings count:", len(settings))

dm.disconnect_db()

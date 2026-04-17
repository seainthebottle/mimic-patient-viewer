import sys
import os
import json
import psycopg2

# Add src to sys.path
sys.path.append(os.path.abspath('src'))

from data_manage.data_model import DataModel
from vital_sheet.vital_summary import VitalSummary

with open('connection.json', 'r') as f:
    config = json.load(f)

dm = DataModel(config)
dm.connect_db()
vs = VitalSummary(dm)

# Try to find a patient with both ABP and NIBP
query = """
SELECT hadm_id, count(*) 
FROM mimiciv_icu.chartevents 
WHERE itemid IN (220050, 220179) 
GROUP BY hadm_id 
HAVING count(DISTINCT itemid) = 2
LIMIT 5
"""
dm.cursor.execute(query)
rows = dm.cursor.fetchall()
print("Patients with both ABP and NIBP:", rows)

if rows:
    hadm_id = rows[0][0]
    # Get a date for this patient
    dm.cursor.execute("SELECT charttime::DATE FROM mimiciv_icu.chartevents WHERE hadm_id = %s AND itemid IN (220050, 220179) LIMIT 1", (hadm_id,))
    chart_date = dm.cursor.fetchone()[0]
    print(f"Testing for HADM_ID: {hadm_id}, Date: {chart_date}")
    
    abps = vs.calculate_ABPs_distribution(hadm_id)
    nbps = vs.calculate_NBPs_distribution(hadm_id)
    print("ABPs count:", len(abps))
    print("NBPs count:", len(nbps))

dm.disconnect_db()

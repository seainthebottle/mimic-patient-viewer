import psycopg2
import json

def find_patient_with_vaso():
    try:
        with open('connection.json') as f:
            config = json.load(f)
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        with open('hadm_ids.txt') as f:
            hadm_ids = [line.strip() for line in f if line.strip()]
            
        itemids = (221906, 222315, 221289, 221662, 221653, 221749)
        
        print("Checking patients for vasopressors...")
        for hadm_id in hadm_ids:
            cur.execute("SELECT COUNT(*) FROM mimiciv_icu.inputevents WHERE hadm_id = %s AND itemid IN %s", (hadm_id, itemids))
            count = cur.fetchone()[0]
            if count > 0:
                print(f"HADM_ID {hadm_id} has {count} vasopressor events.")
                # Get one date
                cur.execute("SELECT starttime::DATE FROM mimiciv_icu.inputevents WHERE hadm_id = %s AND itemid IN %s LIMIT 1", (hadm_id, itemids))
                date = cur.fetchone()[0]
                print(f"Sample date: {date}")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_patient_with_vaso()

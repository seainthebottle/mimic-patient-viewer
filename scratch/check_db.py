import psycopg2
import json

def check_data():
    try:
        with open('connection.json') as f:
            config = json.load(f)
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        # Check table columns
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'mimiciv_icu' AND table_name = 'inputevents'")
        columns = [row[0] for row in cur.fetchall()]
        print(f"Columns in inputevents: {columns}")
        
        # Sample data
        query = """
        SELECT itemid, starttime, endtime, rate, rateuom 
        FROM mimiciv_icu.inputevents 
        WHERE itemid IN (221906, 222315, 221289, 221662, 221653) 
        LIMIT 5
        """
        cur.execute(query)
        rows = cur.fetchall()
        print("\nSample vasopressor data:")
        for row in rows:
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()

import psycopg2
import pandas as pd
from datetime import timedelta

class VitalSummary:
    def __init__(self, dbname, user, password, host, hadm_id):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.hadm_id = hadm_id


    def fetch_event_data(self, hadm_id, item_id):
        self.conn = psycopg2.connect(
            dbname=self.dbname, user=self.user, password=self.password, host=self.host)
        query = """
        SELECT charttime, valuenum
        FROM mimiciv_icu.chartevents
        WHERE itemid = %s AND hadm_id = %s
        """
        data = pd.read_sql_query(query, self.conn, params=(item_id, hadm_id,))
        self.conn.close()
        return data
    
    def calculate_event_distribution(self, item_id, item_abbr):
        data = self.fetch_event_data(self.hadm_id, item_id)  # NBPs
        if data.empty: return pd.DataFrame({'timestamp': [], item_abbr:[]})

        data['charttime'] = pd.to_datetime(data['charttime'])

        # Initialize a DataFrame to hold the fluid amounts distributed by hours
        results = []
        
        # Iterate through each event
        for index, row in data.iterrows():
            chart_hour = row['charttime'].floor('h')
            valuenum = row['valuenum']
            results.append({'timestamp': chart_hour, item_abbr: valuenum})

        # Summarize by hour
        results_df = pd.DataFrame(results)
        summary = results_df.groupby('timestamp')[item_abbr].mean()

        return summary
    
    def calculate_NBPs_distribution(self):
        return self.calculate_event_distribution('220179', 'NBPs')
    
    def calculate_NBPd_distribution(self):
        return self.calculate_event_distribution('220180', 'NBPd')
    
    def calculate_HR_distribution(self):
        return self.calculate_event_distribution('220045', 'HR')
    
    def calculate_BT_distribution(self):
        return self.calculate_event_distribution('223761', 'BT').sub(32).mul(5).div(9)

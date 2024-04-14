import psycopg2
import pandas as pd
from datetime import timedelta

class FluidInjectionSummary:
    def __init__(self, dbname, user, password, host):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        
    def fetch_data(self):
        query = """
        SELECT starttime, endtime, amount, amountuom
        FROM mimiciv_icu.inputevents
        WHERE amountuom = 'ml' AND hadm_id = 28174188
        """
        self.data = pd.read_sql_query(query, self.conn)
    
    def calculate_fluid_distribution(self):
        self.data['starttime'] = pd.to_datetime(self.data['starttime'])
        self.data['endtime'] = pd.to_datetime(self.data['endtime'])

        # Initialize a DataFrame to hold the fluid amounts distributed by hours
        results = []
        
        # Iterate through each event
        for index, row in self.data.iterrows():
            start_hour = row['starttime'].floor('H')
            end_hour = row['endtime'].floor('H') + timedelta(hours=1)  # inclusive of the end hour
            
            # Calculate total duration in hours
            total_duration = (row['endtime'] - row['starttime']).total_seconds() / 3600
            
            # Assign amount proportionally to each hour within the range
            current_hour = start_hour
            while current_hour < end_hour:
                hour_end = current_hour + timedelta(hours=1)
                # Calculate overlap with the event time in this hour
                overlap_start = max(row['starttime'], current_hour)
                overlap_end = min(row['endtime'], hour_end)
                overlap_duration = (overlap_end - overlap_start).total_seconds() / 3600
                
                if overlap_duration > 0:
                    hour_amount = (overlap_duration / total_duration) * row['amount']
                    results.append({'hour': current_hour, 'amount': hour_amount})
                
                current_hour += timedelta(hours=1)

        # Summarize by hour
        results_df = pd.DataFrame(results)
        self.summary = results_df.groupby('hour')['amount'].sum()

    def print_summary(self):
        print(self.summary)

    def close_connection(self):
        self.conn.close()

# Usage
db_params = {
    'dbname': 'mimiciv',
    'user': 'postgres',
    'password': 'Mokpswd7!',
    'host': 'localhost'
}
summary = FluidInjectionSummary(**db_params)
summary.fetch_data()
summary.calculate_fluid_distribution()
summary.print_summary()
summary.close_connection()

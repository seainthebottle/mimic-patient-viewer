import psycopg2
import pandas as pd
from datetime import timedelta

class FluidSummary:
    def __init__(self, dbname, user, password, host, hadm_id):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.hadm_id = hadm_id
        

    def fetch_input_data(self, hadm_id):
        self.conn = psycopg2.connect(
            dbname=self.dbname, user=self.user, password=self.password, host=self.host)
        query = """
        SELECT starttime, endtime, amount, amountuom
        FROM mimiciv_icu.inputevents
        WHERE amountuom = 'ml' AND hadm_id = %s
        """
        data = pd.read_sql_query(query, self.conn, params=(hadm_id,))
        self.conn.close()
        return data
    

    def fetch_output_data(self, hadm_id):
        self.conn = psycopg2.connect(
            dbname=self.dbname, user=self.user, password=self.password, host=self.host)
        query = """
        SELECT charttime, value, valueuom
        FROM mimiciv_icu.outputevents
        WHERE valueuom = 'ml' AND hadm_id = %s
        """
        data = pd.read_sql_query(query, self.conn, params=(hadm_id,))
        self.conn.close()
        return data


    def calculate_input_distribution(self):
        data = self.fetch_input_data(self.hadm_id)

        data['starttime'] = pd.to_datetime(data['starttime'])
        data['endtime'] = pd.to_datetime(data['endtime'])

        # Initialize a DataFrame to hold the fluid amounts distributed by hours
        results = []
        
        # Iterate through each event
        for index, row in data.iterrows():
            # 시작 시간과 끝시간을 정각 단위로 지정한다.
            start_hour = row['starttime'].floor('h')
            end_hour = row['endtime'].floor('h') + timedelta(hours=1)  # inclusive of the end hour
            
            # Calculate total duration in hours
            total_duration = (row['endtime'] - row['starttime']).total_seconds() / 3600
            
            # 한 시간 단위로 시간을 훓어가며 계산한다.
            current_hour = start_hour
            while current_hour < end_hour:
                hour_end = current_hour + timedelta(hours=1)
                # Calculate overlap with the event time in this hour
                overlap_start = max(row['starttime'], current_hour)
                overlap_end = min(row['endtime'], hour_end)
                # 해당 시간대 실제 겹치는 시간을 계산한다.
                overlap_duration = (overlap_end - overlap_start).total_seconds() / 3600
                
                # 해당 시간분량만큼 더해준다.
                if overlap_duration > 0:
                    hour_amount = (overlap_duration / total_duration) * row['amount']
                    results.append({'hour': current_hour, 'amount': hour_amount})
                    print("hour: " + str(current_hour) + "/ amount: " + str(hour_amount))
                
                current_hour += timedelta(hours=1)

        # Summarize by hour
        results_df = pd.DataFrame(results)
        summary = results_df.groupby('hour')['amount'].sum()

        return summary
    

    def calculate_output_distribution(self):
        data = self.fetch_output_data(self.hadm_id)

        data['starttime'] = pd.to_datetime(data['starttime'])
        data['endtime'] = pd.to_datetime(data['endtime'])

        # Initialize a DataFrame to hold the fluid amounts distributed by hours
        results = []
        
        # Iterate through each event
        for index, row in data.iterrows():
            # 시작 시간과 끝시간을 정각 단위로 지정한다.
            chart_hour = row['charttime'].floor('h')
            amount = row['amount']
            results.append({'hour': chart_hour, 'amount': amount})

        # Summarize by hour
        results_df = pd.DataFrame(results)
        summary = results_df.groupby('hour')['amount'].sum()

        return summary

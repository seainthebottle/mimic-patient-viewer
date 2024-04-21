import psycopg2
import pandas as pd
from datetime import timedelta

class VitalSummary:
    def __init__(self, dataModel):
        self.dataModel = dataModel
    
    def calculate_event_distribution(self, hadm_id, item_id, item_abbr):
        data = self.dataModel.fetch_event_data(hadm_id, item_id)  # NBPs
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
    
    def calculate_NBPs_distribution(self, hadm_id):
        return self.calculate_event_distribution(hadm_id, '220179', 'NBPs')
    
    def calculate_NBPd_distribution(self, hadm_id):
        return self.calculate_event_distribution(hadm_id, '220180', 'NBPd')
    
    def calculate_HR_distribution(self, hadm_id):
        return self.calculate_event_distribution(hadm_id, '220045', 'HR')
    
    def calculate_BT_distribution(self, hadm_id):
        return self.calculate_event_distribution(hadm_id, '223761', 'BT').sub(32).mul(5).div(9)

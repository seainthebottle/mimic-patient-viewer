import psycopg2
import pandas as pd
from datetime import timedelta

class VitalSummary:
    def __init__(self, dataModel):
        self.dataModel = dataModel

    def clear(self):
        pass
    
    def calculate_event_distribution(self, hadm_id, item_id, item_abbr):
        data = self.dataModel.fetch_event_data(hadm_id, item_id)  # NBPs
        if data.empty: return pd.DataFrame({'timestamp': pd.Series(dtype='datetime64[ns]'), item_abbr: pd.Series(dtype='float64')})

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
        summary = results_df.groupby('timestamp')[item_abbr].mean().reset_index()

        return summary
    
    def calculate_NBPs_distribution(self, hadm_id):
        return self.calculate_event_distribution(hadm_id, '220179', 'NBPs')
    
    def calculate_NBPd_distribution(self, hadm_id):
        return self.calculate_event_distribution(hadm_id, '220180', 'NBPd')
    
    def calculate_HR_distribution(self, hadm_id):
        return self.calculate_event_distribution(hadm_id, '220045', 'HR')
    
    def calculate_BT_distribution(self, hadm_id):
        df = self.calculate_event_distribution(hadm_id, '223761', 'BT')
        # BT 컬럼에 대해서만 화씨에서 섭씨로 변환을 수행한다.
        # timestamp 컬럼이 포함된 데이터프레임 전체에 대해 연산하면 Datetime 연산 오류가 발생할 수 있다.
        df['BT'] = (df['BT'] - 32) * 5 / 9
        return df

    def calculate_ABPs_distribution(self, hadm_id):
        return self.calculate_event_distribution(hadm_id, '220050', 'ABPs')
    
    def calculate_ABPd_distribution(self, hadm_id):
        return self.calculate_event_distribution(hadm_id, '220051', 'ABPd')

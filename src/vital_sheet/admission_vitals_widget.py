import sys
from PyQt5 import QtWidgets, QtCore
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
from vital_sheet_widget import VitalSheetWidget  # Ensure this is correctly imported from your file
from fluid_summary import FluidSummary  # Importing the FluidSummary class
from vital_summary import VitalSummary

class AdmissionVitalsWidget(QtWidgets.QWidget):
    def __init__(self, db_config, hadm_id):
        super().__init__()
        self.db_config = db_config
        self.hadm_id = hadm_id
        self.fluid_summary = FluidSummary(dbname=db_config['dbname'], 
                                          user=db_config['user'], 
                                          password=db_config['password'], 
                                          host=db_config['host'], 
                                          hadm_id=hadm_id)
        
        self.vital_summary = VitalSummary(dbname=db_config['dbname'], 
                                          user=db_config['user'], 
                                          password=db_config['password'], 
                                          host=db_config['host'], 
                                          hadm_id=hadm_id)
        self.initUI()


    def initUI(self):
        self.setMinimumSize(1440, 800)
        layout = QtWidgets.QVBoxLayout(self)

        self.dateComboBox = QtWidgets.QComboBox()
        self.dateComboBox.activated[str].connect(self.onDateSelected)

        self.vital_fluid_data = self.loadVitalFluidData()
        self.vitalSheetWidget = VitalSheetWidget(self.vital_fluid_data)  # Assuming a default constructor is available
        layout.addWidget(self.dateComboBox)
        layout.addWidget(self.vitalSheetWidget)
        
        self.fetchAdmissionPeriods()
        self.vitalSheetWidget.drawPlotSetDate(self.beginDate)


    def fetchAdmissionPeriods(self):
        self.beginDate = None

        query = "SELECT admittime, dischtime FROM mimiciv_hosp.admissions WHERE hadm_id=%s;"
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute(query, (self.hadm_id,))
            records = cur.fetchall()
            dates = set()
            for record in records:
                start = record[0] #datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S')
                end = record[1] #datetime.strptime(record[1], '%Y-%m-%d %H:%M:%S')
                self.beginDate = start.strftime('%Y-%m-%d')
                while start <= end:
                    dates.add(start.strftime('%Y-%m-%d'))
                    start += timedelta(days=1)
            self.dateComboBox.addItems(sorted(dates))
            conn.close()
        except psycopg2.Error as e:
            print("Database error:", e)


    def onDateSelected(self, date):
        """ 날짜가 변경되면 """
        self.vitalSheetWidget.drawPlotSetDate(date)

    def loadVitalFluidData(self):
        """ 바이탈 데이터와 IO data를 불러와 정리한다. """
        # Assuming you adapt these methods to return summary for specific dates
        input_summary = self.fluid_summary.calculate_input_distribution()  # You might need to adapt this method
        output_summary = self.fluid_summary.calculate_output_distribution()  # You might need to adapt this method
        fluid_data = pd.merge(input_summary, output_summary, on='timestamp', how='outer')
        fluid_data.fillna(0, inplace=True)  # 데이터가 없는 곳은 0으로 채움
        fluid_data = fluid_data.reset_index()
        
        sbp_summary = self.vital_summary.calculate_NBPs_distribution()
        dbp_summary = self.vital_summary.calculate_NBPd_distribution()
        hr_summary = self.vital_summary.calculate_HR_distribution()
        bt_summary = self.vital_summary.calculate_BT_distribution()
        fluid_data = pd.merge(fluid_data, sbp_summary, on='timestamp', how='outer')
        fluid_data = pd.merge(fluid_data, dbp_summary, on='timestamp', how='outer')
        fluid_data = pd.merge(fluid_data, hr_summary, on='timestamp', how='outer')
        fluid_data = pd.merge(fluid_data, bt_summary, on='timestamp', how='outer')
        fluid_data.fillna(0, inplace=True)  # 데이터가 없는 곳은 0으로 채움
        return fluid_data



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = AdmissionVitalsWidget({
        'dbname': 'mimiciv',
        'user': 'postgres',
        'password': 'Mokpswd7!',
        'host': 'localhost',
        'port': '5432'
    }, '28174188')
    widget.show()
    sys.exit(app.exec_())

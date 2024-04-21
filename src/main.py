import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QTabWidget
from data_manage.data_model import DataModel
from vital_sheet.fluid_summary import FluidSummary  
from vital_sheet.vital_summary import VitalSummary
from lab_sheet.lab_sheet_widget import LabSheetWidget
from vital_sheet.vital_sheet_widget import VitalSheetWidget  
import pandas as pd

class LabDisplayWidget(QWidget):
    def __init__(self, db_config):
        super().__init__()
        self.dataModel = DataModel(db_config)
        self.fluid_summary = FluidSummary(self.dataModel)
        self.vital_summary = VitalSummary(self.dataModel)
        self.init_ui()


    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Horizontal layout for HADM_ID input and enter button
        self.hadm_id_layout = QHBoxLayout()
        self.hadm_id_input = QLineEdit(self)
        self.hadm_id_input.setPlaceholderText("Enter HADM_ID")
        self.enter_button = QPushButton('Enter', self)
        self.enter_button.clicked.connect(self.data_load_n_populate_chart_dates)

        # Add HADM_ID input and button to the horizontal layout
        self.hadm_id_layout.addWidget(self.hadm_id_input)
        self.hadm_id_layout.addWidget(self.enter_button)

        # ComboBox for selecting chart date
        self.chart_date_selector = QComboBox(self)
        self.chart_date_selector.setEnabled(False)  # Initially disabled
        self.chart_date_selector.activated[str].connect(self.on_date_selected)  # Connect selection directly to update

        # Tab widget to switch between LabSheet and VitalSheet
        self.tab_widget = QTabWidget(self)
        self.lab_sheet_widget = LabSheetWidget(self.dataModel)
        
        self.vital_sheet_widget = VitalSheetWidget()  # Assuming configuration is passed and used correctly

        self.tab_widget.addTab(self.vital_sheet_widget, "Vital Signs")
        self.tab_widget.addTab(self.lab_sheet_widget, "Lab Results")

        # Add widgets to the main vertical layout
        self.layout.addLayout(self.hadm_id_layout)
        self.layout.addWidget(self.chart_date_selector)
        self.layout.addWidget(self.tab_widget)


    def loadVitalFluidData(self, hadm_id):
        """ 
        바이탈 데이터와 IO data를 불러와 정리한다. hadm_id가 정해지면 한꺼번에 불러온다.
        """
        # Assuming you adapt these methods to return summary for specific dates
        input_summary = self.fluid_summary.calculate_input_distribution(hadm_id)  # You might need to adapt this method
        output_summary = self.fluid_summary.calculate_output_distribution(hadm_id)  # You might need to adapt this method
        fluid_data = pd.merge(input_summary, output_summary, on='timestamp', how='outer')
        fluid_data.fillna(0, inplace=True)  # 데이터가 없는 곳은 0으로 채움
        fluid_data = fluid_data.reset_index()
        
        sbp_summary = self.vital_summary.calculate_NBPs_distribution(hadm_id)
        dbp_summary = self.vital_summary.calculate_NBPd_distribution(hadm_id)
        hr_summary = self.vital_summary.calculate_HR_distribution(hadm_id)
        bt_summary = self.vital_summary.calculate_BT_distribution(hadm_id)
        fluid_data = pd.merge(fluid_data, sbp_summary, on='timestamp', how='outer')
        fluid_data = pd.merge(fluid_data, dbp_summary, on='timestamp', how='outer')
        fluid_data = pd.merge(fluid_data, hr_summary, on='timestamp', how='outer')
        fluid_data = pd.merge(fluid_data, bt_summary, on='timestamp', how='outer')
        fluid_data.fillna(0, inplace=True)  # 데이터가 없는 곳은 0으로 채움
        return fluid_data


    def data_load_n_populate_chart_dates(self):
        hadm_id = self.hadm_id_input.text().strip()
        if hadm_id:
            self.vital_fluid_data = self.loadVitalFluidData(hadm_id)

            dates = self.dataModel.get_available_dates(hadm_id)
            self.chart_date_selector.clear()
            if dates:
                # Add dates and enable the selector
                self.chart_date_selector.addItems([date.strftime("%Y-%m-%d") for date in dates])
                self.chart_date_selector.setEnabled(True)
                # Automatically select the first date
                self.chart_date_selector.setCurrentIndex(0)
                # Manually invoke the date selection event
                self.on_date_selected(self.chart_date_selector.currentText())
            else:
                self.chart_date_selector.setEnabled(False)
        else:
            self.chart_date_selector.clear()
            self.chart_date_selector.setEnabled(False)


    def on_date_selected(self, date):
        """ 날짜가 선택되면 이메 맞춰 vital sheet와 lab sheet의 자료를 업데이트하여 보여준다."""
        hadm_id = self.hadm_id_input.text().strip()
        chart_date = date.strip()
        if hadm_id and chart_date:
            self.vital_sheet_widget.setData(self.vital_fluid_data)
            self.vital_sheet_widget.drawPlotSetDate(chart_date)  # Update method needs to be implemented in VitalSheetWidget
            self.lab_sheet_widget.update_table(hadm_id, chart_date)


def main():
    app = QApplication(sys.argv)
    db_config = {
        'dbname': 'mimiciv',
        'user': 'postgres',
        'password': 'Mokpswd7!',
        'host': 'localhost',
        'port': '5432'
    }
    widget = LabDisplayWidget(db_config)
    widget.resize(1440, 800)
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

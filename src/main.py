import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QTabWidget, QCompleter, QDialog
from data_manage.data_model import DataModel
from vital_sheet.fluid_summary import FluidSummary  
from vital_sheet.vital_summary import VitalSummary
from general_info_sheet.general_info_sheet_widget import GeneralInfoSheetWidget
from note_sheet.note_sheet_widget import DischargeNoteSheetWidget
from lab_sheet.lab_sheet_widget import LabSheetWidget
from vital_sheet.vital_sheet_widget import VitalSheetWidget  
from order_sheet.order_sheet_widget import OrderSheetWidget
from emar_sheet.emar_sheet_widget import EMARSheetWidget
from search_admission import SearchAdmission
import pandas as pd

class MimicEMR(QWidget):
    def __init__(self, db_config):
        super().__init__()
        self.dataModel = DataModel(db_config)
        self.fluid_summary = FluidSummary(self.dataModel)
        self.vital_summary = VitalSummary(self.dataModel)
        self.hadm_id_file = 'hadm_ids.txt'
        self.hadm_ids = self.load_hadm_ids()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Horizontal layout for HADM_ID input and enter button
        self.hadm_id_layout = QHBoxLayout()
        self.hadm_id_input = QLineEdit(self)
        self.hadm_id_input.setPlaceholderText("Enter HADM_ID")
        # 입력을 쉽게 채울 수 있는 completer를 만든다.
        self.completer = QCompleter(self.hadm_ids, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.hadm_id_input.setCompleter(self.completer)        
        #self.show_completer = False
        #self.hadm_id_input.mousePressEvent = self.toggle_completer
        self.hadm_id_input.returnPressed.connect(self.data_load_n_populate_chart_dates)

        self.enter_button = QPushButton('Enter', self)
        self.enter_button.clicked.connect(self.data_load_n_populate_chart_dates)
        self.admission_finder_button = QPushButton('Admission Finder', self)
        self.admission_finder_button.clicked.connect(self.open_admission_finder)

        # Add HADM_ID input and button to the horizontal layout
        self.hadm_id_layout.addWidget(self.hadm_id_input)
        self.hadm_id_layout.addWidget(self.enter_button)
        self.hadm_id_layout.addWidget(self.admission_finder_button)

        # ComboBox for selecting chart date
        self.chart_date_selector = QComboBox(self)
        self.chart_date_selector.setEnabled(False)  # Initially disabled
        self.chart_date_selector.activated[str].connect(self.on_date_selected)  # Connect selection directly to update

        # 탭 위젯을 만들어 여기에 주요 탭을 붙인다.
        self.tab_widget = QTabWidget(self)
        self.general_info_sheet_widget = GeneralInfoSheetWidget(self.dataModel)
        self.note_sheet_widget = DischargeNoteSheetWidget(self.dataModel)
        self.vital_sheet_widget = VitalSheetWidget()  # Assuming configuration is passed and used correctly
        self.lab_sheet_widget = LabSheetWidget(self.dataModel)
        self.order_sheet_widget = OrderSheetWidget(self.dataModel)  # Ensure config is properly passed
        self.emar_sheet_widget = EMARSheetWidget(self.dataModel)

        self.tab_widget.addTab(self.general_info_sheet_widget, "General Information")
        self.tab_widget.addTab(self.note_sheet_widget, "Discharge Note")
        self.tab_widget.addTab(self.vital_sheet_widget, "Vital Signs")
        self.tab_widget.addTab(self.lab_sheet_widget, "Lab Results")
        self.tab_widget.addTab(self.order_sheet_widget, "Order Details")
        self.tab_widget.addTab(self.emar_sheet_widget, "EMAR")

        # Add widgets to the main vertical layout
        self.layout.addLayout(self.hadm_id_layout)
        self.layout.addWidget(self.chart_date_selector)
        self.layout.addWidget(self.tab_widget)

    def load_hadm_ids(self):
        if os.path.exists(self.hadm_id_file):
            with open(self.hadm_id_file, 'r') as file:
                return [line.strip() for line in file.readlines()]
        return []
    
    def save_hadm_id(self, hadm_id):
        # 기존에 입력한 적 있으면 리스트에서 삭제하고
        if hadm_id in self.hadm_ids:
            self.hadm_ids = list(filter(lambda x: x != hadm_id, self.hadm_ids))
        # 새로이 맨 앞에 입력 값을 삽입한다.
        self.hadm_ids.insert(0, hadm_id)
        with open(self.hadm_id_file, 'w') as file:
            for id in self.hadm_ids: file.write(id + '\n')
        self.completer.model().setStringList(self.hadm_ids)

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
        """
        환자번호를 입력하면 이 루틴을 실행한다.
        """
        hadm_id = self.hadm_id_input.text().strip()
        if hadm_id: # 환자번호가 입력되면
            self.general_info_sheet_widget.display_info(hadm_id)
            self.note_sheet_widget.display_note(hadm_id)
            self.vital_fluid_data = self.loadVitalFluidData(hadm_id)

            dates = self.dataModel.get_available_dates(hadm_id)
            self.chart_date_selector.clear()
            if dates:
                self.save_hadm_id(hadm_id)
                # Add dates and enable the selector
                self.chart_date_selector.addItems([date.strftime("%Y-%m-%d") for date in dates])
                self.chart_date_selector.setEnabled(True)
                # Automatically select the first date
                self.chart_date_selector.setCurrentIndex(0)
                # Manually invoke the date selection event
                self.on_date_selected(self.chart_date_selector.currentText())
            else:
                self.reset()
                self.chart_date_selector.setEnabled(False)
        else: # 환자번호가 입력되지 않으면
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
            self.order_sheet_widget.update_table(hadm_id, chart_date)
            self.emar_sheet_widget.update_table(hadm_id, chart_date)

    def open_admission_finder(self):
        dialog = SearchAdmission(self.dataModel)
        dialog.resize(800, 600)
        if dialog.exec_() == QDialog.Accepted:
            selected_hadm_id = dialog.get_selected_hadm_id()
            if selected_hadm_id:
                self.hadm_id_input.setText(selected_hadm_id)
                self.data_load_n_populate_chart_dates()

def main():
    app = QApplication(sys.argv)
    db_config = {
        'dbname': 'mimiciv',
        'user': 'seainthebottle',
        'password': 'Mokpswd7!',
        'host': 'localhost',
        'port': '5432'
    }
    widget = MimicEMR(db_config)
    widget.resize(1440, 1024)
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
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
from db_connection import DBConnection
import pandas as pd

class MimicEMR(QWidget):
    def __init__(self):
        super().__init__()
        #self.dataModel = DataModel(db_config)
        self.dataModel = DataModel()
        self.fluid_summary = FluidSummary(self.dataModel)
        self.vital_summary = VitalSummary(self.dataModel)
        self.hadm_id_file = 'hadm_ids.txt'
        self.hadm_ids = self.load_hadm_ids()
        self.is_connected = False  # 연결 상태를 추적하는 변수
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Horizontal layout for HADM_ID input and enter button
        self.hadm_id_layout = QHBoxLayout()

        # DB 접속 버튼
        self.connection_button = QPushButton('DB Connect', self)
        self.connection_button.clicked.connect(self.toggle_db_connection)

        # 환자번호 입력
        self.hadm_id_input = QLineEdit(self)
        self.hadm_id_input.setPlaceholderText("Enter HADM_ID")
        # 입력을 쉽게 채울 수 있는 completer를 만든다.
        self.completer = QCompleter(self.hadm_ids, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.hadm_id_input.setCompleter(self.completer)        
        #self.show_completer = False
        #self.hadm_id_input.mousePressEvent = self.toggle_completer
        self.hadm_id_input.returnPressed.connect(self.data_load_n_populate_chart_dates)

        # 입력완료 버튼
        self.enter_button = QPushButton('Enter', self)
        self.enter_button.clicked.connect(self.data_load_n_populate_chart_dates)
        
        # 환자검색 버튼
        self.admission_finder_button = QPushButton('Admission Finder', self)
        self.admission_finder_button.clicked.connect(self.open_admission_finder)

        # Add HADM_ID input and button to the horizontal layout
        self.hadm_id_layout.addWidget(self.connection_button)
        self.hadm_id_layout.addWidget(self.hadm_id_input)
        self.hadm_id_layout.addWidget(self.enter_button)
        self.hadm_id_layout.addWidget(self.admission_finder_button)

        # Navigation buttons and ComboBox for selecting chart date
        self.chart_date_layout = QHBoxLayout()

        # Previous day button
        self.previous_day_button = QPushButton('<<', self)
        self.previous_day_button.clicked.connect(self.move_to_previous_day)
        self.previous_day_button.setEnabled(False)  # Initially disabled

        # Next day button
        self.next_day_button = QPushButton('>>', self)
        self.next_day_button.clicked.connect(self.move_to_next_day)
        self.next_day_button.setEnabled(False)  # Initially disabled

        # ComboBox for selecting chart date
        self.chart_date_selector = QComboBox(self)
        self.chart_date_selector.setEnabled(False)  # Initially disabled
        self.chart_date_selector.activated[str].connect(self.on_date_selected)  # Connect selection directly to update

        # Add navigation buttons and selector to the layout
        self.chart_date_layout.addWidget(self.previous_day_button, 1)
        self.chart_date_layout.addWidget(self.next_day_button, 1)
        self.chart_date_layout.addWidget(self.chart_date_selector, 8)

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
        self.layout.addLayout(self.chart_date_layout)
        self.layout.addWidget(self.tab_widget)

        # 초기 상태에서 비활성화
        self.set_controls_enabled(False)


    def move_to_previous_day(self):
        """Move to the previous day in the chart_date_selector."""
        current_index = self.chart_date_selector.currentIndex()
        if current_index > 0:
            self.chart_date_selector.setCurrentIndex(current_index - 1)
            self.on_date_selected(self.chart_date_selector.currentText())
        self.update_navigation_buttons()


    def move_to_next_day(self):
        """Move to the next day in the chart_date_selector."""
        current_index = self.chart_date_selector.currentIndex()
        if current_index < self.chart_date_selector.count() - 1:
            self.chart_date_selector.setCurrentIndex(current_index + 1)
            self.on_date_selected(self.chart_date_selector.currentText())
        self.update_navigation_buttons()


    def update_navigation_buttons(self):
        """Enable or disable navigation buttons based on the current index."""
        current_index = self.chart_date_selector.currentIndex()
        total_dates = self.chart_date_selector.count()
        self.previous_day_button.setEnabled(current_index > 0)
        self.next_day_button.setEnabled(current_index < total_dates - 1)


    def set_controls_enabled(self, enabled):
        """컨트롤 활성화 및 비활성화"""
        self.hadm_id_input.setEnabled(enabled)
        self.enter_button.setEnabled(enabled)
        self.admission_finder_button.setEnabled(enabled)
        self.chart_date_selector.setEnabled(enabled)
        self.tab_widget.setEnabled(enabled)


    def reset(self):
        """컨트롤 초기화"""
        self.hadm_id_input.clear()
        self.chart_date_selector.clear()
        self.chart_date_selector.setEnabled(False)
        self.general_info_sheet_widget.clear()
        self.note_sheet_widget.clear()
        self.vital_sheet_widget.clear()
        self.lab_sheet_widget.clear()
        self.order_sheet_widget.clear()
        self.emar_sheet_widget.clear()
        # 탭을 General information 탭으로 선택한다.
        self.tab_widget.setCurrentIndex(0)


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
                self.previous_day_button.setEnabled(True)
                self.next_day_button.setEnabled(True)

                # Automatically select the first date
                self.chart_date_selector.setCurrentIndex(0)
                # Manually invoke the date selection event
                self.on_date_selected(self.chart_date_selector.currentText())

                # Update navigation button states
                self.update_navigation_buttons()
            else:
                self.reset()
                self.chart_date_selector.setEnabled(False)
                self.previous_day_button.setEnabled(False)
                self.next_day_button.setEnabled(False)
        else: # 환자번호가 입력되지 않으면
            self.chart_date_selector.clear()
            self.chart_date_selector.setEnabled(False)
            self.previous_day_button.setEnabled(False)
            self.next_day_button.setEnabled(False)

    def toggle_db_connection(self):
        """DB 연결 및 연결 해제 처리"""
        if self.is_connected:
            # DB에서 연결을 해제한다.
            self.dataModel.disconnect_db()
            # Disconnect 상태로 변경
            self.is_connected = False
            self.connection_button.setText('DB Connect')
            self.set_controls_enabled(False)
            self.reset()
        else:
            # Connect 상태로 변경
            dialog = DBConnection(self, self.dataModel)
            if dialog.exec_() == QDialog.Accepted:
                self.is_connected = True
                self.connection_button.setText('DB Disconnect')
                self.set_controls_enabled(True)


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
    widget = MimicEMR()
    widget.resize(1440, 1024)
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLineEdit, QLabel, QTableView, QCheckBox, QSpinBox, QHBoxLayout, QMessageBox, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
import pandas as pd
from data_manage.data_model import DataModel

class SearchAdmission(QDialog):
    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.selected_hadm_id = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Admission Finder')

        self.layout = QVBoxLayout()
        
        self.expire_checkbox = QCheckBox('Died in Hospital')
        self.layout.addWidget(self.expire_checkbox)
        
        self.admission_days_label = QLabel('Admission Days Low Limit:')
        self.layout.addWidget(self.admission_days_label)
        
        self.admission_days_input = QSpinBox()
        self.admission_days_input.setRange(0, 365)
        self.layout.addWidget(self.admission_days_input)
        
        self.icustay_days_label = QLabel('ICU Stay Days Low Limit:')
        self.layout.addWidget(self.icustay_days_label)
        
        self.icustay_days_input = QSpinBox()
        self.icustay_days_input.setRange(0, 365)
        self.layout.addWidget(self.icustay_days_input)

        self.fetch_button = QPushButton('Fetch Admission List')
        self.fetch_button.clicked.connect(self.fetch_admission_list)
        self.layout.addWidget(self.fetch_button)
        
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.doubleClicked.connect(self.select_admission)
        self.layout.addWidget(self.table_view)
        
        self.results_count_label = QLabel('')
        self.layout.addWidget(self.results_count_label)
        
        self.setLayout(self.layout)
        
    def fetch_admission_list(self):
        condition = {
            'expire': self.expire_checkbox.isChecked(),
            'admission_days_low_limit': self.admission_days_input.value(),
            'icustay_days_low_limit': self.icustay_days_input.value()
        }
        
        admission_data = self.data_model.fetch_admission_list(condition)
        
        if not admission_data.empty:
            self.show_data(admission_data)
            self.results_count_label.setText(f'Total Admissions Viewed: {len(admission_data)}')
        else:
            self.show_error('No data found for the given conditions.')
            self.results_count_label.setText('Total Admissions Viewed: 0')
        
    def show_data(self, data):
        model = QStandardItemModel()
        
        headers = data.columns.tolist()
        model.setHorizontalHeaderLabels(headers)
        
        for index, row in data.iterrows():
            items = [QStandardItem(str(field)) for field in row]
            model.appendRow(items)
        
        self.table_view.setModel(model)
        
    def show_error(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle('Error')
        error_box.setText(message)
        error_box.exec()

    def select_admission(self, index):
        selected_row = index.row()
        model = self.table_view.model()
        self.selected_hadm_id = model.item(selected_row, 0).text()
        self.accept()  # Close the dialog

    def get_selected_hadm_id(self):
        return self.selected_hadm_id

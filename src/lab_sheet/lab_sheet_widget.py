from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QComboBox, QLabel

class LabSheetWidget(QWidget):
    def __init__(self, dataModel):
        super().__init__()
        self.dataModel = dataModel
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Category", "Label", "Chart Time", "Value", "Value Num", "Unit", "Ref Lower", "Ref Upper", "Flag"
        ])

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def update_table(self, hadm_id, chart_date):
        data = self.dataModel.fetch_lab_data(hadm_id, chart_date)
        self.table.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for column_index, value in enumerate(row_data):
                table_item = QTableWidgetItem(str(value))
                self.table.setItem(row_index, column_index, table_item)
                if column_index == 4:  # Check valuenum column for color coding
                    if row_data[8] == 'high' and row_data[4] is not None and row_data[4] > row_data[7]:
                        table_item.setBackground(QtGui.QColor(255, 0, 0))
                    elif row_data[8] == 'low' and row_data[4] is not None and row_data[4] < row_data[6]:
                        table_item.setBackground(QtGui.QColor(0, 0, 255))

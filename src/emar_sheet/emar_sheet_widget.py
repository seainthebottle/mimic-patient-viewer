from PySide6 import QtGui
from PySide6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout

class EMARSheetWidget(QWidget):
    def __init__(self, dataModel):
        super().__init__()
        self.dataModel = dataModel
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setColumnCount(17)
        self.table.setHorizontalHeaderLabels([
            "Subject ID", "HADM ID", "EMAR ID", "EMAR Seq", "POE ID", "Pharmacy ID", 
            "Chart Time", "Medication", "Event Text", 
            "Schedule Time", "Store Time", "Administration Type", "Dose Due", 
            "Dose Due Unit", "Dose Given", "Dose Given Unit", "Route"
        ])

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def update_table(self, hadm_id, chart_date):
        data = self.dataModel.fetch_emar_data(hadm_id, chart_date)
        self.table.setRowCount(0)  # Reset the table
        self.table.setRowCount(len(data))
        for row_index, row_data in data.iterrows():
            for column_index, value in enumerate(row_data):
                table_item = QTableWidgetItem(str(value))
                self.table.setItem(row_index, column_index, table_item)
        
        # 컬럼 사이즈를 조절한다.
        self.table.resizeColumnsToContents()
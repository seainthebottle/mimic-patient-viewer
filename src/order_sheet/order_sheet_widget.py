import sys
import pandas as pd
import psycopg2
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout

class OrderSheetWidget(QWidget):
    def __init__(self, dataModel):
        super().__init__()
        self.dataModel = dataModel
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        self.layout.addWidget(self.table)
        self.table.setColumnCount(7)  # Adjust the number of columns based on what you want to show
        self.table.setHorizontalHeaderLabels([
            'Order ID', 'Order Seq', 'Order Time', 'Order Type', 'Order Subtype', 'Order Status', 'Details'])

    def clear(self):
        self.table.clear()

    def update_table(self, hadm_id, chart_date):
        data = self.dataModel.fetch_order_data(hadm_id, chart_date)
        self.table.reset()
        self.table.setRowCount(len(data))
        for i, row in enumerate(data.itertuples()):
            if(str(row[4]) == 'Medications'): 
                for j in range(4):  # row contains index at the first position
                    self.table.setItem(i, j, QTableWidgetItem(str(row[j+1])))
                self.table.setItem(i, 4, QTableWidgetItem(str(row[8])))
                self.table.setItem(i, 5, QTableWidgetItem(str(row[9])))
                self.table.setItem(i, 6, QTableWidgetItem(str(row[10])))
            # 약물 오더가 아닌 경우
            else:
                for j in range(7):  # row contains index at the first position
                    self.table.setItem(i, j, QTableWidgetItem(str(row[j+1])))

        # 컬럼 사이즈를 조절한다.
        self.table.resizeColumnsToContents()

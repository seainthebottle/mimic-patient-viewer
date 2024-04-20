import sys
import psycopg2
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QLineEdit, QPushButton, QComboBox, QLabel

class LabSummary:
    def __init__(self, config):
        self.config = config

    def connect_db(self):
        try:
            self.connection = psycopg2.connect(**self.config)
            self.cursor = self.connection.cursor()
            print("Database connection successful")
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def fetch_lab_data(self, hadm_id, chart_date):
        self.connect_db()
        query = f"""
        SELECT d.category, d.label, l.charttime, l.value, l.valuenum, l.valueuom, l.ref_range_lower, l.ref_range_upper, l.flag
        FROM mimiciv_hosp.labevents AS l
        JOIN mimiciv_hosp.d_labitems AS d ON l.itemid = d.itemid
        WHERE l.hadm_id = %s AND DATE(l.charttime) = %s
        ORDER BY l.charttime DESC, d.category;
        """
        try:
            self.cursor.execute(query, (hadm_id, chart_date))
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching lab data: {e}")
            return []

    def get_available_dates(self, hadm_id):
        self.connect_db()
        query = f"""
        SELECT DISTINCT DATE(charttime)
        FROM mimiciv_hosp.labevents
        WHERE hadm_id = %s
        ORDER BY DATE(charttime);
        """
        try:
            self.cursor.execute(query, (hadm_id,))
            dates = self.cursor.fetchall()
            return [date[0] for date in dates]
        except Exception as e:
            print(f"Error fetching available dates: {e}")
            return []

class LabDisplayWidget(QWidget):
    def __init__(self, lab_summary):
        super().__init__()
        self.lab_summary = lab_summary
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.hadm_id_input = QLineEdit(self)
        self.hadm_id_input.setPlaceholderText("Enter HADM_ID")
        self.enter_button = QPushButton('Enter', self)
        self.enter_button.clicked.connect(self.update_date_selector)

        self.date_label = QLabel("Select Chart Date:")
        self.chart_date_selector = QComboBox(self)
        self.chart_date_selector.setEnabled(False)

        self.search_button = QPushButton('Search', self)
        self.search_button.clicked.connect(self.update_table)
        self.search_button.setEnabled(False)

        self.table = QTableWidget(self)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Category", "Label", "Chart Time", "Value", "Value Num", "Unit", "Ref Lower", "Ref Upper", "Flag"
        ])

        self.layout.addWidget(self.hadm_id_input)
        self.layout.addWidget(self.enter_button)
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.chart_date_selector)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def update_date_selector(self):
        hadm_id = self.hadm_id_input.text().strip()
        if hadm_id.isdigit():
            dates = self.lab_summary.get_available_dates(hadm_id)
            self.chart_date_selector.clear()
            if dates:
                self.chart_date_selector.addItems([date.strftime("%Y-%m-%d") for date in dates])
                self.chart_date_selector.setEnabled(True)
                self.search_button.setEnabled(True)
            else:
                self.chart_date_selector.setEnabled(False)
                self.search_button.setEnabled(False)
        else:
            self.chart_date_selector.clear()
            self.chart_date_selector.setEnabled(False)
            self.search_button.setEnabled(False)

    def update_table(self):
        hadm_id = self.hadm_id_input.text()
        chart_date = self.chart_date_selector.currentText()
        data = self.lab_summary.fetch_lab_data(hadm_id, chart_date)
        self.table.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for column_index, value in enumerate(row_data):
                table_item = QTableWidgetItem(str(value))
                self.table.setItem(row_index, column_index, table_item)
                if column_index == 4:  # Check valuenum column for color coding
                    if row_data[8] == 'high' and row_data[4] is not None and row_data[4] > row_data[7]:  # Check upper reference
                        table_item.setBackground(QtGui.QColor(255, 0, 0))
                    elif row_data[8] == 'low' and row_data[4] is not None and row_data[4] < row_data[6]:  # Check lower reference
                        table_item.setBackground(QtGui.QColor(0, 0, 255))

class LabSheetWidget:
    def __init__(self):
        self.app = QApplication(sys.argv)
        db_config = {
            'dbname': 'mimiciv',
            'user': 'postgres',
            'password': 'Mokpswd7!',
            'host': 'localhost',
            'port': '5432'
        }
        self.lab_summary = LabSummary(db_config)
        self.display_widget = LabDisplayWidget(self.lab_summary)
        self.display_widget.resize(1440, 800)
        self.display_widget.show()
        sys.exit(self.app.exec_())

# To run the program, create an instance of LabSheetWidget:
if __name__ == "__main__":
    lab_sheet_widget = LabSheetWidget()

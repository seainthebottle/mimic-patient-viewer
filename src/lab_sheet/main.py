import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox
from lab_summary import LabSummary
from lab_sheet_widget import LabSheetWidget

class LabDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.lab_summary = LabSummary({
            'dbname': 'mimiciv',
            'user': 'postgres',
            'password': 'Mokpswd7!',
            'host': 'localhost',
            'port': '5432'
        })
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Horizontal layout for HADM_ID input and enter button
        self.hadm_id_layout = QHBoxLayout()
        self.hadm_id_input = QLineEdit(self)
        self.hadm_id_input.setPlaceholderText("Enter HADM_ID")
        self.enter_button = QPushButton('Enter', self)
        self.enter_button.clicked.connect(self.populate_chart_dates)

        # Add HADM_ID input and button to the horizontal layout
        self.hadm_id_layout.addWidget(self.hadm_id_input)
        self.hadm_id_layout.addWidget(self.enter_button)

        # ComboBox for selecting chart date
        self.chart_date_selector = QComboBox(self)
        self.chart_date_selector.setEnabled(False)  # Initially disabled
        self.chart_date_selector.activated[str].connect(self.on_date_selected)  # Connect selection directly to update

        self.sheet_widget = LabSheetWidget(self.lab_summary)

        # Add widgets to the main vertical layout
        self.layout.addLayout(self.hadm_id_layout)
        self.layout.addWidget(self.chart_date_selector)
        self.layout.addWidget(self.sheet_widget)

    def populate_chart_dates(self):
        hadm_id = self.hadm_id_input.text().strip()
        if hadm_id:
            dates = self.lab_summary.get_available_dates(hadm_id)
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
        hadm_id = self.hadm_id_input.text().strip()
        chart_date = date.strip()
        if hadm_id and chart_date:
            self.sheet_widget.update_table(hadm_id, chart_date)

def main():
    app = QApplication(sys.argv)
    widget = LabDisplayWidget()
    widget.resize(1440, 800)
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from PyQt5 import QtWidgets, QtCore

from vital_sheet.vital_sheet_widget import VitalSheetWidget

# Mock data setup
# 더미 데이터 설정: 2023년 4월 14일부터 하루 동안의 시간대별 데이터를 생성
date_range = pd.date_range("2024-04-14 00:00", "2024-04-16 00:00", freq="1h")
np.random.seed(0)
data = {
    "timestamp": date_range,
    "heart_rate": np.random.randint(60, 100, size=len(date_range)),
    "body_temp": np.random.uniform(35.5, 38.5, size=len(date_range)),
    "sbp": np.random.randint(110, 130, size=len(date_range)),
    "dbp": np.random.randint(70, 90, size=len(date_range)),
    "input_ml": np.random.randint(100, 500, size=len(date_range)),
    "output_ml": np.random.randint(100, 500, size=len(date_range))
}
df = pd.DataFrame(data)
#df = pd.concat(pd.DataFrame(["2024-14-15 18:35", 130, 36.5, 100, 70, 0,  0], columns=df.columns), ignore_index = True)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.widget = VitalSheetWidget(self, df)
        self.setCentralWidget(self.widget)
        self.date_edit = QtWidgets.QDateEdit(calendarPopup=True)
        self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.date_edit.dateTimeChanged.connect(self.update_plot)
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addWidget(self.date_edit)
        self.show()
        self.initial_plot()

    def initial_plot(self):
        self.update_plot()

    def update_plot(self):
        date = self.date_edit.date().toString('yyyy-MM-dd')
        self.widget.plotVitals(date)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())

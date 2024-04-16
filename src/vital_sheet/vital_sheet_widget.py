import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from PyQt5 import QtWidgets

class VitalSheetWidget(QtWidgets.QWidget):
    def __init__(self, parent = None, mainData = None):
        """  
        클래스를 초기화한다.
        self.dataFrame      주요 데이터를 담는 DataFrame
        self.current_date   데이터를 표시할 날짜
        """
        super(VitalSheetWidget, self).__init__(parent)
        
        if not mainData: self.dataFrame = None
        else: self.dataFrame = pd.DataFrame(mainData)

        self.figure = Figure()  # Create the matplotlib figure
        self.canvas = FigureCanvas(self.figure)  # Create a canvas for the figure
        self.layout = QtWidgets.QVBoxLayout(self)  # Set up a vertical layout
        self.layout.addWidget(self.canvas)  # Add the canvas to the layout

        self.ax1 = self.figure.add_subplot(211)  # First graph axis for blood pressure
        self.ax2 = self.figure.add_subplot(212)  # Second graph axis for heart rate
        self.ax3 = self.ax2.twinx()  # Additional axis for body temperature on the right side

        self.current_date = None  # Store the current date for replotting

    def setData(self, mainData):
        if not mainData: self.dataFrame = None
        else: self.dataFrame = pd.DataFrame(mainData)

    def plotVitals(self, date):
        self.current_date = date
        self.drawPlot()

    def drawPlot(self):
        if self.current_date:
            date = self.current_date
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()  # Also clear the third axis

            mask = (self.dataFrame['timestamp'].dt.date == pd.to_datetime(date).date()) | (self.dataFrame['timestamp'] == pd.to_datetime(date).date() + pd.Timedelta(days=1))
            daily_data = self.dataFrame[mask]

            if not daily_data.empty:
                # Plot blood pressure
                self.ax1.plot(daily_data['timestamp'], daily_data['sbp'], label='SBP', marker='o', linestyle='--', color='red')
                self.ax1.plot(daily_data['timestamp'], daily_data['dbp'], label='DBP', marker='o', linestyle='--', color='blue')
                self.ax1.fill_between(daily_data['timestamp'], daily_data['dbp'], daily_data['sbp'], color='grey', alpha=0.3, label='Pressure Gap')
                self.ax1.set_title('Blood Pressure')
                self.ax1.legend(loc='upper right')
                self.ax1.grid(True)

                # Plot heart rate
                self.ax2.plot(daily_data['timestamp'], daily_data['heart_rate'], label='Heart Rate', marker='o', linestyle='-', color='green')
                self.ax2.set_title('Heart Rate and Body Temperature')
                #self.ax2.legend(loc='upper right')
                self.ax2.grid(True)
                # Set the lower limit of heart rate to 0 and determine a suitable upper limit
                max_heart_rate = daily_data['heart_rate'].max() + 10  # Adding a buffer for better visibility
                self.ax2.set_ylim(0, max_heart_rate)

                # Plot body temperature on a separate axis
                self.ax3.plot(daily_data['timestamp'], daily_data['body_temp'], label='Body Temperature', marker='o', linestyle='-', color='orange')
                #self.ax3.legend(loc='upper right')
                self.ax3.tick_params(axis='y', labelcolor='orange')
                self.ax3.set_ylim(30, 50)  # Set the limits for body temperature

                # Collect legend handles and labels from both ax2 and ax3
                handles, labels = [], []
                for ax in [self.ax2, self.ax3]:
                    for handle, label in zip(*ax.get_legend_handles_labels()):
                        handles.append(handle)
                        labels.append(label)

                # Place a single combined legend on ax2
                self.ax2.legend(handles, labels, loc='upper right')
                self.ax2.set_title('Heart Rate and Body Temperature')
                self.ax2.grid(True)

                # Set axis parameters
                for ax in [self.ax1, self.ax2, self.ax3]:
                    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
                    ax.set_xlim([pd.to_datetime(date), pd.to_datetime(date) + pd.Timedelta(days=1)])

                # Add table below the second graph
                table_data = daily_data[['timestamp', 'input_ml', 'output_ml']].copy()
                table_data['timestamp'] = table_data['timestamp'].dt.strftime('%H:%M')
                transposed_data = table_data.T
                cell_text = transposed_data.values.tolist()
                self.ax2.table(cellText=cell_text, rowLabels=transposed_data.index, loc='bottom', bbox=[0, -0.4, 1, 0.2])

            self.figure.subplots_adjust(left=0.1, right=0.95, bottom=0.2, top=0.95)
            self.canvas.draw()

    def resizeEvent(self, event):
        self.drawPlot()  # Redraw the plot to adjust to new size
        super(VitalSheetWidget, self).resizeEvent(event)
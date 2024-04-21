import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from PyQt5 import QtWidgets

class VitalSheetWidget(QtWidgets.QWidget):
    def __init__(self, mainData = None):
        """  
        클래스를 초기화한다.

        Argument:
        - mainData          주요 데이터 (DataFrame)

        Class Variables:
        - self.dataFrame    주요 데이터를 담는 DataFrame
        - self.current_date 데이터를 표시할 날짜
        """
        super(VitalSheetWidget, self).__init__()
        
        if mainData is None or mainData.empty:
            self.dataFrame = None
        else:
            self.dataFrame = mainData

        self.figure = Figure()  # Create the matplotlib figure
        self.canvas = FigureCanvas(self.figure)  # Create a canvas for the figure
        self.layout = QtWidgets.QVBoxLayout(self)  # Set up a vertical layout
        self.layout.addWidget(self.canvas)  # Add the canvas to the layout

        self.ax1 = self.figure.add_subplot(211)  # First graph axis for blood pressure
        self.ax2 = self.figure.add_subplot(212)  # Second graph axis for heart rate
        self.ax3 = self.ax2.twinx()  # Additional axis for body temperature on the right side

        self.current_date = None  # Store the current date for replotting

    def setData(self, mainData):
        if mainData is None or mainData.empty:
            self.dataFrame = None
        else:
            self.dataFrame = mainData

    def drawPlotSetDate(self, date):
        self.current_date = date
        self.drawPlot()

    def drawPlot(self):
        if self.current_date and not self.dataFrame.empty:
            date = pd.to_datetime(self.current_date)
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()  # Also clear the third axis

            # 하루 동안의 모든 시간을 포함하는 Timestamp 생성
            full_day_range = pd.date_range(start=pd.to_datetime(self.current_date), end=pd.to_datetime(self.current_date) + pd.Timedelta(days=1), freq='h')
            #full_day_range = pd.date_range(start=pd.to_datetime(self.current_date), end=pd.to_datetime(self.current_date) + pd.Timedelta(hours=25), freq='h')
            #full_day_range = full_day_range[:-1]  # Exclude the last hour if mimicking 'closed='left''

            mask = (self.dataFrame['timestamp'].dt.date == date.date()) | (self.dataFrame['timestamp'] == date + pd.Timedelta(days=1))
            daily_data = self.dataFrame[mask]
            daily_data = daily_data.fillna(0)  # 누락된 데이터는 0으로 채움
            #daily_data['input_ml'] = daily_data['input_ml'].fillna(0).round(0).astype(int)
            #daily_data['output_ml'] = daily_data['output_ml'].fillna(0).round(0).astype(int)

            # 전체 시간대로 인덱싱
            daily_data.set_index('timestamp', inplace=True)
            daily_data = daily_data.reindex(full_day_range)
            daily_data.reset_index(inplace=True)
            daily_data.rename(columns={'index': 'timestamp'}, inplace=True)

            if not daily_data.empty:
                sbp_data = daily_data[daily_data['NBPs'] != 0]
                dbp_data = daily_data[daily_data['NBPd'] != 0]
                gbp_data = daily_data[(daily_data['NBPs'] != 0) & (daily_data['NBPd'] != 0)]
                hr_data = daily_data[daily_data['HR'] != 0]
                bt_data = daily_data[daily_data['BT'] != 0]

                # Plot blood pressure

                #print(sbp_data, dbp_data)
                self.ax1.plot(sbp_data['timestamp'], sbp_data['NBPs'], label='SBP', marker='o', linestyle='--', color='red')
                self.ax1.plot(dbp_data['timestamp'], dbp_data['NBPd'], label='DBP', marker='o', linestyle='--', color='blue')
                self.ax1.fill_between(gbp_data['timestamp'], gbp_data['NBPd'], gbp_data['NBPs'], color='grey', alpha=0.3, label='Pressure Gap')
                self.ax1.set_title('Blood Pressure')
                self.ax1.legend(loc='upper right')
                #max_sbp = sbp_data['NBPs'].max()  
                #min_dbp = dbp_data['NBPd'].min() 
                #print(sbp_data, dbp_data)
                #if max_sbp and min_dbp: self.ax1.set_ylim(min_dbp, max_sbp)
                self.ax1.grid(True)

                # Plot heart rate
                self.ax2.plot(hr_data['timestamp'], hr_data['HR'].replace(0, None), label='Heart Rate', marker='o', linestyle='-', color='green',)
                self.ax2.set_title('Heart Rate and Body Temperature')
                #self.ax2.legend(loc='upper right')
                self.ax2.grid(True)
                # Set the lower limit of heart rate to 0 and determine a suitable upper limit
                max_heart_rate = hr_data['HR'].max() + 50  # Adding a buffer for better visibility
                if not pd.isna(max_heart_rate): self.ax2.set_ylim(30, max_heart_rate)

                # Plot body temperature on a separate axis
                self.ax3.plot(bt_data['timestamp'], bt_data['BT'].replace(0, None), label='Body Temperature', marker='o', linestyle='-', color='orange')
                #self.ax3.legend(loc='upper right')
                self.ax3.tick_params(axis='y', labelcolor='orange')
                self.ax3.set_ylim(33, 45)  # Set the limits for body temperature

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

            if not daily_data.empty:
                # Add table below the second graph
                table_data = daily_data[['timestamp', 'input_ml', 'output_ml']].copy()
                table_data = table_data[:-1]
                table_data['timestamp'] = table_data['timestamp'].dt.strftime('%H:%M')
                table_data['input_ml'] = table_data['input_ml'].apply(lambda x: '' if pd.isna(x) else int(x))
                table_data['output_ml'] = table_data['output_ml'].apply(lambda x: '' if pd.isna(x) else int(x))
                transposed_data = table_data.T
                cell_text = transposed_data.values.tolist()
                table = self.ax2.table(cellText=cell_text, rowLabels=transposed_data.index, loc='bottom', bbox=[0, -0.45, 1, 0.3], fontsize=9)
                table.auto_set_font_size(False)

            self.figure.subplots_adjust(left=0.1, right=0.95, bottom=0.2, top=0.95)
            self.canvas.draw()

    def resizeEvent(self, event):
        self.drawPlot()  # Redraw the plot to adjust to new size
        super(VitalSheetWidget, self).resizeEvent(event)
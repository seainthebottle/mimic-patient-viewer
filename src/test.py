import matplotlib.pyplot as plt
import ipywidgets as widgets
import pandas as pd
import numpy as np
from IPython.display import display
import matplotlib.dates as mdates

# Mock data setup
date_range = pd.date_range("2023-04-14 00:00", "2023-04-15 00:00", freq="1H")  # Extends to the start of the next day
np.random.seed(0)
data = {
    "timestamp": date_range,
    "heart_rate": np.random.randint(60, 100, size=len(date_range)),
    "body_temp": np.random.uniform(36.5, 37.5, size=len(date_range)),
    "sbp": np.random.randint(110, 130, size=len(date_range)),
    "dbp": np.random.randint(70, 90, size=len(date_range)),
    "input_ml": np.random.randint(100, 500, size=len(date_range)),
    "output_ml": np.random.randint(100, 500, size=len(date_range))
}

df = pd.DataFrame(data)

def plot_vitals(date):
    # Filter data for the selected date and include the very start of the next day
    mask = (df['timestamp'].dt.date == pd.to_datetime(date).date()) | (df['timestamp'] == pd.to_datetime(date).date() + pd.Timedelta(days=1))
    daily_data = df[mask]
    
    # Create a figure with subplots
    fig, ax = plt.subplots(figsize=(15, 8))  # Adjusted height slightly larger
    
    # Plotting the vital signs
    ax.plot(daily_data['timestamp'], daily_data['heart_rate'], label='Heart Rate', marker='o', linestyle='-')
    ax.plot(daily_data['timestamp'], daily_data['body_temp'], label='Body Temperature', marker='o', linestyle='-')
    ax.plot(daily_data['timestamp'], daily_data['sbp'], label='SBP', marker='o', linestyle='-')
    ax.plot(daily_data['timestamp'], daily_data['dbp'], label='DBP', marker='o', linestyle='-')
    ax.legend()
    ax.set_title('Vital Signs by Hour')
    ax.grid(True)

    # Set x-axis date format
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # set major ticks every hour
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # format x-axis labels as hour:minute

    # Set x-axis limits to explicitly cover the whole day
    start_of_day = pd.to_datetime(date)
    end_of_day = start_of_day + pd.Timedelta(days=1)
    ax.set_xlim([start_of_day, end_of_day])

    # Format data for table correctly
    table_data = daily_data[['timestamp', 'input_ml', 'output_ml']].copy()
    table_data['timestamp'] = table_data['timestamp'].dt.strftime('%H:%M')
    
    # Transpose the DataFrame for the table
    transposed_data = table_data.T
    cell_text = transposed_data.values.tolist()

    # Create table below the axis
    table = ax.table(cellText=cell_text, rowLabels=transposed_data.index, loc='bottom', bbox=[0, -0.3, 1, 0.2])
    plt.subplots_adjust(left=0.1, right=0.95, bottom=0.25, top=0.95)  # Increase bottom margin for better fit

    plt.show()

# Create a date picker widget
date_picker = widgets.DatePicker(
    description='Pick a Date',
    value=pd.to_datetime('2023-04-14'),  # default value
    disabled=False
)

# Create a function to handle date changes
def on_date_change(change):
    plot_vitals(change.new)

date_picker.observe(on_date_change, names='value')

# Display the widget
display(date_picker)
plot_vitals(date_picker.value)  # initial plot

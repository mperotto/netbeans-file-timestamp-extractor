import pandas as pd
from datetime import datetime, timedelta
import sys
import pdb

# Define a function to calculate the duration between timestamps
def calculate_duration(start_time, end_time):
    if start_time.date() == end_time.date() and start_time <= end_time:
        duration = end_time - start_time
        return duration.total_seconds()
    else:
        return 0


def format_duration(duration):
    if isinstance(duration, str):
        return duration
    seconds = duration.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# Read the input file name from command line arguments
input_file = sys.argv[1]

# Set the output file name based on the input file name
output_file = input_file.split(".")[0] + ".xlsx"

# Read the file and parse the timestamps
df = pd.read_csv(input_file, sep=',', names=['file', 'timestamp'], parse_dates=['timestamp'], skiprows=1)
df['date'] = df['timestamp'].dt.date

df = df.sort_values(by=['timestamp', 'file'])
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%H:%M:%S')

df['previous_timestamp'] = df.groupby('file')['timestamp'].shift(1).fillna(df['timestamp'] - pd.Timedelta(minutes=1))
df['duration'] = pd.Timedelta(minutes=0)
df['duration'] = df['duration'].fillna(pd.Timedelta(minutes=1))
df['duration'] = df['timestamp'] - df['previous_timestamp']

df['duration'] = df['duration'].fillna(0)

df = df.dropna()

# Calculate the duration for each task and handle events on different days and files
prev_row = None
for index, row in df.iterrows():
    if prev_row is not None and row['file'] == prev_row['file']:
        duration = calculate_duration(prev_row['timestamp'], row['timestamp'])
        if pd.Timedelta(seconds=duration) < pd.Timedelta(minutes=15):
            df.at[index, 'duration'] = duration
        else:
            df.at[index, 'duration'] = pd.Timedelta(minutes=15)
    else:
        if prev_row is not None and prev_row['file'] != row['file']:
            df.at[prev_row.name, 'duration'] = pd.Timedelta(minutes=1)
        df.at[index, 'duration'] = pd.Timedelta(minutes=0)
    prev_row = row

# Adjust to last record if have more than one occurrence for the same date
if prev_row is not None and df[df['file'] == prev_row['file']].shape[0] == 1:
    df.at[prev_row.name, 'duration'] = pd.Timedelta(minutes=1)


# Convert the duration to a timedelta object and sum it by day of week and file path
df['duration'] = pd.to_timedelta(df['duration'], unit='s')
grouped_df = df.groupby(['date', 'file'])['duration'].sum().reset_index()
grouped_df['duration'] = grouped_df['duration'].apply(format_duration).astype(str)


# Add a column for day of week and sort the rows by date and file path
grouped_df['day_of_week'] = pd.to_datetime(grouped_df['date']).dt.day_name()
grouped_df = grouped_df[['date', 'file', 'day_of_week', 'duration']]
grouped_df['duration'] = grouped_df['duration'].apply(format_duration)
grouped_df = grouped_df.sort_values(by=['date', 'file'])

# Write the output to an Excel file
output_df = grouped_df[['date', 'file', 'day_of_week', 'duration']]
output_df.to_excel(output_file, index=False)

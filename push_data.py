import os
import pandas as pd
from sqlalchemy import create_engine

# Define your PostgreSQL connection string
connection_string = "postgresql://DhairyaPatel1403:BY3CpiV1dUgD@ep-blue-pine-a4nxdtlt.us-east-1.aws.neon.tech/tradedata?sslmode=require"

# Function to push data from CSV to PostgreSQL
def push_csv_data_to_postgres(csv_file_path, connection_string):
    # Read CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Extract filename without extension as 'Name'
    file_name = os.path.basename(csv_file_path)
    name = os.path.splitext(file_name)[0]
    df['Name'] = name  # Add 'Name' column

    # Create a connection engine
    engine = create_engine(connection_string)

    # Append data to PostgreSQL table
    df.to_sql('stocks', engine, if_exists='append', index=False)

# Path to the directory containing CSV files
data_folder_path = 'data'

# Iterate through each file in the data folder
for file_name in os.listdir(data_folder_path):
    if file_name.endswith('.csv'):
        csv_file_path = os.path.join(data_folder_path, file_name)
        push_csv_data_to_postgres(csv_file_path, connection_string)

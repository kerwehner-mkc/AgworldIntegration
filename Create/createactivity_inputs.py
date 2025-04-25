# Bring in dependencies
import json
import pyodbc
import os
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, ParseResult
from dateutil import parser
from dotenv import load_dotenv
from datetime import datetime
import psutil


# Set up tracking memory
process = psutil.Process(os.getpid())


# Load the .env file
load_dotenv()


# Access environment variables
server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')


# Build the connection string
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
)


# Check if connected to server
print(f"Trying to connect to: {server}")


# Connect to SQL Server
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


# Check connection to database
cursor.execute("SELECT DB_NAME() AS CurrentDatabase")
row = cursor.fetchone()
print(f"✅ Connected to database: {row.CurrentDatabase}")


# Define activity_input table structure

table_definitions = {
    "activity_inputs": """
	IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='activity_inputs' AND xtype='U')
	CREATE TABLE activity_inputs (
		id INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
		activity_id BIGINT NULL,
		activity_input_order INT NULL,
		cost_per_area NVARCHAR(MAX) NULL,
		grazing_interval NVARCHAR(MAX) NULL,
		harvest_interval NVARCHAR(MAX) NULL,
		input_name NVARCHAR(MAX) NULL,
		input_type NVARCHAR(100) NULL,
		cost_activity_id BIGINT NULL,
		crop_variety_id BIGINT NULL,
		product_id BIGINT NULL,
		national_registration_number NVARCHAR(MAX) NULL,
		mix_method NVARCHAR(100) NULL,
		plantback_interval NVARCHAR(MAX) NULL,
		product_categories NVARCHAR(MAX) NULL,  -- store JSON
		product_substance NVARCHAR(MAX) NULL,
		rain_fast_interval NVARCHAR(MAX) NULL,
		rate NVARCHAR(MAX) NULL,
		re_entry_interval NVARCHAR(MAX) NULL,
		stockfeed_inverval NVARCHAR(MAX) NULL,
		tags NVARCHAR(MAX) NULL,  -- store JSON
		total_area NVARCHAR(MAX) NULL,
		total_cost NVARCHAR(MAX) NULL,
		total_count NVARCHAR(MAX) NULL,
		total_time NVARCHAR(MAX) NULL,
		total_volume NVARCHAR(MAX) NULL,
		total_weight NVARCHAR(MAX) NULL,
		unit_cost NVARCHAR(MAX) NULL,
		FOREIGN KEY (activity_id) REFERENCES activities(id)
    );
    """
 }


# Execute table creation and commit
for ddl in table_definitions.values():
    cursor.execute(ddl)
conn.commit()


# Close connection
conn.close()



# Close connection
conn.close()
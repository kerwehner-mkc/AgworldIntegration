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


# Define activity_fields table structure

table_definitions = {
    "activity_fields": """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='activity_fields' AND xtype='U')
        CREATE TABLE activity_fields (
			id int IDENTITY(1,1) PRIMARY KEY NOT NULL,
			activity_id BIGINT,
			area nvarchar(max) NULL,
			area_ratio float NULL,
			chemical_cost nvarchar(max) NULL,
			crops nvarchar(max) NULL,
			crop_stage nvarchar(max) NULL,
			farm_id bigint NULL,
			farm_name nvarchar(max) NULL,
			fertilizer_cost nvarchar(max) NULL,
            field_id int,
            field_name nvarchar(max) NULL,
            operation_cost nvarchar(max) NULL,
			seed_cost nvarchar(max) NULL,
			season_id bigint NULL,
			season_phase nvarchar(max) NULL,
			total_cost nvarchar(max) NULL,
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
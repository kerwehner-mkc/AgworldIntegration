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


# Define activity_problems table structure

table_definitions = {
    "activity_problems": """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='activity_problems' AND xtype='U')
        CREATE TABLE activity_problems (
			id int IDENTITY(1,1) PRIMARY KEY NOT NULL,
			activity_id BIGINT,
			description nvarchar(max) NULL,
			infestation nvarchar(max) NULL,
			pest_name nvarchar(max) NULL,
			severity nvarchar(max) NULL,
			stage nvarchar(max) NULL
    );
    """
 }


# Execute table creation and commit
for ddl in table_definitions.values():
    cursor.execute(ddl)
conn.commit()


# Close connection
conn.close()
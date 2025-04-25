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


# Define operator_licenses table structure

table_definitions = {
    "operator_company_licenses": """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='operator_company_licenses' AND xtype='U')
        CREATE TABLE operator_company_licenses (
			id int IDENTITY(1,1) NOT NULL,
            activity_id bigint NOT NULL,
			name nvarchar(max) NULL,
			description nvarchar(max) NULL,
			authority nvarchar(max) NULL,
			number nvarchar(max) NULL,
			valid_from datetimeoffset(7) NULL,
			valid_to datetimeoffset(7) NULL,
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
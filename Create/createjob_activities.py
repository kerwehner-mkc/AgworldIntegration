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


# Define job_activities table structure

table_definitions = {
    "job_activities": """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='job_activities' AND xtype='U')
        CREATE TABLE job_activities (
            id INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
            activity_id BIGINT, -- the "parent" activity_id from the root object
            job_activity_id BIGINT, -- the activity_id inside job_activities list
            activity_type NVARCHAR(100),
            author_user_name NVARCHAR(255),
            author_user_id INT,
            author_company_name NVARCHAR(255),
            author_company_id INT,
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

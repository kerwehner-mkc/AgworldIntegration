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


# Define activities table structure

table_definitions = {
    "activities": """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='activities' AND xtype='U')
        CREATE TABLE activities (
			id bigint PRIMARY KEY NOT NULL,
			type nvarchar(max) NULL,
			activity_category nvarchar(max) NULL,
			application_method nvarchar(max) NULL,
			approved nvarchar(max) NULL,
			area nvarchar(max) NULL,
			author_company_id bigint NULL,
			author_company_name nvarchar(max) NULL,
			author_user_id bigint NULL,
			author_user_name nvarchar(max) NULL,
			band nvarchar(max) NULL,
			chemical_cost nvarchar(max) NULL,
			comments nvarchar(max) NULL,
			company_id bigint NULL,
			company_name nvarchar(max) NULL,
			completed bit NULL,
			completed_at datetimeoffset(7) NULL,
			cost_per_area nvarchar(max) NULL,
			created_at datetimeoffset(7) NULL,
			created_on nvarchar(max) NULL,
			droplet_size nvarchar(max) NULL,
			due_at datetimeoffset(7) NULL,
			expiration_date datetimeoffset(7) NULL,
			farm_assets nvarchar(max) NULL,
			fertilizer_cost nvarchar(max) NULL,
			humidity nvarchar(max) NULL,
			nozzle_type nvarchar(max) NULL,
			operator_company_id bigint NULL,
			operator_company_name nvarchar(max) NULL,
			operator_company_licenses nvarchar(max) NULL,
			operation_cost nvarchar(max) NULL,
			operator_users nvarchar(max) NULL,
			parent_id bigint NULL,
			reason_name nvarchar(max) NULL,
			reason_text nvarchar(max) NULL,
			season_phase nvarchar(max) NULL,
			seed_cost nvarchar(max) NULL,
			skip_row nvarchar(max) NULL,
			specialisation nvarchar(max) NULL,
			started_at datetimeoffset(7) NULL,
			tags nvarchar(max) NULL,
			temperature nvarchar(max) NULL,
			timing nvarchar(max) NULL,
			total_cost nvarchar(max) NULL,
			total_volume nvarchar(max) NULL,
			activity_type nvarchar(max) NULL,
			updated_at datetimeoffset(7) NULL,
			water_rate nvarchar(max) NULL,
			weather_conditions nvarchar(max) NULL,
			wind_direction nvarchar(max) NULL,
			wind_speed nvarchar(max) NULL,
			activity_inputs nvarchar(max) NULL,
			activity_fields nvarchar(max) NULL,
			activity_problems nvarchar(max) NULL,
			job_activities nvarchar(max) NULL,
			job_id bigint NULL,
			job_status nvarchar(max) NULL,
			colour_id bigint NULL,
			colour_name nvarchar(max) NULL,
			activity_status nvarchar(max) NULL,
    );
    """
 }


# Execute table creation and commit
for ddl in table_definitions.values():
    cursor.execute(ddl)
conn.commit()


# Close connection
conn.close()

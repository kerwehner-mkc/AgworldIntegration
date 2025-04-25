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
api_base_url = os.getenv('API_BASE_URL')
api_token = os.getenv('API_TOKEN')


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


# Start with the first request
url = api_base_url
headers = {
    'Content-Type': 'application/vnd.api+json',
    'Accept': 'application/vnd.api+json',
    'api_token': api_token
}
params = {
    'api_token': api_token,
    'page[number]': 100,
    'page[size]': 100,
    'sort': '-updated_at'
}


# Set a limit on how many pages to fetch for testing
page_limit = 20
pages_fetched = 0


# Loop through paginated results as long as there's a next URL and we're within the page limit
while url and pages_fetched < page_limit:
    # Ensure the API token is included in the paginated URL
    if 'api_token' not in url:
        if '?' in url:
            url += f"&api_token={api_token}"
        else:
            url += f"?api_token={api_token}"
    # Make the request for the current page
    response = requests.get(url, headers=headers)
    # Raise an error if unauthorized (likely due to missing or incorrect token)
    if response.status_code == 401:
        raise Exception("Unauthorized — check if token is missing on paginated request.")
    # Parse the response JSON
    data = response.json()
    print(f"📄 Processing page {pages_fetched + 1}")
    # Loop through each activity record in the current page
    for activity in data.get('data', []):
        attr = activity.get('attributes', {})
        # Extract operator licenses from the activity, if present
        job_activities = attr.get('job_activities') or []
        activity_id = activity.get('id')
        # Print licenses in terminal
        print(f"Found {len(job_activities)} job_activities for activity ID {activity_id}")


        # Loop through each field in the current activity
        for job in job_activities:
            # Create a record tuple with parsed values to insert into SQL
            record = (
                int(activity.get('id')),             # parent activity_id
                int(job.get("activity_id")),         # job_activity_id
                job.get("activity_type"),
                job.get("author_user_name"),
                int(job.get("author_user_id")),
                job.get("author_company_name"),
                int(job.get("author_company_id"))
            )


            # Check if the combination already exists to prevent duplicates
            cursor.execute("""
                SELECT 1 FROM job_activities
                WHERE activity_id = ? AND activity_id = ?
            """, (record[0], record[1]))


            # Print skip duplicates in terminal
            if cursor.fetchone():
                print(f"⚠️ Skipping duplicate: job_activities {record[0]}")
                continue


            try:
                # Insert the job_activities data into the table
                cursor.execute("""
                    INSERT INTO job_activities (
                        activity_id,
                        job_activity_id,
                        activity_type,
                        author_user_name,
                        author_user_id,
                        author_company_name,
                        author_company_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, record)
            except pyodbc.IntegrityError:
                print(f"Duplicate ID {record[0]} — skipping.")
                continue


    # Commit after every page
    conn.commit()  


    # Move to the next page
    url = data.get('links', {}).get('next')
    params = {}  # Remove params for subsequent requests, as 'next' already includes them
    pages_fetched += 1  # Increment the page counter


# Print done fetching pages
print(f"✅ Finished. Fetched {pages_fetched} pages of data.")


# Close the cursor and connection
cursor.close()
conn.close()
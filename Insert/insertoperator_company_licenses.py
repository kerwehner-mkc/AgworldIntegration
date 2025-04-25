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


# Make a test API call
try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    print("✅ Connected to API successfully.")
    print(f"Status Code: {response.status_code}")
    print(f"Sample Response: {response.json()[:1] if response.headers.get('Content-Type', '').startswith('application/json') else response.text[:200]}")
except requests.exceptions.RequestException as e:
    print("❌ Failed to connect to API.")
    print(f"Error: {e}")
    exit()


# Parse the API response as JSON
data = response.json()
# Increment the page counter after successfully fetching this page
pages_fetched += 1
# Get the URL for the next page of results (if any)
url = data.get('links', {}).get('next')


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
        operator_company_licenses = attr.get('operator_company_licenses') or []
        activity_id = int(activity.get('id'))
        # Print licenses in terminal
        print(f"Found {len(operator_company_licenses)} operator_company_licenses for activity ID {activity_id}")


        # Loop through each license found in the current activity
        for license in operator_company_licenses:
            # Create a record tuple with parsed values to insert into SQL
            record = (
                int(activity.get('id')),
                license.get('name'),
                license.get('description'),
                license.get('authority'),
                license.get('number'),
                parser.parse(license.get('valid_from')) if license.get('valid_from') else None,
                parser.parse(license.get('valid_to')) if license.get('valid_to') else None,
            )
            # Print insert in terminal
            print("🔄 Inserting record:", record)


            # Check if the combination of activity_id and company license number already exists to prevent duplicates
            cursor.execute("""
                SELECT 1 FROM operator_company_licenses
                WHERE activity_id = ? AND number = ?
            """, (record[0], record[4]))
            # Print skip duplicates in terminal
            if cursor.fetchone():
                print(f"⚠️ Skipping duplicate: activity_id {record[0]}, company license number {record[4]}")
                continue

            try:
                # Insert the new company license record into the database
                cursor.execute("""
                    INSERT INTO operator_company_licenses (
                        activity_id,
                        name,
                        description,
                        authority,
                        number,
                        valid_from,
                        valid_to
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, record)
                conn.commit()  # Commit after each insert for visibility during debugging
                print("✅ Inserted successfully.")
            except pyodbc.IntegrityError:
                # Catch any unexpected primary key/unique constraint issues
                print(f"⚠️ Duplicate activity_id {record[0]} — skipping.")
            except pyodbc.Error as e:
                # Handle general SQL errors and log the problematic record
                print("❌ SQL Insert Error:", e)
                print("🔎 Record causing error:", record)


    # Move to the next page in the paginated API response
    url = data.get('links', {}).get('next')
    pages_fetched += 1


# Print done fetching pages
print(f"✅ Finished. Fetched {pages_fetched} pages of data.")


# Close the cursor and connection
cursor.close()
conn.close()

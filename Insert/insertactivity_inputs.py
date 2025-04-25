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
        activity_inputs = attr.get('activity_inputs') or []
        activity_id = activity.get('id')
        # Print licenses in terminal
        print(f"Found {len(activity_inputs)} activity_inputs for activity ID {activity_id}")


        # Loop through each field in the current activity
        for items in activity_inputs:
            # Create a record tuple with parsed values to insert into SQL
            record = (
                int(activity.get('id')),
                items.get("activity_input_order"),
                items.get("cost_per_area"), 
                items.get("grazing_interval"), 
                items.get("harvest_interval"), 
                items.get("input_name"), 
                items.get("input_type"), 
                items.get("cost_activity_id"),
                items.get("crop_variety_id"),
                items.get("product_id"),
                items.get("national_registration_number"), 
                items.get("mix_method"), 
                items.get("plantback_interval"), 
                json.dumps(items.get("product_categories")), 
                items.get("product_substance"), 
                items.get("rain_fast_interval"), 
                items.get("rate"), 
                items.get("re_entry_interval"), 
                items.get("stockfeed_inverval"), 
                json.dumps(items.get("tags")),
                items.get("total_area"), 
                items.get("total_cost"), 
                items.get("total_count"), 
                items.get("total_time"), 
                items.get("total_volume"), 
                items.get("total_weight"), 
                items.get("unit_cost")
            )


        # Check if the combination of activity_id and license number already exists to prevent duplicates
        cursor.execute("""
        SELECT 1 FROM activity_inputs
        WHERE activity_id = ? AND activity_input_order = ?
        """, (record[0], record[1]))  # record[1] is activity_input_order


        # Print skip duplicates in terminal
        if cursor.fetchone():
            print(f"⚠️ Skipping duplicate: activity_inputs {record[0]}")
            continue


            try:
            # Insert the activity_inputs data into the table
                cursor.execute("""
                    INSERT INTO activity_inputs (
                        activity_id,
                        activity_input_order,
                        cost_per_area,
                        grazing_interval, 
                        harvest_interval, 
                        input_name, 
                        input_type,
                        cost_activity_id,
                        crop_variety_id,
                        product_id,
                        national_registration_number, 
                        mix_method, 
                        plantback_interval, 
                        product_categories, 
                        product_substance, 
                        rain_fast_interval, 
                        rate, 
                        re_entry_interval, 
                        stockfeed_inverval, 
                        tags, 
                        total_area, 
                        total_cost, 
                        total_count, 
                        total_time, 
                        total_volume, 
                        total_weight, 
                        unit_cost
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

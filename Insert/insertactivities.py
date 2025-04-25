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


    # Map the columns
        attr = activity.get('attributes', {})
        record = (
            int(activity.get('id')),
            attr.get('type'),
            attr.get('activity_category'),
            attr.get('application_method'),
            attr.get('approved'),
            attr.get('area'),
            attr.get('author_company_id'),
            attr.get('author_company_name'),
            attr.get('author_user_id'),
            attr.get('author_user_name'),
            attr.get('band'),
            attr.get('chemical_cost'),
            attr.get('comments'),
            attr.get('company_id'),
            attr.get('company_name'),
            attr.get('completed'),
            attr.get('completed_at'),
            attr.get('cost_per_area'),
            parser.parse(attr.get('created_at')) if attr.get('created_at') else None,
            attr.get('created_on'),
            attr.get('droplet_size'),
            parser.parse(attr.get('due_at')) if attr.get('due_at') else None,
            parser.parse(attr.get('expiration_date')) if attr.get('expiration_date') else None,
            json.dumps(attr.get('farm_assets')),
            attr.get('fertilizer_cost'),
            attr.get('humidity'),
            attr.get('nozzle_type'),
            attr.get('operator_company_id'),
            attr.get('operator_company_name'),
            json.dumps(attr.get('operator_company_licenses')),
            attr.get('operation_cost'),
            json.dumps(attr.get('operator_users')),
            attr.get('parent_id'),
            attr.get('reason_name'),
            attr.get('reason_text'),
            attr.get('season_phase'),
            attr.get('seed_cost'),
            attr.get('skip_row'),
            attr.get('specialisation'),
            attr.get('started_at'),
            json.dumps(attr.get('tags')),
            attr.get('temperature'),
            attr.get('timing'),
            attr.get('total_cost'),
            attr.get('total_volume'),
            attr.get('activity_type'),
            parser.parse(attr.get('updated_at')) if attr.get('updated_at') else None,
            attr.get('water_rate'),
            attr.get('weather_conditions'),
            attr.get('wind_direction'),
            attr.get('wind_speed'),
            json.dumps(attr.get('activity_inputs')),
            json.dumps(attr.get('activity_fields')),
            json.dumps(attr.get('activity_problems')),
            json.dumps(attr.get('job_activities')),
            attr.get('job_id'),
            attr.get('job_status'),
            attr.get('colour_id'),
            attr.get('colour_name'),
            attr.get('activity_status')  
        )


        # Check if the combination of activity_id and license number already exists to prevent duplicates
        cursor.execute("""
            SELECT 1 FROM activities
            WHERE id = ?
        """, (record[0],))


        # Print skip duplicates in terminal
        if cursor.fetchone():
            print(f"⚠️ Skipping duplicate: activity_id {record[0]}")
            continue


        # Print insert in terminal
        print("🔄 Inserting record:", record)


        try:
            # Insert the new activity into the database
            cursor.execute("""
                INSERT INTO activities (
                    id,
                    type,
                    activity_category,
                    application_method,
                    approved,
                    area,
                    author_company_id,
                    author_company_name,
                    author_user_id,
                    author_user_name,
                    band,
                    chemical_cost,
                    comments,
                    company_id,
                    company_name,
                    completed,
                    completed_at,
                    cost_per_area,
                    created_at,
                    created_on,
                    droplet_size,
                    due_at,
                    expiration_date,
                    farm_assets,
                    fertilizer_cost,
                    humidity,
                    nozzle_type,
                    operator_company_id,
                    operator_company_name,
                    operator_company_licenses,
                    operation_cost,
                    operator_users,
                    parent_id,
                    reason_name,
                    reason_text,
                    season_phase,
                    seed_cost,
                    skip_row,
                    specialisation,
                    started_at,
                    tags,
                    temperature,
                    timing,
                    total_cost,
                    total_volume,
                    activity_type,
                    updated_at,
                    water_rate,
                    weather_conditions,
                    wind_direction,
                    wind_speed,
                    activity_inputs,
                    activity_fields,
                    activity_problems,
                    job_activities,
                    job_id,
                    job_status,
                    colour_id,
                    colour_name,
                    activity_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,  record)

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
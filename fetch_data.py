"""
fetch_data.py
--------------
Purpose: Connect to data.gov.in's API and pull real-time AQI readings
for Delhi monitoring stations, then save them as a CSV file we can
work with for the rest of the project.
"""

import os                    # lets Python read environment variables
from dotenv import load_dotenv  # reads our .env file and loads it into the environment

load_dotenv()  # this line finds .env in the current folder and loads its values

import requests   # lets Python "ask" a website/server for data over the internet
import pandas as pd  # lets us turn raw data into a table (DataFrame) we can analyze

# ---- STEP 1: Your credentials ----
# These now come from the .env file, NOT hardcoded here.
# os.getenv() looks up a value by name from the environment.
API_KEY = os.getenv("API_KEY")
RESOURCE_ID = os.getenv("RESOURCE_ID")

# Safety check: if these are missing, stop early with a clear message
# instead of a confusing error later.
if not API_KEY or not RESOURCE_ID:
    raise ValueError("API_KEY or RESOURCE_ID missing. Check your .env file.")

# ---- STEP 2: Build the request URL ----
# This is the address we're going to "call" to get data.
# Think of it like a very specific question we're asking the server.
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

params = {
    "api-key": API_KEY,   # proves who we are (so the server trusts us)
    "format": "json",     # we want the response back as JSON (structured text)
    "limit": 1000,        # ask for up to 1000 rows in one go
    "filters[city]": "Delhi",  # ask the SERVER to only send Delhi rows,
                                # instead of downloading all of India and
                                # filtering afterward ourselves
}

# Some servers block requests that "look like" they're from a script
# (Python's requests library identifies itself as "python-requests/x.x" by default).
# We fake a normal browser identity here so the server treats us the same
# way it treats your browser.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

# ---- STEP 3: Make the actual request ----
# Let's print the exact URL we're about to call, so we can debug it.
# requests.Request lets us build the URL without sending it, just to inspect it.
debug_request = requests.Request('GET', BASE_URL, params=params, headers=headers).prepare()
print("Full URL being called:\n", debug_request.url, "\n")

# requests.get() sends our question to the server and waits for a reply.
response = requests.get(BASE_URL, params=params, headers=headers)

# ---- STEP 4: Check if it worked ----
# Every web request returns a "status code".
# 200 means "success". Anything else means something went wrong
# (401 = bad API key, 404 = wrong resource ID, etc.)
print("Status code:", response.status_code)

if response.status_code != 200:
    print("Something went wrong. Response text below:")
    print(response.text)
else:
    # ---- STEP 5: Convert the JSON reply into Python data ----
    data = response.json()

    # The actual rows of data usually live inside a key called "records"
    # Let's peek at the raw structure first, so you SEE what we're working with.
    print("\nTop-level keys in the response:", list(data.keys()))
    print("\nFirst record (one row) looks like this:")
    print(data["records"][0])

    # ---- STEP 6: Turn the list of records into a table ----
    df = pd.DataFrame(data["records"])

    print("\nShape of our table (rows, columns):", df.shape)
    print("\nColumn names:", list(df.columns))
    print("\nFirst 5 rows:")
    print(df.head())

    # ---- STEP 7: Save it so we don't have to re-fetch every time ----
    df.to_csv("data/delhi_aqi_raw.csv", index=False)
    print("\nSaved to data/delhi_aqi_raw.csv")
    #uh

#!/usr/bin/python

import requests
from datetime import datetime, timedelta, timezone

# --- CONFIG ---
CLIST_API_KEY = "username=zcxdr&api_key=79d37ce0131464026c1c5206e73e44fbd301dd23"
RESOURCE_IDS = "1,93" 
START_TIME_SECONDS = 24 * 3600 
# ---

def fetch_upcoming_contests():
    try:
        # --- TIME FIX (v3) ---
        now_dt = datetime.now(timezone.utc)
        later_dt = now_dt + timedelta(seconds=START_TIME_SECONDS)
        
        # Format the time as "YYYY-MM-DD HH:MM:SS" (with a space)
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        later_str = later_dt.strftime("%Y-%m-%d %H:%M:%S")
        # ---
        
        # Construct the API URL
        url = (
            f"https://clist.by/api/v4/contest/?"
            f"{CLIST_API_KEY}"
            f"&resource_id__in={RESOURCE_IDS}"
            # UPDATED: Use the new strftime strings
            f"&start__gt={now_str}"
            f"&start__lt={later_str}"
            f"&order_by=start"
        )
        
        response = requests.get(url)
        response.raise_for_status() 
        
        contests = response.json().get("objects", [])
        
        if not contests:
            print("No upcoming CF/AtCoder contests in the next 24h.")
            return
            
        next_contest = contests[0]
        print(f"Next Contest: {next_contest['event']}")
        print(f"Site: {next_contest['resource']}")
        print(f"Starts: {next_contest['start']}")
        
    except requests.exceptions.HTTPError as e:
        print(f"--- HTTP Error: {e.response.status_code} {e.response.reason} ---")
        print(f"Details: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_upcoming_contests()

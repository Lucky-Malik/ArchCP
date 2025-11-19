#!/usr/bin/python

import requests
from datetime import datetime, timedelta, timezone
import os

# --- CONFIG ---
def load_env():
    # Find the .env file in the same directory as the script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    env_path = os.path.join(script_dir, ".env")
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"')
    except FileNotFoundError:
        pass # No .env file, will fail later (which is ok)

load_env() # Run the function

# Get the key from the environment
CLIST_API_KEY = os.environ.get("CLIST_API_KEY")
RESOURCE_IDS = "1,93" 
START_TIME_SECONDS = 72 * 3600 
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
            print(" None") 
            return

        # Get the next contest
        next_contest = contests[0]
        event_name = next_contest['event']

        # --- NEW: Calculate Time To Event (TTE) ---
        start_time_str = next_contest['start']
        # Convert the API's time string (which is in UTC) into a datetime object
        # We must tell Python it's UTC (timezone.utc)
        start_time_dt = datetime.fromisoformat(start_time_str).replace(tzinfo=timezone.utc)

        # Get current UTC time
        now_dt = datetime.now(timezone.utc)

        # Calculate the difference
        time_diff = start_time_dt - now_dt

        # Format the TTE
        total_seconds = int(time_diff.total_seconds())
        if total_seconds < 0:
            print(" Contest in progress!")
            return

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        # Format the final output string for Polybar
        if days > 0:
            tte_str = f"{days}d {hours}h"
        elif hours > 0:
            tte_str = f"{hours}h {minutes}m"
        else:
            tte_str = f"{minutes}m"

        # Limit the event name length
        if len(event_name) > 30:
            event_name = event_name[:27] + "..."

        # The FINAL, SINGLE-LINE output
        print(f" {event_name} (in {tte_str})")

    except requests.exceptions.HTTPError as e:
        print(f"--- HTTP Error: {e.response.status_code} {e.response.reason} ---")
        print(f"Details: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_upcoming_contests()

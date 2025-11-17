#!/usr/bin/python

import requests

# --- CONFIG ---
# Change this to your Codeforces handle
CODEFORCES_HANDLE = "zcxdr"
# ---

def fetch_cf_rating():
    try:
        # Construct the public API URL
        url = f"https://codeforces.com/api/user.info?handles={CODEFORCES_HANDLE}"

        response = requests.get(url)
        response.raise_for_status() # Check for errors

        data = response.json()

        if data.get("status") == "OK":
            # Get the first user from the result list
            user_info = data.get("result", [])[0]
            rating = user_info.get("rating", "N/A")
            rank = user_info.get("rank", "Unranked")

            # The FINAL, SINGLE-LINE output
            print(f"CF: {rating} ({rank})")
        else:
            print("CF: Error")

    except requests.exceptions.RequestException:
        print("CF: Offline") # Can't connect
    except Exception:
        print("CF: Error") # Any other bug

if __name__ == "__main__":
    fetch_cf_rating()

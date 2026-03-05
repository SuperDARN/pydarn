from datetime import datetime

# This will fail on the old code if 'curl' or 'unzip' are not installed like as default on Windows.
from pydarn.utils import superdarn_radars  

# It should succeed with the new code, and the following should download and extract the files automatically.
print("--- Testing automatic download and read for 'wal' radar ---")
try:
    # Use a recent date
    wal_hdw = superdarn_radars.read_hdw_file('wal', date=datetime(2023, 1, 1))
    print(f"  Station ID: {wal_hdw.stid}") #some test output
except Exception as e:
    print(f"An error occurred: {e}")

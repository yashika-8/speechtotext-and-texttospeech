import os
import time

# Create a file
file_path = './static/test_file.txt'

# Write to the file
with open(file_path, 'w') as f:
    f.write('Test content')

# Sleep for a bit to simulate file usage
time.sleep(5)

# Delete the file
try:
    os.remove(file_path)
    print("File removed successfully")
except Exception as e:
    print(f"Error removing file: {e}")

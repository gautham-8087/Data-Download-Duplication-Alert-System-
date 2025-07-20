import sqlite3

# Connect to the database
conn = sqlite3.connect('downloads_metadata.db')
cursor = conn.cursor()

# Execute SQL command to delete all data from the downloads table
cursor.execute("DELETE FROM downloads")

# Commit the changes
conn.commit()

# Optional: Verify that the table is empty by counting the rows
cursor.execute("SELECT COUNT(*) FROM downloads")
row_count = cursor.fetchone()[0]

if row_count == 0:
    print("All data has been cleared from the downloads table.")
else:
    print(f"Failed to clear data. There are still {row_count} records in the table.")

# Close the connection
conn.close()

#!/usr/bin/env python
"""
Teiko Technical Test Unit Test File
"""
import sqlite3
import os
from database import create_db
from summary import calc_cell_frequencies
from dashboard import fetch_data
from dashboard import distinct_values
import logging

# Suppress Streamlit logging for output
logging.getLogger("streamlit").setLevel(logging.ERROR)

print("BEGIN UNIT TEST")

# Reset db and output formatting setup
os.remove("cell-count.db") if os.path.exists("cell-count.db") else None
results = []

# Test create_db()
try:
    create_db()
    results.append("create_db PASS")
except: 
    results.append("create_db FAIL")

# Test calc_cell_frequencies()
try:
    calc_cell_frequencies()
    results.append("calc_cell_frequencies PASS")
except:
    results.append("calc_cell_frequencies FAIL")

# Test fetch_data()
try:
    df = fetch_data("SELECT * FROM cell_frequencies LIMIT 5")
    print("Data fetched successfully. Sample data:\n")
    print(df)
    print("\n")
    results.append("fetch_data PASS")
except:
    results.append("fetch_data FAIL")

# Test distinct_values()
try:
    distinct_projects = distinct_values("project")
    print("Distinct values fetched successfully. Sample distinct projects:\n")
    print(distinct_projects[:5])  # show first 5 distinct projects
    print("\n")
    results.append("distinct_values PASS")
except:
    results.append("distinct_values FAIL")

# Verify contents of database
try:
    conn = sqlite3.connect("cell-count.db")
    cursor = conn.cursor()
    for table in ["cell_counts", "cell_frequencies"]: # print first 3 rows of each table
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        rows = cursor.fetchall()
        print(f"First 3 rows of {table}:")
        for row in rows:
            print(row)
        print("\n")
    conn.close()
    results.append("Database contents PASS")
except:
    results.append("Database content FAIL")

# Print all results
for res in results:
    print(res)
print("END UNIT TEST")
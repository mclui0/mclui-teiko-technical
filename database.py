#!/usr/bin/env python
"""
Teiko Technical Test Database Setup File
"""

# Imports
import os
import pandas as pd
import sqlite3

# Create database from CSV if not exists
db_path = "cell-count.db"
csv_path = "cell-count.csv"

def create_db():
    """Generates a relational database from a CSV file
    In: N/A
    Out: N/A
    """
    # Check if db already exists
    if os.path.exists(db_path):
        return 
    
    # Set up db connection
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Schema setup
    cursor.execute("DROP TABLE IF EXISTS cell_counts;")
    cursor.execute("""
        CREATE TABLE cell_counts (
            project TEXT NOT NULL,
            subject TEXT NOT NULL,
            condition TEXT NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            treatment TEXT,
            response TEXT,
            sample TEXT NOT NULL,
            sample_type TEXT NOT NULL,
            time_from_treatment_start INTEGER NOT NULL,
            b_cell INTEGER NOT NULL,
            cd8_t_cell INTEGER NOT NULL,
            cd4_t_cell INTEGER NOT NULL,
            nk_cell INTEGER NOT NULL,
            monocyte INTEGER NOT NULL,
            PRIMARY KEY (sample)
        )
    """)

    # Load rows and call function
    df.to_sql('cell_counts', conn, if_exists='append', index=False)
    conn.commit()  # publish schema changes
    conn.close()  # finish
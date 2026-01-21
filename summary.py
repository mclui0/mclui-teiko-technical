#!/usr/bin/env python
"""
Teiko Technical Test Summary Table File
"""

# Imports
import os
import pandas as pd
import sqlite3
from database import create_db  # local db setup file

def calc_cell_frequencies():
    """Calculates cell type frequencies and stores in new table in database
    In: N/A
    Out: N/A
    """
    # Check if db exists, create if not
    if not os.path.exists("cell-count.db"):
        print("Database not found. Running create_db() (db.py) to create database.")
        create_db() 
    conn = sqlite3.connect("cell-count.db")
    cursor = conn.cursor()

    # Create cell_frequencies table
    cursor.execute("DROP TABLE IF EXISTS cell_frequencies;")
    cursor.execute("""
        CREATE TABLE cell_frequencies (
            sample TEXT NOT NULL,
            total_count INTEGER NOT NULL,
            population TEXT NOT NULL,
            count INTEGER NOT NULL,
            percentage REAL NOT NULL,
            PRIMARY KEY (sample, population)
        )
    """)

    # Calculate and populate table
    cursor.execute("""
        WITH sample_totals AS (
            SELECT sample,
                (b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte) AS total_count,
                b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
            FROM cell_counts
        )
        INSERT INTO cell_frequencies (sample, total_count, population, count, percentage)
        SELECT sample, total_count, 'b_cell', b_cell, (b_cell * 100.0) / total_count FROM sample_totals
        UNION ALL
        SELECT sample, total_count, 'cd8_t_cell', cd8_t_cell, (cd8_t_cell * 100.0) / total_count FROM sample_totals
        UNION ALL
        SELECT sample, total_count, 'cd4_t_cell', cd4_t_cell, (cd4_t_cell * 100.0) / total_count FROM sample_totals
        UNION ALL
        SELECT sample, total_count, 'nk_cell', nk_cell, (nk_cell * 100.0) / total_count FROM sample_totals
        UNION ALL
        SELECT sample, total_count, 'monocyte', monocyte, (monocyte * 100.0) / total_count FROM sample_totals
    """)
    conn.commit()  # publish changes
    conn.close()  # finish
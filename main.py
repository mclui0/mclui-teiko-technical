#!/usr/bin/env python
"""
Teiko Technical Test Main File
"""

# NOTES
# populations = b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
# sample_metadata = sample_id, indication, treatment, time_from_treatment_start,
# response, gender

# Imports
import sqlite3
import os
import pandas as pd  # included in requirements.txt
from database import create_db  # local db setup file
from summary import calc_cell_frequencies

def main():
    """Main function to run program and setup files"""

    # Reset db if exists
    os.remove("cell-count.db") if os.path.exists("cell-count.db") else None

    ### Part 1 - Database Setup ###
    create_db()

    ### Parts 2 - Data Overview ###
    calc_cell_frequencies()
    
    ### Parts 3and 4 functionality implemented in dashboard: http://localhost:8501

if __name__ == "__main__":
    main()

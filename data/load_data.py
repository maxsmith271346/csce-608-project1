#!/usr/bin/env python3

# load csvs into separate relations in the database


import os
import sys
import pandas as pd
from clean_data import *

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from utils.database import Database

def load_data(data_dir='./'):
    db = Database("project1", "postgres", "password", "localhost", "5432")
    # drop all tables
    db.drop_all_tables()

    # create schema
    db.define_schema()
    
    
    # Load CSV data into predefined tables
    csv_files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f)) and f.endswith('.csv')]

    
    # Define the order of table loading based on dependencies
    table_order = [
        "session",  # Must be loaded first
        "committee",
        "person",
        "bill",  # Depends on session and committee
        "rollcall",  # Depends on bill
        "document",  # Depends on bill
        "history",  # Depends on bill
        "sast",  # Depends on bill
        "sponsor",  # Depends on bill and person
        "vote"  # Depends on rollcall and person
    ]

    for table_name in table_order:
        csv_file = f"{table_name}.csv"
        if csv_file in csv_files:
            print(f"Loading {table_name}...")
            df = pd.read_csv(os.path.join(data_dir, csv_file))
            df = clean_invalid_dates(df)  # Clean invalid dates if necessary
            db.insert_relation(table_name, df)  # Insert data into the table

if __name__ == "__main__":
    load_data()
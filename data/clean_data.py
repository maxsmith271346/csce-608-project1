#!/usr/bin/env python3

import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

def clean_invalid_dates(df):
    for column in df.select_dtypes(include=['datetime64', 'object']).columns:
        df[column] = df[column].apply(lambda x: None if x == '0000-00-00' else x)
    return df
def clean_data(data_dir='./', subset=None):
    csv_files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f)) and f.endswith('.csv')]
    for csv_file in csv_files:
        df = pd.read_csv(os.path.join(data_dir, csv_file))
        df.drop_duplicates(subset=subset.get(csv_file), inplace=True)
        df.to_csv(os.path.join(data_dir, csv_file), index=False)

if __name__ == "__main__":
    clean_data(subset={"person.csv": ["people_id"]})
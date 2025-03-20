#!/usr/bin/env python3

import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

def bcnf_normalization():
    bills = pd.read_csv("bill.csv")
    history = pd.read_csv("history.csv")
    rollcalls = pd.read_csv("rollcall.csv")
    sasts = pd.read_csv("sast.csv")

    # remove committee from bill
    bills.drop(columns=["committee"], inplace=True, errors='ignore')

    # remove chamber from history
    history.drop(columns=["chamber"], inplace=True, errors='ignore')

    # remove chamber from rollcall
    rollcalls.drop(columns=["chamber"], inplace=True, errors='ignore')

    # remove sast_bill_number from sast
    sasts.drop(columns=["sast_bill_number"], inplace=True, errors='ignore')

    # save the cleaned data
    bills.to_csv("bill.csv", index=False)
    history.to_csv("history.csv", index=False)
    rollcalls.to_csv("rollcall.csv", index=False)
    sasts.to_csv("sast.csv", index=False)

if __name__ == "__main__":
    bcnf_normalization()


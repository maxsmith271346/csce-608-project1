#!/usr/bin/env python3

import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

def remove_unused_columns():
    sessions = pd.read_csv("session.csv")
    votes = pd.read_csv("vote.csv")
    documents = pd.read_csv("document.csv")
    people = pd.read_csv("person.csv")
    sasts = pd.read_csv("sast.csv")
    bills = pd.read_csv("bill.csv")
    committees = pd.read_csv("committee.csv")

    # remove state_id from session
    sessions.drop(columns=["state_id"], inplace=True, errors='ignore')

    # remove vote and rename vote_desc to vote
    votes.drop(columns=["vote"], inplace=True, errors='ignore')
    votes.rename(columns={"vote_desc": "vote"}, inplace=True)

    # remove url from document and rename state_link to url
    documents.drop(columns=["url"], inplace=True, errors='ignore')
    documents.rename(columns={"state_link": "url"}, inplace=True)

    # remove first_name,middle_name,last_name,suffix,nickname,party_id,role_id
    people.drop(columns=["first_name", "middle_name", "last_name", "suffix", "nickname", "party_id", "role_id", "committee_id"], inplace=True, errors='ignore')

    # remove type_id from sast
    sasts.drop(columns=["type_id"], inplace=True, errors='ignore')

    # remove status and url from bill, rename status_desc to status, and state_link to url
    bills.drop(columns=["status", "url"], inplace=True, errors='ignore')
    bills.rename(columns={"status_desc": "status", "state_link": "url"}, inplace=True)

    # remove chamber_id from committee
    committees.drop(columns=["chamber_id"], inplace=True, errors='ignore')

    # save the cleaned data
    sessions.to_csv("session.csv", index=False)
    votes.to_csv("vote.csv", index=False)
    documents.to_csv("document.csv", index=False)
    people.to_csv("person.csv", index=False)
    sasts.to_csv("sast.csv", index=False)
    bills.to_csv("bill.csv", index=False)
    committees.to_csv("committee.csv", index=False)

if __name__ == "__main__":
    remove_unused_columns()



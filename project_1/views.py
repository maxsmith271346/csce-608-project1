from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

from utils.database import Database
from datetime import datetime

class BillsView(View):
    def get(self, request):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        params = {
            "bill_id": request.GET.get('bill_id', ''),
            "session_id": request.GET.get('session_id', ''),
            "bill_number": request.GET.get('bill_number', ''),
            "status": request.GET.get('status', ''),
            "status_desc": request.GET.get('status_desc', ''),
            "status_date": request.GET.get('status_date', ''),
            "title": request.GET.get('title', ''),
            "description": request.GET.get('description', ''),
            "committee_id": request.GET.get('committee_id', ''),
            "committee": request.GET.get('committee', ''),
            "last_action_date": request.GET.get('last_action_date', ''),
            "last_action": request.GET.get('last_action', ''),
            "sponsors": [s.strip() for s in request.GET.get('sponsors', '').split(',') if s.strip()],
        }

        bills = db.get_bills(params)

        context = {
            "bills": [{
                "bill_id": bill[0],
                "session_id": bill[1],
                "bill_number": bill[2],
                "status": bill[3],
                "status_desc": bill[4],
                "status_date": bill[5],
                "title": bill[6] if bill[6] and bill[6] != 'NaN' else bill[2]
            } for bill in bills]
        }

        return render(request, 'project_1/index.html', context)

# TODO: remove committee and id from bills table
class BillView(View):
    def get_sponsors(self, bill_id):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        sponsors = db.get_sponsors(bill_id)

        return sponsors
    
    def get_sasts(self, bill_id):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        sasts = db.get_sasts(bill_id)

        return sasts
    
    def get_rollcalls(self, bill_id):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        rollcalls = db.get_rollcalls(bill_id)

        return rollcalls
    
    def get_history(self, bill_id):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        history = db.get_history(bill_id)

        return history

    def get(self, request, bill_id):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        bill = db.get_bill(bill_id)

        # print(bill)
        committee = db.get_bill_committee(bill_id) or ["N/A", "N/A"]

        context = {
            "bill": {
                "bill_id": bill[0],
                "session_id": bill[1],
                "bill_number": bill[2],
                "status": bill[3],
                "status_desc": bill[4],
                "status_date": bill[5],
                "title": bill[6],
                "description": bill[7],
                "last_action_date": bill[10],
                "last_action": bill[11],
                "url": bill[12],
                "state_link": bill[13],
                "sponsors": [{
                    "name": sponsor[0],
                    "position": sponsor[1],
                    "party": sponsor[2],
                    "role": sponsor[3],
                    "district": sponsor[4],
                    "people_id": sponsor[5],
                } for sponsor in self.get_sponsors(bill_id)],
                "sasts": [{
                    "type": sast[0],
                    "sast_bill_number": sast[1],
                    "sast_bill_id": sast[2],
                    "bill_id": sast[3],
                    "title": sast[4],
                    "bill_number": sast[5],
                } for sast in self.get_sasts(bill_id)],
                "rollcalls": sorted([{
                    "roll_call_id": rollcall[0],
                    "date": rollcall[1],
                    "chamber": rollcall[2],
                    "description": rollcall[3],
                    "yea": rollcall[4],
                    "nay": rollcall[5],
                    "nv": rollcall[6],
                    "absent": rollcall[7],
                    "total": rollcall[8],
                } for rollcall in self.get_rollcalls(bill_id)], key=lambda x: x["roll_call_id"], reverse=True),
                "history": sorted([{
                    "date": history[0],
                    "chamber": history[1],
                    "sequence": history[2],
                    "action": history[3],
                } for history in self.get_history(bill_id)], key=lambda x: x["sequence"], reverse=True),
                "documents": [{
                    "document_id": document[0],
                    "document_type": document[1],
                    "document_size": document[2],
                    "document_mime": document[3],
                    "document_desc": document[4],
                    "url": document[5],
                    "state_link": document[6],
                } for document in db.get_bill_documents(bill_id)],
                "committee": {
                    "chamber": committee[0],
                    "name": committee[1],
                }
            }
        }

        return render(request, 'project_1/bill.html', context)

class PeopleView(View):
    def get(self, request):
        db = Database("project1", "postgres", "password", "localhost", "5432")
        params = {
            "people_id": request.GET.get('people_id', ''),
            "party": request.GET.get('party', ''),
            "role": request.GET.get('role', ''),
            "name": request.GET.get('name', ''),
            "first_name": request.GET.get('first_name', ''),
            "middle_name": request.GET.get('middle_name', ''),
            "last_name": request.GET.get('last_name', ''),
            "suffix": request.GET.get('suffix', ''),
            "nickname": request.GET.get('nickname', ''),
            "district": request.GET.get('district', '')
        }

        people = db.get_people(params)

        context = {
            "people": [dict(person) for person in people]
        }

        return render(request, 'people.html', context)

class PersonView(View):
    def get_votes(self, people_id):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        votes = db.get_votes(people_id)

        return votes
    
    def get_sponsored_bills(self, people_id):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        sponsored_bills = db.get_sponsored_bills(people_id)

        return sponsored_bills

    def get(self, request, people_id):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        person = db.get_person(people_id)

        context = {
            "person": {
            "people_id": person[0],
            "name": person[1],
            "first_name": person[2],
            "middle_name": person[3],
            "last_name": person[4],
            "suffix": person[5],
            "nickname": person[6],
            "party_id": person[7],
            "party": person[8],
            "role_id": person[9],
            "role": person[10],
            "district": person[11],
            "followthemoney_eid": person[12],
            "votesmart_id": person[13],
            "opensecrets_id": person[14],
            "ballotpedia": person[15],
            "knowwho_pid": person[16],
            "committee_id": person[17],
            "votes": sorted([{
                "vote": vote[0],
                "vote_desc": vote[1],
                "date": vote[2],
                "description": vote[3],
                "chamber": vote[4],
                "title": vote[5],
                "bill_number": vote[6],
                "bill_id": vote[7],
                "session_name": vote[8],
            } for vote in self.get_votes(person[0])], key=lambda x: x["date"] or datetime.min.date(), reverse=True),
            "sponsored_bills": sorted([{
                "title": bill[0],
                "bill_number": bill[1],
                "bill_id": bill[2],
                "last_action_date": bill[3],
                "last_action": bill[4],
                "session_name": bill[5],
            } for bill in self.get_sponsored_bills(person[0])], key=lambda x: x["last_action_date"] or datetime.min.date(), reverse=True) 
            }
        }

        return render(request, 'project_1/person.html', context)
    
class RollCallView(View):
    def get(self, request, rollcall_id):
        db = Database("project1", "postgres", "password", "localhost", "5432")

        roll_call = db.get_rollcall(rollcall_id)

        context = {
            "roll_call": {
                "roll_call_id": roll_call[0],
                "date": roll_call[1],
                "chamber": roll_call[2],
                "description": roll_call[3],
                "yea": roll_call[4],
                "nay": roll_call[5],
                "nv": roll_call[6],
                "absent": roll_call[7],
                "total": roll_call[8],
                "bill": {
                    "bill_id": roll_call[9],
                    "title": roll_call[10],
                    "bill_number": roll_call[11],
                    "session_name": roll_call[12],
                },
                "votes": [{
                    "vote": vote[0],
                    "vote_desc": vote[1],
                    "name": vote[2],
                    "party": vote[3],
                    "role": vote[4],
                    "district": vote[5],
                    "people_id": vote[6],
                } for vote in db.get_rollcall_votes(rollcall_id)]
            }
        }

        return render(request, 'project_1/rollcall.html', context)
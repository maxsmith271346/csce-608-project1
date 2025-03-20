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
            "bipartisanship": request.GET.get('bipartisanship', '') == 'on'
        }

        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        page_size = 50  # Number of items per page

        # Get sorting parameters
        sort = request.GET.get('sort', 'bill_id')  # Default sort column
        order = request.GET.get('order', 'asc')  # Default sort order

        # Validate sort column and order
        valid_columns = ['bill_id', 'bill_number', 'title', 'status_desc', 'status_date', 'session_name', 'bipartisanship_score']
        if sort not in valid_columns:
            sort = 'bill_id'
        if order not in ['asc', 'desc']:
            order = 'asc'

        # Fetch bills and total count
        bills, total_bills = db.get_bills(params, page=page, page_size=page_size, sort=sort, order=order)

        # Calculate pagination metadata
        total_pages = (total_bills + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1

        print("Bills", [bill[-1] for bill in bills])

        # TODO: add session name to bill table
        context = {
            "bills": [{
                "bill_id": bill[0],
                "bill_number": bill[1],
                "status": bill[2],
                "status_date": bill[3],
                "title": bill[4] if bill[4] and bill[4] != 'NaN' else bill[1],
                "session_name": bill[5],
                "committee": bill[6],
                "bipartisanship_score": bill[7],
            } for bill in bills],
            "page": page,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous,
            "sort": sort,
            "order": order,
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
                "status_date": bill[4],
                "title": bill[5],
                "description": bill[6],
                "committee_id": bill[7],
                "last_action_date": bill[8],
                "last_action": bill[9],
                "url": bill[10],
                "session_name": bill[11],
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
                    "url": document[5]
                } for document in db.get_bill_documents(bill_id)],
                "committee": {
                    "chamber": committee[0],
                    "name": committee[1],
                },
                "partisan_breakdown": sorted([{
                    "party": partisan[0],
                    "count": partisan[1],
                } for partisan in db.get_partisan_breakdown(bill_id)], key=lambda x: x["party"]),
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
            "people": [{
                "people_id": person[0],
                "name": person[1],
                "party": person[2],
                "role": person[3],
                "district": person[4],
            } for person in people]
        }

        return render(request, 'project_1/people.html', context)

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

        # TODO: add rollcall links

        context = {
            "person": {
                "people_id": person[0],
                "name": person[1],
                "party": person[2],
                "role": person[3],
                "district": person[4],
                "followthemoney_eid": person[5],
                "votesmart_id": person[6],
                "opensecrets_id": person[7],
                "ballotpedia": person[8],
                "knowwho_pid": person[9],
                "votes": sorted([{
                    "vote": vote[0],
                    "date": vote[1],
                    "description": vote[2],
                    "title": vote[3],
                    "bill_number": vote[4],
                    "bill_id": vote[5],
                    "session_name": vote[6],
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
                    "name": vote[1],
                    "party": vote[2],
                    "role": vote[3],
                    "district": vote[4],
                    "people_id": vote[5],
                } for vote in db.get_rollcall_votes(rollcall_id)]
            }
        }

        return render(request, 'project_1/rollcall.html', context)
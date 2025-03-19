import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def drop_all_tables(self):
        # drop all tables
        tables = [
            'bill',
            'person',
            'session',
            'committee',
            'rollcall',
            'document',
            'history',
            'sast',
            'sponsor',
            'vote'
        ]
        for table in tables:
            self.cursor.execute(sql.SQL('DROP TABLE IF EXISTS {} CASCADE').format(sql.Identifier(table)))
        self.conn.commit()

    def define_schema(self):
        # define schema
        schema = """
        CREATE TABLE IF NOT EXISTS bill (
            bill_id INTEGER PRIMARY KEY,
            session_id INTEGER,
            bill_number TEXT,
            status INTEGER,
            status_desc TEXT,
            status_date DATE,
            title TEXT,
            description TEXT,
            committee_id INTEGER,
            committee TEXT,
            last_action_date DATE,
            last_action TEXT,
            url TEXT,
            state_link TEXT
        );
        CREATE TABLE IF NOT EXISTS person (
            people_id INTEGER PRIMARY KEY,
            name TEXT,
            first_name TEXT,
            middle_name TEXT,
            last_name TEXT,
            suffix TEXT,
            nickname TEXT,
            party_id INTEGER,
            party TEXT,
            role_id INTEGER,
            role TEXT,
            district TEXT,
            followthemoney_eid TEXT,
            votesmart_id INTEGER,
            opensecrets_id TEXT,
            ballotpedia TEXT,
            knowwho_pid INTEGER,
            committee_id INTEGER
        );
        CREATE TABLE IF NOT EXISTS session (
            session_id INTEGER PRIMARY KEY,
            state_id INTEGER,
            year_start INTEGER,
            year_end INTEGER,
            prefile BOOLEAN,
            sine_die BOOLEAN,
            prior BOOLEAN,
            special BOOLEAN,
            session_tag TEXT,
            session_title TEXT,
            session_name TEXT
        );
        CREATE TABLE IF NOT EXISTS committee (
            committee_id INTEGER PRIMARY KEY,
            chamber TEXT,
            chamber_id INTEGER,
            name TEXT
        );
        CREATE TABLE IF NOT EXISTS rollcall (
            roll_call_id INTEGER PRIMARY KEY,
            bill_id INTEGER,
            people_id INTEGER,
            date DATE,
            chamber TEXT,
            description TEXT,
            yea INTEGER,
            nay INTEGER,
            nv INTEGER,
            absent INTEGER,
            total INTEGER
        );
        CREATE TABLE IF NOT EXISTS document (
            bill_id INTEGER,
            document_id INTEGER PRIMARY KEY,
            document_type TEXT,
            document_size INTEGER,
            document_mime TEXT,
            document_desc TEXT,
            url TEXT,
            state_link TEXT
        );
        CREATE TABLE IF NOT EXISTS history (
            bill_id INTEGER,
            date DATE,
            chamber TEXT,
            sequence INTEGER,
            action TEXT,
            PRIMARY KEY (bill_id, sequence)
        );
        CREATE TABLE IF NOT EXISTS sast (
            type_id INTEGER,
            type TEXT,
            sast_bill_number TEXT,
            sast_bill_id INTEGER,
            bill_id INTEGER,
            PRIMARY KEY (sast_bill_id, bill_id)
        );
        CREATE TABLE IF NOT EXISTS sponsor (
            bill_id INTEGER,
            people_id INTEGER,
            position INTEGER,
            PRIMARY KEY (bill_id, people_id, position)
        );
        CREATE TABLE IF NOT EXISTS vote (
            roll_call_id INTEGER,
            people_id INTEGER,
            vote INTEGER,
            vote_desc TEXT,
            PRIMARY KEY (roll_call_id, people_id)
        );
        """
        self.cursor.execute(schema)
        self.conn.commit()

    def insert_relation(self, relation_name, df):
        for i, row in df.iterrows():
            query = sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                sql.Identifier(relation_name),
                sql.SQL(', ').join(map(sql.Identifier, df.columns)),
                sql.SQL(', ').join(map(sql.Literal, row))
            )
            self.cursor.execute(query)
        self.conn.commit()

    def get_bills(self, bill_params, page=1, page_size=50):
        # Base query for filtering bills
        query = sql.SQL('''
            SELECT b.*, ss.session_name, sc.D, sc.R,
                (1 - ABS(COALESCE(sc.D, 0) - COALESCE(sc.R, 0)) 
                / NULLIF(COALESCE(sc.D, 0) + COALESCE(sc.R, 0), 0)) 
                * (COALESCE(sc.D, 0) + COALESCE(sc.R, 0)) AS bipartisanship_score
            FROM bill b
            LEFT JOIN (
                SELECT s.bill_id, 
                    COUNT(CASE WHEN p.party = 'D' THEN 1 END) AS D, 
                    COUNT(CASE WHEN p.party = 'R' THEN 1 END) AS R
                FROM sponsor s
                JOIN person p ON s.people_id = p.people_id
                GROUP BY s.bill_id
            ) sc ON b.bill_id = sc.bill_id
            LEFT JOIN session ss ON b.session_id = ss.session_id
            WHERE TRUE
        ''')
        count_query = sql.SQL('SELECT COUNT(*) FROM bill WHERE TRUE')  # Query to count total records

        # Add filters based on bill_params
        if bill_params:
            if 'bill_id' in bill_params and bill_params['bill_id']:
                condition = sql.SQL(' AND bill_id = {}').format(sql.Literal(bill_params['bill_id']))
                query += condition
                count_query += condition
            if 'session_id' in bill_params and bill_params['session_id']:
                condition = sql.SQL(' AND session_id = {}').format(sql.Literal(bill_params['session_id']))
                query += condition
                count_query += condition
            if 'bill_number' in bill_params and bill_params['bill_number']:
                condition = sql.SQL(' AND bill_number = {}').format(sql.Literal(bill_params['bill_number']))
                query += condition
                count_query += condition
            if 'status' in bill_params and bill_params['status']:
                condition = sql.SQL(' AND status = {}').format(sql.Literal(bill_params['status']))
                query += condition
                count_query += condition
            if 'status_desc' in bill_params and bill_params['status_desc']:
                condition = sql.SQL(' AND status_desc ILIKE {}').format(sql.Literal(f"%{bill_params['status_desc']}%"))
                query += condition
                count_query += condition
            if 'status_date' in bill_params and bill_params['status_date']:
                condition = sql.SQL(' AND status_date = {}').format(sql.Literal(bill_params['status_date']))
                query += condition
                count_query += condition
            if 'title' in bill_params and bill_params['title']:
                condition = sql.SQL(' AND title ILIKE {}').format(sql.Literal(f"%{bill_params['title']}%"))
                query += condition
                count_query += condition
            if 'description' in bill_params and bill_params['description']:
                condition = sql.SQL(' AND description ILIKE {}').format(sql.Literal(f"%{bill_params['description']}%"))
                query += condition
                count_query += condition
            if 'committee_id' in bill_params and bill_params['committee_id']:
                condition = sql.SQL(' AND committee_id = {}').format(sql.Literal(bill_params['committee_id']))
                query += condition
                count_query += condition
            if 'committee' in bill_params and bill_params['committee']:
                condition = sql.SQL(' AND committee ILIKE {}').format(sql.Literal(f"%{bill_params['committee']}%"))
                query += condition
                count_query += condition
            if 'last_action_date' in bill_params and bill_params['last_action_date']:
                condition = sql.SQL(' AND last_action_date = {}').format(sql.Literal(bill_params['last_action_date']))
                query += condition
                count_query += condition
            if 'last_action' in bill_params and bill_params['last_action']:
                condition = sql.SQL(' AND last_action ILIKE {}').format(sql.Literal(f"%{bill_params['last_action']}%"))
                query += condition
                count_query += condition
            if 'sponsors' in bill_params and bill_params['sponsors']:
                sponsor_conditions = sql.SQL(' OR ').join(
                    sql.SQL('p.name ILIKE {}').format(sql.Literal(f"%{sponsor}%"))
                    for sponsor in bill_params['sponsors']
                )
                sponsor_filter = sql.SQL('''
                    AND bill_id IN (
                        SELECT bill_id
                        FROM sponsor s
                        JOIN person p ON s.people_id = p.people_id
                        WHERE {}
                    )
                ''').format(sponsor_conditions)
                query += sponsor_filter
                count_query += sponsor_filter

        # Add LIMIT and OFFSET for pagination
        offset = (page - 1) * page_size
        if 'bipartisanship' in bill_params and bill_params['bipartisanship']:
            print('bipartisanship')
            query += sql.SQL(' ORDER BY bipartisanship_score DESC NULLS LAST LIMIT {} OFFSET {}').format(sql.Literal(page_size), sql.Literal(offset))
        else:
            query += sql.SQL(' ORDER BY bill_id LIMIT {} OFFSET {}').format(sql.Literal(page_size), sql.Literal(offset))

        # Execute the count query to get the total number of matching records
        self.cursor.execute(count_query)
        total_count = self.cursor.fetchone()[0]

        # Execute the paginated query to get the current page of results
        self.cursor.execute(query)
        bills = self.cursor.fetchall()

        return bills, total_count

    # TODO: add session name
    def get_bill(self, bill_id):
        query = sql.SQL('''
            SELECT b.*, ss.session_name
            FROM bill b
            JOIN session ss ON b.session_id = ss.session_id
            WHERE bill_id = {}
        ''').format(sql.Literal(bill_id))
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def get_people(self, people_params):
        query = sql.SQL('SELECT people_id, name, party, role, district FROM person WHERE TRUE')
        if people_params:
            if 'people_id' in people_params and people_params['people_id']:
                query += sql.SQL(' AND people_id = {}').format(sql.Literal(people_params['people_id']))
            if 'party' in people_params and people_params['party']:
                query += sql.SQL(' AND party = {}').format(sql.Literal(people_params['party']))
            if 'role' in people_params and people_params['role']:
                query += sql.SQL(' AND role = {}').format(sql.Literal(people_params['role']))
            if 'name' in people_params and people_params['name']:
                query += sql.SQL(' AND name ILIKE {}').format(sql.Literal(people_params['name']))
            if 'district' in people_params and people_params['district']:
                query += sql.SQL(' AND district ILIKE {}').format(sql.Literal(f"%{people_params['district']}%"))
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_person(self, people_id):
        query = sql.SQL('SELECT * FROM person WHERE people_id = {}').format(sql.Literal(people_id))
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def get_sessions(self, session_tag, session_title, session_name, special):
        query = sql.SQL('SELECT * FROM session WHERE TRUE')
        if session_tag:
            query += sql.SQL(' AND session_tag = {}').format(sql.Literal(session_tag))
        if session_title:
            query += sql.SQL(' AND session_title = {}').format(sql.Literal(session_title))
        if session_name:
            query += sql.SQL(' AND session_name = {}').format(sql.Literal(session_name))
        if special:
            query += sql.SQL(' AND special = {}').format(sql.Literal(special))
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_session(self, session_tag):
        query = sql.SQL('SELECT * FROM session WHERE session_tag = {}').format(sql.Literal(session_tag))
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def get_committees(self, committee_id, committee_name, chamber):
        query = sql.SQL('SELECT * FROM committee WHERE TRUE')
        if committee_id:
            query += sql.SQL(' AND committee_id = {}').format(sql.Literal(committee_id))
        if committee_name:
            query += sql.SQL(' AND committee_name = {}').format(sql.Literal(committee_name))
        if chamber:
            query += sql.SQL(' AND chamber = {}').format(sql.Literal(chamber))
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_committee(self, committee_id):
        query = sql.SQL('SELECT * FROM committee WHERE committee_id = {}').format(sql.Literal(committee_id))
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def get_rollcall(self, role_call_id):
        query = sql.SQL('''
            SELECT r.roll_call_id, r.date, r.chamber, r.description,
                r.yea, r.nay, r.nv, r.absent, r.total, b.bill_id, b.title, b.bill_number, s.session_name
            FROM rollcall r
            JOIN bill b ON r.bill_id = b.bill_id
            JOIN session s ON b.session_id = s.session_id
            WHERE r.roll_call_id = {}
        ''').format(sql.Literal(role_call_id))
        self.cursor.execute(query)
        return self.cursor.fetchone()
    
    def get_rollcall_votes(self, role_call_id):
        query = sql.SQL('''
            SELECT v.vote, v.vote_desc, p.name, p.party, p.role, p.district, p.people_id
            FROM vote v
            JOIN person p ON v.people_id = p.people_id
            WHERE v.roll_call_id = {}
        ''').format(sql.Literal(role_call_id))
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_sponsors(self, bill_id):
        query = sql.SQL('''
            SELECT p.name, s.position, p.party, p.role, p.district, s.people_id
            FROM sponsor s
            JOIN person p ON s.people_id = p.people_id
            WHERE s.bill_id = {}
        ''').format(sql.Literal(bill_id))
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_partisan_breakdown(self, bill_id):
        query = sql.SQL('''
            SELECT p.party, COUNT(*) as count
            FROM sponsor s
            JOIN person p ON s.people_id = p.people_id
            WHERE s.bill_id = {}
            GROUP BY p.party
        ''').format(sql.Literal(bill_id))
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_votes(self, people_id):
        query = sql.SQL('''
            SELECT v.vote, v.vote_desc, r.date, r.description, r.chamber, b.title, b.bill_number, b.bill_id, s.session_name
            FROM vote v
            JOIN rollcall r ON v.roll_call_id = r.roll_call_id
            JOIN bill b ON r.bill_id = b.bill_id
            JOIN session s ON b.session_id = s.session_id
            WHERE v.people_id = {}
        ''').format(sql.Literal(people_id))
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_sponsored_bills(self, people_id):
        query = sql.SQL('''
            SELECT b.title, b.bill_number, b.bill_id, b.last_action_date, b.last_action, ss.session_name
            FROM sponsor s
            JOIN bill b ON s.bill_id = b.bill_id
            Join session ss ON b.session_id = ss.session_id
            WHERE s.people_id = {}
        ''').format(sql.Literal(people_id))
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_sasts(self, bill_id):
        query = sql.SQL('''
            SELECT s.type, s.sast_bill_number, s.sast_bill_id, s.bill_id, b.title, b.bill_number
            FROM sast s
            JOIN bill b ON s.sast_bill_id = b.bill_id
            WHERE s.bill_id = {}
        ''').format(sql.Literal(bill_id))
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_rollcalls(self, bill_id):
        query = sql.SQL('''
            SELECT r.roll_call_id, r.date, r.chamber, r.description, r.yea, r.nay, r.nv, r.absent, r.total
            FROM rollcall r
            WHERE r.bill_id = {}
        ''').format(sql.Literal(bill_id))
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_history(self, bill_id):
        query = sql.SQL('''
            SELECT h.date, h.chamber, h.sequence, h.action
            FROM history h
            WHERE h.bill_id = {}
        ''').format(sql.Literal(bill_id))
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_bill_documents(self, bill_id):
        query = sql.SQL('''
            SELECT d.document_id, d.document_type, d.document_size, d.document_mime, d.document_desc, d.url, d.state_link
            FROM document d
            WHERE d.bill_id = {}
        ''').format(sql.Literal(bill_id))
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_bill_committee(self, bill_id):
        query = sql.SQL('''
            SELECT c.chamber, c.name
            FROM committee c
            JOIN bill b ON c.committee_id = b.committee_id
            WHERE b.bill_id = {}
        ''').format(sql.Literal(bill_id))
        self.cursor.execute(query)
        return self.cursor.fetchone()
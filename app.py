#!/usr/bin/env python3
import os
from functools import wraps

import psycopg2
from flask import Flask, request

from db import db_cursor, db_connection

app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in request.cookies:
            return 'You are not logged in'
        db_connection = psycopg2.connect(dbname="postgres", user=request.cookies.get('username'), password=request.cookies.get("password"), host="temp.devmrfitz.xyz",
                                         port="7254")
        db_cursor = db_connection.cursor()
        if request.cookies.get('isEmp'):
            print("isEmp")
            db_cursor.execute("SET ROLE employee")
            db_connection.commit()
        else:
            db_cursor.execute("SET ROLE customer")
            db_connection.commit()
        return f(*args, **kwargs, db_cursor=db_cursor, db_connection=db_connection, username=request.cookies.get('username')+"_" if not request.cookies.get('isEmp') else "")

    return decorated_function


@app.route('/api/customer/list')
@login_required
def list_customers(db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * FROM {username}customer")
    records = db_cursor.fetchall()
    if records is None:
        return {"message": "No customers found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in records]
        return {"data": result}

@app.route('/api/phone/list')
def list_phones():
    db_cursor.execute("SELECT * FROM phone")
    records = db_cursor.fetchall()
    if records is None:
        return {"message": "No phones found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in records]
        return {"data": result}

@app.route('/api/customer/list/<int:customer_id>')
@login_required
def get_customer(customer_id, db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * FROM {username}customer WHERE aadhar_number = {customer_id}")
    record = db_cursor.fetchone()
    if record is None:
        return {"message": "Customer not found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = dict(zip(column_names, record))
        return {"data": result}

@app.route('/api/customer/create', methods=['POST'])
@login_required
def create_customer(db_cursor, db_connection, username):
    db_cursor.execute(f"INSERT INTO {username}customer (aadhar_number, first_name, last_name) "
                      f"VALUES ({request.json['aadhaar_number']}, {request.json['first_name']}, {request.json['last_name']})")
    db_connection.commit()
    return {"message": "Customer created successfully."}


#     plan (phone number)


@app.route('/api/phone/plan/<int:phn_num>')
@login_required
def plan_for_num(phn_num, db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * "
                      f"FROM {username}plan "
                      f"INNER JOIN {username}subscription ON {username}plan.id = {username}subscription.plan_id "
                      f"WHERE {username}subscription.phone_id IN (SELECT id FROM {username}phone WHERE mobile_number = {phn_num})")
    plan = db_cursor.fetchone()
    if plan is None:
        return {"message": "No plan found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = dict(zip(column_names, plan))
        return {"data": result}


@app.route('/api/phone/customer/<int:phn_num>')
@login_required
def profile_of_customer(phn_num, db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * FROM phone WHERE owner IN "
                      f"(SELECT customer.id "
                      f"FROM {username}customer "
                      f"INNER JOIN {username}phone ON {username}customer.id = {username}phone.owner "
                      f"WHERE {username}phone.mobile_number = {phn_num})")
    profile = db_cursor.fetchall()
    if profile is None:
        return {"message": "Customer not found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in profile]
        return {"data": result}


@app.route('/api/phone/sms/<int:phn_num>')
@login_required
def sms_log_for_num(phn_num, db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * "
                      f"FROM {username}sms "
                      f"INNER JOIN {username}phone ON {username}sms.from_id={username}phone.id OR {username}sms.to_id={username}phone.id "
                      f"WHERE {username}phone.id IN (SELECT id FROM {username}phone WHERE mobile_number = {phn_num})")
    sms_log = db_cursor.fetchall()
    if sms_log is None:
        return {"message": "No sms found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in sms_log]
        return {"data": result}


@app.route('/api/phone/call/<int:phn_num>')
@login_required
def call_log_for_num(phn_num, db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * "
                      f"FROM {username}call "
                      f"INNER JOIN {username}phone "
                      f"ON {username}call.from_id={username}phone.id OR {username}call.to_id={username}phone.id "
                      f"WHERE {username}phone.id IN (SELECT id FROM {username}phone WHERE mobile_number = {phn_num})")
    call_log = db_cursor.fetchall()
    if call_log is None:
        return {"message": "No call found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in call_log]
        return {"data": result}


@app.route('/api/plan/list')
@login_required
def get_all_plans(db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * FROM {username}plan")
    plans = db_cursor.fetchall()
    if plans is None:
        return {"message": "No plans found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in plans]
        return {"data": plans}


@app.route('/api/phone/data/<int:phn_num>')
@login_required
def data_log_for_num(phn_num, db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * "
                      f"FROM {username}data_log "
                      f"INNER JOIN {username}phone "
                      f"ON {username}data_log.phone_data={username}phone.id "
                      f"WHERE {username}phone.id IN (SELECT id FROM {username}phone WHERE mobile_number = {phn_num})")
    data_log = db_cursor.fetchall()
    if data_log is None:
        return {"message": "No data found."}
    else:
        return {"data": data_log}


@app.route('/api/phone/mms/<int:phn_num>')
@login_required
def mms_log_for_num(phn_num, db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * "
                      f"FROM {username}mms "
                      f"INNER JOIN {username}phone "
                      f"ON {username}mms.from_id={username}phone.id OR {username}mms.to_id={username}phone.id "
                      f"WHERE {username}phone.id IN (SELECT id FROM {username}phone WHERE mobile_number = {phn_num})")
    mms_log = db_cursor.fetchall()
    if mms_log is None:
        return {"message": "No mms found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in mms_log]
        return {"data": result}


@app.route('/api/employee/list/<int:emp_id>')
@login_required
def employee_profile(emp_id, db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * FROM {username}employee WHERE id = {emp_id}")
    profile = db_cursor.fetchone()
    if profile is None:
        return {"message": "Employee not found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in profile]
        return {"data": result}


@app.route('/api/plan/create', methods=['POST'])
@login_required
def create_plan(db_cursor, db_connection, username):
    db_cursor.execute(
        f"INSERT INTO {username}plan (validity, value, type, cost) VALUES ({request.json('plan_validity')}, {request.json('plan_value')}, {request.json('plan_type')}, {request.json('plan_cost')})")
    db_connection.commit()
    if db_cursor.rowcount == 0:
        return {"message": "Plan not created."}
    else:
        return {"message": "Plan created successfully."}


@app.route('/api/tickets/list')
@login_required
def return_all_active_tickets(db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT * FROM {username}ticket WHERE status = false")
    tickets = db_cursor.fetchall()
    if tickets is None:
        return {"message": "No tickets found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in tickets]
        return {"data": tickets}


@app.route('/verify-creds')
@login_required
def verify_creds():
    try:
        db_cursor.execute(f"SELECT * FROM employee");
        db_cursor.fetchall()
    except:
        return {"message": "Verified", "isEmp": "0"}
    return {"message": "Verified", "isEmp": "1"}




def initiate_database():
    # Create employee role
    db_cursor.execute("CREATE ROLE employee")
    db_connection.commit()
    db_cursor.execute("CREATE ROLE customer")
    db_connection.commit()
    db_cursor.execute("GRANT ALL PRIVILEGES ON DATABASE postgres TO employee")
    db_connection.commit()
    db_cursor.execute("REVOKE ALL ON code_table FROM employee")
    db_connection.commit()
    db_cursor.execute("GRANT SELECT ON code_table TO employee")
    db_connection.commit()
    db_cursor.execute("CREATE USER john WITH PASSWORD 'passjohn'")
    db_connection.commit()
    db_cursor.execute("GRANT customer TO john")
    db_connection.commit()
    db_cursor.execute("CREATE USER alex WITH PASSWORD 'passalex'")
    db_connection.commit()
    db_cursor.execute("GRANT customer TO alex")
    db_connection.commit()
    for customer in ["john", "alex"]:
        customer_id = 1 if customer == "john" else 2
        db_cursor.execute(f"CREATE VIEW {customer}_phone AS "
                          f"SELECT * FROM phone WHERE owner = {customer_id}")
        db_connection.commit()
        db_cursor.execute(f"CREATE VIEW {customer}_data_log AS "
                          f"SELECT * FROM data_log WHERE phone_data IN (SELECT id FROM {customer}_phone)")
        db_connection.commit()
        db_cursor.execute(f"CREATE VIEW {customer}_mms AS "
                          f"SELECT * FROM mms WHERE from_id IN (SELECT id FROM {customer}_phone) OR to_id IN (SELECT id FROM {customer}_phone)")
        db_connection.commit()
        db_cursor.execute(f"CREATE VIEW {customer}_sms AS "
                          f"SELECT * FROM sms WHERE from_id IN (SELECT id FROM {customer}_phone) OR to_id IN (SELECT id FROM {customer}_phone)")
        db_connection.commit()
        db_cursor.execute(f"CREATE VIEW {customer}_ticket AS "
                          f"SELECT * FROM ticket WHERE raiser IN (SELECT id FROM {customer}_phone)")
        db_connection.commit()
        db_cursor.execute(f"CREATE VIEW {customer}_plan AS "
                          f"SELECT * FROM plan")
        db_connection.commit()
        db_cursor.execute(f"CREATE VIEW {customer}_call AS "
                          f"SELECT * FROM call WHERE from_id IN (SELECT id FROM {customer}_phone) OR to_id IN (SELECT id FROM {customer}_phone)")
        db_connection.commit()
        db_cursor.execute(f"CREATE VIEW {customer}_customer AS "
                          f"SELECT * FROM customer WHERE id = {customer_id}")
        db_connection.commit()
        db_cursor.execute(f"CREATE VIEW {customer}_subscription AS "
                          f"SELECT * FROM subscription WHERE phone_id IN (SELECT id FROM {customer}_phone)")
        db_connection.commit()
        db_cursor.execute(f"CREATE VIEW {customer}_tower AS "
                          f"SELECT * FROM tower")
        db_connection.commit()
        db_cursor.execute(f"GRANT ALL ON {customer}_phone TO {customer}")
        db_connection.commit()
        db_cursor.execute(f"GRANT ALL ON {customer}_data_log TO {customer}")
        db_connection.commit()
        db_cursor.execute(f"GRANT ALL ON {customer}_mms TO {customer}")
        db_connection.commit()
        db_cursor.execute(f"GRANT ALL ON {customer}_sms TO {customer}")
        db_connection.commit()
        db_cursor.execute(f"GRANT ALL ON {customer}_ticket TO {customer}")
        db_connection.commit()
        db_cursor.execute(f"GRANT ALL ON {customer}_call TO {customer}")
        db_connection.commit()
        db_cursor.execute(f"GRANT ALL ON {customer}_customer TO {customer}")
        db_connection.commit()
        db_cursor.execute(f"GRANT ALL ON {customer}_subscription TO {customer}")
        db_connection.commit()


if __name__ == '__main__':
    port = os.getenv('PORT', '8000')
    app.run(debug=False, host='0.0.0.0', port=int(port))

#
# // ticket page
# // kyc checker/signup and login
# // customer features
#      // ticket  radio for tower or phone
#     //call log for a particular customer (phone number)(done)
#     //plan (phone number)(done)
#     //data of customer, all the phone numbers owned by him and
#     //payment(no sense)
#     //profile(every detail about the customer holding the phone number)(phone number)(done but I need all the number related to that person)
#     //sms that a phone number has received or sent (phone number)(done)
#     //call (from ka number, to ka number, duration)(phone number)(done)
#     //data log (from ka number, to ka number, duration)(phone number)(done)
#     //mms log (from ka number, to ka number, duration)(phone number)(done)
#
# // employee features
#     //create plan(all except id)
#     //payment(no sense)
#     //profile details(id)
#     //incomplete kyc(no sense)
#     //tower to be serviced and marked(to think)
#     //open tickets view(return all details of false wale tickets)
#     //mark a ticket as true(abhi hold rakho)

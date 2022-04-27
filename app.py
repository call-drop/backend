#!/usr/bin/env python3
import datetime
import os
from functools import wraps

import psycopg2
from flask import Flask, request
from flask_cors import CORS

import db

from db import db_cursor, db_connection

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'https://calldrop.netlify.app'],
     supports_credentials=True)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in request.cookies:
            db_connection = psycopg2.connect(dbname="postgres", user=request.cookies.get('username'),
                                             password=request.cookies.get("password"), host="temp.devmrfitz.xyz",
                                             port="7254")
            db_cursor = db_connection.cursor()
            username = request.cookies.get('username')
            isEmp = request.cookies.get('isEmp')
            if request.cookies.get('isEmp'):
                print("isEmp")
                db_cursor.execute("SET ROLE employee")
                db_connection.commit()
            else:
                db_cursor.execute("SET ROLE customer")
                db_connection.commit()
        elif 'username' in request.headers:
            db_connection = psycopg2.connect(dbname="postgres", user=request.headers.get('username'),
                                             password=request.headers.get("password"), host="temp.devmrfitz.xyz",
                                             port="7254")
            db_cursor = db_connection.cursor()
            username = request.headers.get('username')
            isEmp = request.headers.get('isEmp')
            if request.headers.get('isEmp'):
                print("isEmp")
                db_cursor.execute("SET ROLE employee")
                db_connection.commit()
            else:
                db_cursor.execute("SET ROLE customer")
                db_connection.commit()
        else:
            return "You must be logged in to access this page", 401
        return f(*args, **kwargs, db_cursor=db_cursor, db_connection=db_connection,
                 username=username + "_" if not isEmp else "")

    return decorated_function


@app.route('/api/sms/create', methods=['POST'])
@login_required
def create_sms(db_cursor, db_connection, username):
    db_cursor.execute(f"INSERT INTO {username}sms (from_id, to_id, content, time_stamp ) "
                      f"VALUES ({request.json['from_id']}, {request.json['to_name']}, '{request.json['content']}', '{datetime.datetime.now()}')")
    db_connection.commit()
    return {"message": "SMS created successfully."}

@app.route('/api/tower/maintainence/<int:tower_id>')
@login_required
def change_tower_maintenance_status(tower_id, db_cursor, db_connection, username):
    db_cursor.execute(f"UPDATE tower SET needs_maintenance = false, last_maintained = '{datetime.datetime.now()}' WHERE id = {tower_id}")
    db_connection.commit()
    return {"message": "Tower Maintenance status changed successfully."}

@app.route('/api/mms/create', methods=['POST'])
@login_required
def create_mms(db_cursor, db_connection, username):
    db_cursor.execute(f"INSERT INTO {username}mms (from_id, to_id, content, time_stamp, file_name, subject ) "
                      f"VALUES ({request.json['from_id']}, {request.json['to_name']}, '{request.json['content']}', "
                      f"'{datetime.datetime.now()}', '{request.json['file_name']}', '{request.json['subject']}')")
    db_connection.commit()
    return {"message": "MMS created successfully."}


@app.route('/api/call/create', methods=['POST'])
@login_required
def create_call(db_cursor, db_connection, username):
    db_cursor.execute(f"INSERT INTO {username}call (from_id, to_id, start_time, end_time ) "
                      f"VALUES ({request.json['from_id']}, {request.json['to_name']}, '{datetime.datetime.now()}', '{datetime.datetime.now() + datetime.timedelta(seconds=int(request.json['duration']))}')")
    db_connection.commit()
    return {"message": "Call created successfully."}


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


@app.route('/api/customer/phone_number_list/<int:customer_id>')
@login_required
def get_phone_nums_for_customer(customer_id, db_cursor, db_connection, username):
    db.db_cursor.execute(f"SELECT * FROM {username}phone WHERE owner = {customer_id}")
    records = db_cursor.fetchall()
    if records is None:
        return {"message": "No phone numbers found."}
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
                      f"VALUES ({request.json['aadhaar_number']}, '{request.json['first_name']}', '{request.json['last_name']}')")
    db_connection.commit()
    return {"message": "Customer created successfully."}


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
def profile_of_customer(phn_num, db_cursor, db_connection, username):  # on hold
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


@app.route('/api/plan/update/')
@login_required
def update_plan(db_cursor, db_connection, username, plan_id, plan_validity, plan_value, plan_cost, plan_type):
    db_cursor.execute(f"UPDATE {username}plan "
                      f"SET validity = {plan_validity}, value = {plan_value}, type = {plan_type}, cost = {plan_cost} "
                      f"WHERE id = {plan_id}")
    db_connection.commit()
    return {"message": "Plan updated successfully."}


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
        return {"data": result}


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
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in data_log]
        return {"data": result}


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
        result = [dict(zip(column_names, profile))]
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

@app.route('/api/ticket/create', methods=['POST'])
@login_required
def create_ticket(db_cursor, db_connection, username):
    db_cursor.execute(f"INSERT INTO {username}ticket (timestamp , status, resolver, raiser) VALUES ('{datetime.datetime.now()}', false , null , SELECT owner FROM phone WHERE mobile_number = int(request.json('ticket_mobile_number')))")
    db_connection.commit()
    if db_cursor.rowcount == 0:
        return {"message": "Ticket not created."}
    else:
        return {"message": "Ticket created successfully."}

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
        return {"data": result}


@app.route('/api/owner/plan/<int:owner_id>')
@login_required
def plan_for_owner_id(owner_id, db_cursor, db_connection, username):
    db_cursor.execute(
        f"SELECT {username}plan.validity, {username}plan.value, {username}plan.type, {username}plan.cost, {username}subscription.recharge_date "
        f"FROM {username}plan INNER JOIN {username}subscription ON "
        f"{username}plan.id = {username}subscription.plan_id WHERE "
        f"{username}subscription.phone_id IN ("
        f"SELECT c.id FROM {username}customer AS c INNER JOIN {username}phone ON {username}phone.owner = c.id "
        f"WHERE {username}phone.is_active=true AND {username}phone.owner = {owner_id})")
    plan = db_cursor.fetchall()
    if plan is None:
        return {"message": "No plan found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in plan]
        return {"data": result}


@app.route('/api/customer/last_location/<int:cust_id>')
@login_required
def last_known_location_for_custID(cust_id, db_cursor, db_connection, username):
    db_cursor.execute(f"SELECT phone.mobile_number, street_name "
                      f"FROM customer AS c "
                      f"INNER JOIN phone on phone.owner = c.id"
                      f"INNER JOIN public.tower t on t.id = phone.last_known_location "
                      f"where c.id = {cust_id}")
    last_known_location = db_cursor.fetchall()
    if last_known_location is None:
        return {"message": "Customer not found."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in last_known_location]
        return {"data": result}


@app.route('/verify-creds')
@login_required
def verify_creds():
    try:
        db_cursor.execute(f"SELECT * FROM employee");
        db_cursor.fetchall()
    except:
        return {"message": "Verified", "isEmp": "0"}
    return {"message": "Verified", "isEmp": "1"}


def setup_triggers():
    db_cursor.execute("""CREATE OR REPLACE FUNCTION customer_insert_trigger() RETURNS TRIGGER AS $$
                      DECLARE
                          n varchar(255);
                      BEGIN
                          n = NEW.first_name;
                          CREATE USER n WITH PASSWORD 'password';
                          GRANT customer to n;
                          RETURN NEW;
                      END
                      $$ LANGUAGE plpgsql;"""
                      )
    db_connection.commit()
    db_cursor.execute(f"CREATE TRIGGER customer_insert_trigger "
                      f"AFTER INSERT ON customer FOR EACH ROW "
                      f"EXECUTE PROCEDURE customer_insert_trigger()")
    db_connection.commit()

    db_cursor.execute("""CREATE OR REPLACE FUNCTION customer_delete_trigger() RETURNS TRIGGER AS $$
                          DECLARE
                              n varchar(255);
                          BEGIN
                              n = OLD.first_name;
                              REVOKE customer from n;
                              DROP USER n;
                              RETURN OLD;
                          END
                          $$ LANGUAGE plpgsql;"""
                      )
    db_connection.commit()
    db_cursor.execute(f"""CREATE TRIGGER customer_delete_trigger 
                      AFTER DELETE ON customer FOR EACH ROW 
                      EXECUTE PROCEDURE customer_delete_trigger()""")


def create_indices(db_cursor, db_connection, username):
    db_cursor.execute(f"CREATE INDEX phone_index ON phone(mobile_number)")
    db_cursor.execute(f"CREATE INDEX plan_index ON plan(validity)")
    db_cursor.execute(f"CREATE INDEX subscription_plan_phone_index ON subscription(phone_id, plan_id)")
    db_cursor.execute(f"CREATE INDEX ticket_index ON ticket (status)")
    db_cursor.execute(f"CREATE INDEX from_to_call_index ON call (from_id, to_id)")
    db_cursor.execute(f"CREATE INDEX from_to_mms_index ON mms (from_id, to_id)")
    db_cursor.execute(f"CREATE INDEX from_to_sms_index ON sms (from_id, to_id)")
    db_cursor.execute(f"CREATE INDEX phone_owner_index ON phone (owner)")
    db_cursor.execute(f"CREATE INDEX works_at_employee_index ON employee(works_at)")
    db_cursor.execute(f"CREATE INDEX phone_data_datalog_index ON data_log(phone_id)")
    db_cursor.execute(f"CREATE INDEX area_officeID_tower_index ON tower(maintenance_office)")

    db_connection.commit()


@app.route('/api/towers-to-maintain')
def return_towers_to_maintain():
    db_cursor.execute(f"""SELECT *
    FROM tower
    WHERE tower.id IN (
    SELECT phone.last_known_location
    FROM phone
    GROUP BY phone.last_known_location
    ORDER BY count(*) DESC
    ) AND needs_maintenance = true;""")
    towers = db_cursor.fetchall()
    if towers is None:
        return {"message": "No towers to maintain."}
    else:
        column_names = [desc[0] for desc in db_cursor.description]
        result = [dict(zip(column_names, row)) for row in towers]
        return {"data": result}


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

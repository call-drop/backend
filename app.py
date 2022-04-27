#!/usr/bin/env python3
import os

from flask import Flask, request

from db import db_cursor, db_connection

app = Flask(__name__)


@app.route('/api/customer/list')
def list_customers():
    db_cursor.execute("SELECT * FROM customer")
    records = db_cursor.fetchall()
    column_names = [desc[0] for desc in db_cursor.description]
    result = [dict(zip(column_names, row)) for row in records]
    return {"data": result}


@app.route('/api/customer/list/<int:customer_id>')
def get_customer(customer_id):
    db_cursor.execute(f"SELECT * FROM customer WHERE id = {customer_id}")
    record = db_cursor.fetchone()
    return {"data": record}


@app.route('/api/customer/create', methods=['POST'])
def create_customer():
    # Customer: Aadhaar number, first name, last name

    db_cursor.execute(
        f"INSERT INTO customer (aadhar_number, first_name, last_name) VALUES ({request.json['aadhaar_number']}, {request.json['first_name']}, {request.json['last_name']})")
    db_connection.commit()
    return {"message": "Customer created successfully."}

#     plan (phone number)


@app.route('/api/phone/plan/<int:phn_num>')
def plan_for_num(phn_num):
    db_cursor.execute(f"SELECT * "
                      f"FROM plan "
                      f"INNER JOIN subscription ON plan.id = subscription.plan_id "
                      f"WHERE subscription.phone_id IN (SELECT id FROM phone WHERE mobile_number = {phn_num})")
    plan = db_cursor.fetchone()
    return plan

@app.route('/api/phone/customer/<int:phn_num>')
def profile_of_customer(phn_num):
    db_cursor.execute(f"SELECT * "
                      f"FROM customer "
                      f"INNER JOIN phone ON customer.id = phone.owner "
                      f"WHERE phone.mobile_number = {phn_num}")
    profile = db_cursor.fetchone()
    return profile

@app.route('/api/phone/sms/<int:phn_num>')
def sms_log_for_num(phn_num):
    db_cursor.execute(f"SELECT * "
                      f"FROM sms "
                      f"INNER JOIN phone ON sms.from_id=phone.id OR sms.to_id=phone.id "
                      f"WHERE phone.id IN (SELECT id FROM phone WHERE mobile_number = {phn_num})")
    sms_log = db_cursor.fetchall()
    return sms_log

@app.route('/api/phone/call/<int:phn_num>')
def call_log_for_num(phn_num):
    db_cursor.execute(f"SELECT * "
                      f"FROM call "
                      f"INNER JOIN phone "
                      f"ON call.from_id=phone.id OR call.to_id=phone.id "
                      f"WHERE phone.id IN (SELECT id FROM phone WHERE mobile_number = {phn_num})")
    call_log = db_cursor.fetchall()
    return call_log

@app.route('/api/plan/list')
def get_all_plans():
    db_cursor.execute("SELECT * FROM plan")
    plans = db_cursor.fetchall()
    return plans

@app.route('/api/phone/data/<int:phn_num>')
def data_log_for_num(phn_num):
    db_cursor.execute(f"SELECT * "
                      f"FROM data_log "
                      f"INNER JOIN phone "
                      f"ON data_log.phone_data=phone.id " 
                      f"WHERE phone.id IN (SELECT id FROM phone WHERE mobile_number = {phn_num})")
    data_log = db_cursor.fetchall()
    return data_log

@app.route('/api/phone/mms/<int:phn_num>')
def mms_log_for_num(phn_num):
    db_cursor.execute(f"SELECT * "
                      f"FROM mms "
                      f"INNER JOIN phone "
                      f"ON mms.from_id=phone.id OR mms.to_id=phone.id "
                      f"WHERE phone.id IN (SELECT id FROM phone WHERE mobile_number = {phn_num})")
    mms_log = db_cursor.fetchall()
    return mms_log

@app.route('/api/employee/list/<int:phn_num>')
def employee_profile(emp_id):
    db_cursor.execute(f"SELECT * FROM employee WHERE id = {emp_id}")
    profile = db_cursor.fetchone()
    return profile

@app.route('/api/plan/create', methods=['POST'])
def create_plan(plan_validity, plan_value, plan_type, plan_cost):
    db_cursor.execute(f"INSERT INTO plan (validity, value, type, cost) VALUES ({plan_validity}, {plan_value}, {plan_type}, {plan_cost})")
    db_connection.commit()
    return {"message": "Plan created successfully."}

@app.route('/api/tickets/list/<int:phn_num>')
def return_all_active_tickets():
    db_cursor.execute("SELECT * FROM ticket WHERE status = false")
    tickets = db_cursor.fetchall()
    return tickets


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

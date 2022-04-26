#!/usr/bin/env python3
from flask import Flask, request

from db import db_cursor, db_connection

app = Flask(__name__)


@app.route('/api/customer/list')
def list_customers():  # put application's code here
    db_cursor.execute("SELECT * FROM customer")
    records = db_cursor.fetchall()
    return {"data": records}


@app.route('/api/customer/list/<int:pk>')
def get_customer(pk):  # put application's code here
    db_cursor.execute(f"SELECT * FROM customer WHERE id = {pk}")
    record = db_cursor.fetchone()
    return {"data": record}


@app.route('/api/customer/create', methods=['POST'])
def create_customer():
    # Customer: Aadhaar number, first name, last name

    db_cursor.execute(
        f"INSERT INTO customer (aadhar_number, first_name, last_name) VALUES ({request.json['aadhaar_number']}, {request.json['first_name']}, {request.json['last_name']})")
    db_connection.commit()
    return {"message": "Customer created successfully."}

def call_log_for_num(phn_num):
    db_cursor.execute(f"SELECT id FROM phone WHERE phone_number = {phn_num}")
    phone_id = db_cursor.fetchone()
    db_cursor.execute(f"SELECT * FROM call_log WHERE phone_id = {phone_id}")
    call_log = db_cursor.fetchall()
    return call_log

#     plan (phone number)

def plan_for_num(phn_num):
    db_cursor.execute(f"")
    phone_id = db_cursor.fetchone()
    db_cursor.execute(f"SELECT * FROM plan WHERE phone_id = SELECT id FROM phone WHERE phone_number = {phn_num}")
    plan = db_cursor.fetchone()
    return plan

def profile_of_customer(phn_num):
    db_cursor.execute(f"SELECT id FROM phone WHERE phone_number = {phn_num}")
    phone_id = db_cursor.fetchone()
    db_cursor.execute(f"SELECT * FROM customer WHERE phone_id = {phone_id}")
    profile = db_cursor.fetchone()
    return profile

def

if __name__ == '__main__':
    app.run()

#
# // ticket page
# // kyc checker/signup and login
# // customer features
#      // ticket  radio for tower or phone
#     //call log for a particular customer (phone number)
#     //plan (phone number)
#     //payment(no sense)
#     //profile(every detail about the customer holding the phone number)(phone number)
#     //sms that a phone number has received or sent (phone number)
#     //call (from ka number, to ka number, duration)
#     //data log (from ka number, to ka number, duration)
#     //mms log (from ka number, to ka number, duration)
#
# // employee features
#     //create plan(all except id)
#     //payment(no sense)
#     //profile details(id)
#     //incomplete kyc(no sense)
#     //tower to be serviced and marked(to think)
#     //open tickets view(return all details of false wale tickets)
#     //mark a ticket as true(abhi hold rakho)
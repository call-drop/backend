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

    db_cursor.execute(f"INSERT INTO customer (aadhar_number, first_name, last_name) VALUES ({request.json['aadhaar_number']}, {request.json['first_name']}, {request.json['last_name']})")
    db_connection.commit()
    return {"message": "Customer created successfully."}


if __name__ == '__main__':
    app.run()

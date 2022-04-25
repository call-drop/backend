#!/usr/bin/env python3

import psycopg2

# Connect to your postgres DB
db_connection = psycopg2.connect(dbname="postgres", user="user", password="password", host="temp.devmrfitz.xyz", port="7254")

# Open a cursor to perform database operations
db_cursor = db_connection.cursor()
#
# # Execute a query
# db_cursor.execute("SELECT * FROM customer")
#
# # Retrieve query results
# records = db_cursor.fetchall()
#
# print(records)
#
#
# # Execute a query
# db_cursor.execute("SELECT * FROM customer where id = 1")
#
# # Retrieve query results
# records = db_cursor.fetchall()
#
# print(records)

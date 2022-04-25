#!/usr/bin/env python3
from flask import Flask

from db import db_cursor

app = Flask(__name__)


@app.route('/api/list-customers')
def list_customers():  # put application's code here
    db_cursor.execute("SELECT * FROM customer")
    records = db_cursor.fetchall()
    return {"data": records}


if __name__ == '__main__':
    app.run()

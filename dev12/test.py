#!flask/bin/python
import pymysql.cursors
from flask import Flask, jsonify
from flask import request

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

status_flag = True

status_enable = {'status': 'enable'}

status_disable = {'status': 'disable'}


@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


@app.route('/status', methods=['GET'])
def get_status():
    global status_flag

    mac = request.args.get('mac')
    key_SN = request.args.get('key_SN')
    config_SN = request.args.get('config_SN')

    print("status -->>> ", mac, key_SN, config_SN)

    if key_SN == "none":
        print("OLD key_SN")
    if config_SN == "none":
        print("OLD config_SN")

    print()

    x = None
    if status_flag:
        x = status_enable
    else:
        x = status_disable

    status_flag = not status_flag
    return jsonify(x)


@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    print("Login ---->>> (" + username + ", " + password + ")")

    return jsonify(status_disable)


@app.route('/test', methods=['GET'])
def get_test():
    try:
        # Connect to the database
        connection = pymysql.connect(host='localhost',
                                     user='testuser',
                                     password='password',
                                     db='testdb',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            # Create a new record

            sql = "INSERT INTO users (email, password) VALUES (%s, %s)"
            cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT id, password FROM users WHERE email=%s"
            cursor.execute(sql, ('webmaster@python.org',))
            # result = cursor.fetchone()
            result = cursor.fetchall()
            print(result)
            print(type(result))
    finally:
        connection.close()
    return jsonify({'tasks': tasks})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)

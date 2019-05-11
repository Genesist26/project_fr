from subprocess import check_output

from flask import Flask

app = Flask(__name__)
ip = check_output(['hostname', '-I'])

@app.route('/')
def hello():
    return "Hello World!"


if __name__ == '__main__':
    app.run(host=ip.decode('ascii'))

import threading

def hello():
    print("hello, Timer")

t = threading.Timer(3.0, hello)
t.start()
import json

x = '{ "name":"John", "age":30, "city":"New York"}'
y = json.loads(x)
print(type(y))

# the result is a Python dictionary:
print(y["age"])
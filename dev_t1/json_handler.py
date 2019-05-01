import json

# # some JSON:
# x = '{ "name":"John", "age":30, "city":"New York"}'
#
# # parse x:
# y = json.loads(x)
#
# # the result is a Python dictionary:
# print(y["age"])

# Convert a Python object containing all the legal data types:
x = {
    'faceId': '2bed5571-71e8-4930-9fae-b2ba46db077d',
    'faceRectangle': {
        'top': 335,
        'left': 249,
        'width': 319,
        'height': 319
    },
    'faceAttributes': {
        'smile': 1.0,
        'headPose': {
            'pitch': 0.0,
            'roll': -3.7,
            'yaw': -2.6
        },
        'gender': 'male',
        'age': 43.0,
        'facialHair': {
            'moustache': 0.1,
            'beard': 0.1,
            'sideburns': 0.1
        }
    }
}

y = json.loads(json.dumps(x))
if 'faceId' in x.keys():
    print('True')
else:
    print('False')
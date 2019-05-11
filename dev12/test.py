li = [{'faceId': '4f366a75-cede-4c41-bc7a-d0b99099a436',
       'faceRectangle': {'top': 295, 'left': 488, 'width': 231, 'height': 231}},
      {'faceId': 'd1be2d7f-85a3-43ef-b044-4558ef140fe3',
       'faceRectangle': {'top': 269, 'left': 906, 'width': 207, 'height': 207}}]

new_li = [d for d in li if d['faceId'] != '4f366a75-cede-4c41-bc7a-d0b99099a436']
print(li)

import cognitive_face as CF

KEY = 'ce5f9a111c7a4a26b8fd0f88ab2fe47a'  # Replace with a valid subscription key (keeping the quotes in place).
CF.Key.set(KEY)

BASE_URL = 'https://southeastasia.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL
CF.BaseUrl.set(BASE_URL)

person_list = CF.person.lists('myteams')
print(person_list)
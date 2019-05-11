from urllib.request import urlopen

url_str = "http://google.com"
urlopen(url_str)

try:
    res = urlopen(url_str)
    print("Has internet connection")

except:
    print("No internet connection")
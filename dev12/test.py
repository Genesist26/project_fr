import re

e = "Error when calling Cognitive Face API: status_code: 429" \
    "code: None " \
    "message: Rate limit is exceeded. Try again in 41 seconds."

s = "message: Rate limit is exceeded. Try again in 41 seconds."
# s = "Part 1. Try 41 seconds then more text"
delay_str = re.search(r'Try again in(.*?)seconds', e).group(1)
delay = int(delay_str)
print(delay)
# print(y)
import requests
web=requests.get("https://www.tutorialsfreak.com/")
print(web)
a=web.content
print(a)
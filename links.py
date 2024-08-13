import requests
from bs4 import BeautifulSoup
web=requests.get("https://www.tutorialsfreak.com/")
soup=BeautifulSoup(web.content,"html.parser")
links=soup.find_all("a")
(links)
for i in links:
    print (i.get("href"))
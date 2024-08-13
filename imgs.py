import requests
from bs4 import BeautifulSoup
web=requests.get("https://www.tutorialsfreak.com/")
soup=BeautifulSoup(web.content,"html.parser")
img=soup.find_all("img")
#print(img)
for i in img:
    print(i.get("src"))
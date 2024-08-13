import requests
from bs4 import BeautifulSoup
web=requests.get("https://www.tutorialsfreak.com/")
soup=BeautifulSoup(web.content,"html.parser")
lines=soup.find_all("p")
#print(lines)


s=soup.find("p",class_="section-subheading mb-0")
print(s)
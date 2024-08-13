import requests
from bs4 import BeautifulSoup
import json

web = requests.get("https://vidiq.com/youtube-stats/channel/UCeVMnSShP_Iviwkknt83cww/")
soup = BeautifulSoup(web.content, "html.parser")


data = {
    "channel_name": "CodeWithHarry",
    "Overall Score": soup.find('p', {'class': 'mb-8 text-center text-[88px] font-extrabold leading-[68px]'}).text.strip(),
}

# Finding all elements using find_all:
elements = soup.find_all("p", {'class': "mb-1 text-xl font-extrabold text-white lg:text-[26px] lg:leading-[30px]"})

#indexing using elements
#this is the OVERALL SCORE DATA
data["Subscribers"] = elements[0].text.strip()
data["Video views"] = elements[1].text.strip()
data["Monthly Earnings"] = elements[2].text.strip()
data["Engagement rate"] = elements[3].text.strip()
data["Video Upload Frequency"]=elements[4].text.strip()
data["Average Video Length"]=elements[5].text.strip()

# Convert to JSON and print
json_data = json.dumps(data, indent=4)
print(json_data)

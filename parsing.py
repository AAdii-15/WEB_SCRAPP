# Importing the requests library to make HTTP requests
import requests

# Importing BeautifulSoup from the bs4 library for parsing HTML
from bs4 import BeautifulSoup

# Sending a GET request to the specified URL and storing the response in 'web'
web = requests.get("https://www.tutorialsfreak.com/")

# Printing the status code of the response to check if the request was successful (200 means OK)
web.status_code

# Storing the content of the response (HTML of the webpage) in 'a'
a = web.content

# Creating a BeautifulSoup object 'soup' to parse the HTML content using the 'html.parser'
soup = BeautifulSoup(a, "html.parser")

# Printing the prettified (formatted) version of the HTML content
print(soup.prettify())

# Printing the title tag of the HTML content
print(soup.title)

# Printing the first paragraph (p) tag of the HTML content
print(soup.p)

#TAGS
tag=soup.html
print(type(tag))

tag=soup.p
print(tag)


#soup
print(soup.find_all("p"))
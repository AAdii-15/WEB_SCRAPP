import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = 'https://vidiq.com/youtube-stats/channel/UCeVMnSShP_Iviwkknt83cww/'

# Fetch the HTML content
response = requests.get(url)
html_content = response.text

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

script = soup.findAll('script')
print(len(script))
print(script[-5])

# Extract the SVG element where the graph data is located
# svg = soup.find('svg')

# # Check if SVG is found
# if svg:
#     # Extract text labels for the x-axis (months) and y-axis (video views)
#     x_labels = [text.get_text() for text in svg.find_all('text', class_='recharts-cartesian-axis-tick-value')]
#     y_values = [text.get_text() for text in svg.find_all('text', class_='recharts-text')]
    
#     # Create key-value pairs for monthly gained video views
#     monthly_views = {}
#     if len(x_labels) == len(y_values):
#         for i in range(len(x_labels)):
#             monthly_views[x_labels[i]] = y_values[i]
    
#     print("Monthly Gained Video Views Data:")
#     for month, views in monthly_views.items():
#         print(f"{month}: {views}")
# else:
#     print("SVG element not found. The data might be rendered dynamically by JavaScript.")

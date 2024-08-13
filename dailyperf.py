from bs4 import BeautifulSoup

def extract_performance_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    # Finding all table rows
    rows = soup.find_all('tr', class_='hover:bg-vidiq-dark-300 transition duration-150 ease-in-out')

    for row in rows:
        columns = row.find_all('td')
        
        date = columns[0].text.strip()
        subscribers = columns[1].text.strip().replace("\u00A0", " ")
        views = columns[2].text.strip().replace("\u00A0", " ")
        estimated_earnings = columns[3].text.strip()
        
        data.append({
            'Date': date,
            'Subscribers': subscribers,
            'Views': views,
            'Estimated Earnings': estimated_earnings
        })
    
    return data

def main():
    # Example HTML content (replace this with your actual HTML content)
    html_content = "html.content"
    
    performance_data = extract_performance_data(html_content)
    
    for entry in performance_data:
        print(entry)

if __name__ == "__main__":
    main()

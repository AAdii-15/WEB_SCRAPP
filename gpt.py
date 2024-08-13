from bs4 import BeautifulSoup

html_content = '''
<!-- Your HTML content goes here -->
'''

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Dictionary to store the values
data = {}

# Helper function to safely extract text
def safe_extract_text(element):
    return element.text.strip() if element else 'N/A'

# Extract the overall score
overall_score_element = soup.find('p', class_='mb-8 text-center text-[88px] font-extrabold leading-[68px]')
data['Overall Score'] = safe_extract_text(overall_score_element)

# Extract the individual scores
scores = soup.find_all('div', class_='flex min-w-[120px] items-center justify-between gap-4 text-xs font-medium text-white')
for score in scores:
    key_element = score.find('span')
    value_element = score.find_all('span')[1] if score.find_all('span') else None
    key = safe_extract_text(key_element)
    value = safe_extract_text(value_element)
    data[key] = value

# Extract the subscribers count and change
subscribers = soup.find('div', class_='lg:border-vidiq-dark-300 h-full lg:border-r lg:border-b')
if subscribers:
    subscribers_details = subscribers.find('div', class_='rounded-[10px] bg-vidiq-dark-500 text-white p-3 md:p-4 border-none h-full')
    if subscribers_details:
        subscribers_count_element = subscribers_details.find('p', class_='mb-1 text-xl font-extrabold text-white lg:text-[26px] lg:leading-[30px]')
        subscribers_change_element = subscribers_details.find('p', class_='text-vidiq-body-gray mb-0 inline-flex gap-1 text-xs font-medium leading-4')
        data['Subscribers'] = safe_extract_text(subscribers_count_element)
        data['Subscribers Change'] = safe_extract_text(subscribers_change_element)

        # Extract the video views count and change
        video_views = subscribers_details.find_next_sibling('div', class_='rounded-[10px] bg-vidiq-dark-500 text-white p-3 md:p-4 border-none h-full')
        if video_views:
            views_count_element = video_views.find('p', class_='mb-1 text-xl font-extrabold text-white lg:text-[26px] lg:leading-[30px]')
            views_change_element = video_views.find('p', class_='text-vidiq-body-gray mb-0 inline-flex gap-1 text-xs font-medium leading-4')
            data['Video Views'] = safe_extract_text(views_count_element)
            data['Video Views Change'] = safe_extract_text(views_change_element)

            # Extract the estimated monthly earnings
            earnings = video_views.find_next_sibling('div', class_='rounded-[10px] bg-vidiq-dark-500 text-white p-3 md:p-4 border-none h-full')
            if earnings:
                earnings_value_element = earnings.find('p', class_='mb-1 text-xl font-extrabold text-white lg:text-[26px] lg:leading-[30px]')
                earnings_comparison_element = earnings.find('div', class_='mb-0 inline-flex items-center gap-2 text-xs text-[#FF4273]')
                data['Estimated Monthly Earnings'] = safe_extract_text(earnings_value_element)
                data['Earnings Comparison'] = safe_extract_text(earnings_comparison_element)

                # Extract the engagement rate
                engagement_rate = earnings.find_next_sibling('div', class_='rounded-[10px] bg-vidiq-dark-500 text-white p-3 md:p-4 border-none h-full')
                if engagement_rate:
                    engagement_rate_value_element = engagement_rate.find('p', class_='mb-1 text-xl font-extrabold text-white lg:text-[26px] lg:leading-[30px]')
                    data['Engagement Rate'] = safe_extract_text(engagement_rate_value_element)

# Print the extracted data
for key, value in data.items():
    print(f"{key}: {value}")

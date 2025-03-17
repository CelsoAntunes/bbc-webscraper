from bs4 import BeautifulSoup
import requests
import json
from urllib.parse import urljoin
import time
from datetime import datetime

url = 'https://www.bbc.com/news/world'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)
response.encoding = response.apparent_encoding
if response.status_code != 200:
    print(f"Failed to get the URL, Status Code: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text,'html.parser')

news_data=[]

def format_timestamp(iso_timestamp):
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        return "Invalid timestamp"
    
for header in soup.find_all(attrs={'data-testid':"card-headline"}):
    headline = header.text.strip()
    parent_a = header.find_parent('a')
    if parent_a and parent_a.get('href'):
        article_url = urljoin(url, parent_a.get('href'))
    else: 
        article_url = None
    if not article_url:
        continue
    try:
        article_response = requests.get(article_url, headers=headers)
        if article_response.status_code == 200:
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            time_tag = article_soup.find('time')
            if time_tag and time_tag.has_attr('datetime'):
                raw_timestamp = time_tag['datetime']
                formatted_timestamp = format_timestamp(raw_timestamp)
            else:
                formatted_timestamp = "No timestamp found"
        else:
            formatted_timestamp = "Failed to load article"
    except Exception:
        formatted_timestamp = "Error fetching timestamp"

    news_data.append({
        "headline": headline,
        "link": article_url,
        "timestamp": formatted_timestamp
    })
print(json.dumps(news_data, indent=4, ensure_ascii=False))
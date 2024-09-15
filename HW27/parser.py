import requests
from  bs4 import BeautifulSoup

response = requests.get('https://scipost.org/atom/publications/comp-ai')

bs = BeautifulSoup(response.text, 'xml')

for entry in bs.find_all('entry'):
    title = entry.find('title').text.strip()
    link = entry.find('link')['href']
    summary = entry.find('summary').text if entry.find('summary') else 'No available summary'

    print(f"Title: {title}")
    print(f"Link: {link}'")
    print(f"Text: {summary}")
    print('-' * 100)

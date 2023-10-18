import requests
import csv
from bs4 import BeautifulSoup

API_KEY = 'YOUR_API_KEY_FOR_YOUTUBE_DATA_API_V3'  
BASE_URL = 'https://www.googleapis.com/youtube/v3/'

def get_channel_id(channel_url):
    channel_url = channel_url.lower().strip()

    
    if not channel_url.startswith('https://'):
        channel_url = 'https://www.youtube.com/' + channel_url.split('youtube.com/')[-1]

    if 'channel/' in channel_url:
        return channel_url.split('channel/')[1].split('/')[0]
    elif 'user/' in channel_url:
        username = channel_url.split('user/')[1].split('/')[0]
        return get_id_from_username(username)
    elif '/c/' in channel_url or '@' in channel_url:
        username = channel_url.split('/')[-1].replace('@', '')
        return get_id_from_username(username)
    return None

def get_id_from_username(username):
    print(f"Fetching channel ID for username: {username}")  
    response = requests.get(BASE_URL + 'channels', params={
        'part': 'id',
        'forUsername': username,
        'key': API_KEY
    })

    if response.status_code != 200:
        print(f"API call failed with status code {response.status_code}. Response: {response.text}")  

    items = response.json().get('items', [])
    if items:
        return items[0]['id']

    
    print("Attempting to scrape channel ID...")  
    url = f"https://www.youtube.com/@{username}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    canonical_link = soup.find("link", {"rel": "canonical"})
    if canonical_link:
        channel_id = canonical_link["href"].split("/")[-1]
        return channel_id

    print(f"No channel ID found for username: {username}")  
    return None

def get_videos_from_channel(channel_id):
    videos = []
    page_token = None
    while True:
        response = requests.get(BASE_URL + 'search', params={
            'part': 'snippet',
            'channelId': channel_id,
            'maxResults': 50,  
            'order': 'date',
            'type': 'video',
            'key': API_KEY,
            'pageToken': page_token
        })
        items = response.json().get('items', [])
        for item in items:
            video = {
                'title': item['snippet']['title'],
                'link': f'https://www.youtube.com/watch?v={item["id"]["videoId"]}',
                'upload_date': item['snippet']['publishedAt']
            }
            videos.append(video)
        page_token = response.json().get('nextPageToken')
        if not page_token:
            break
    return videos

def main():
    channel_url = input('Please provide a link to a YouTube channel: ')
    channel_id = get_channel_id(channel_url)

    if not channel_id:
        print("Invalid YouTube channel URL or failed to fetch channel ID.")
        return

    videos = get_videos_from_channel(channel_id)

    with open('youtube_videos.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'link', 'upload_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for video in videos:
            writer.writerow(video)

    print('CSV file has been created.')

if __name__ == '__main__':
    main()

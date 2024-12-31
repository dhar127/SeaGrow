import re
import json
from urllib.parse import urlencode
import requests

def search_youtube_videos(query, max_results=5):
    """
    Search YouTube videos from all channels
    
    Args:
        query (str): Search query string
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of dictionaries containing video information
    """
    try:
        # Construct search URL
        params = {
            'search_query': query,
            'sp': 'CAA%253D'  # Filter for most relevant results
        }
        base_url = 'https://www.youtube.com/results?' + urlencode(params)
        
        # Headers to mimic browser behavior
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        # Make request to YouTube
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        
        # Find the JSON data in the page
        start = response.text.find('ytInitialData') + 16
        end = response.text.find('};', start) + 1
        json_str = response.text[start:end]
        json_data = json.loads(json_str)
        
        # Extract video data
        videos = []
        items = json_data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
        
        for item in items:
            if 'videoRenderer' in item.keys():
                video_data = item['videoRenderer']
                
                # Extract video details
                video_id = video_data.get('videoId', '')
                title = video_data.get('title', {}).get('runs', [{}])[0].get('text', 'No title')
                channel_name = video_data.get('ownerText', {}).get('runs', [{}])[0].get('text', 'Unknown channel')
                
                # Get duration
                duration = 'Unknown duration'
                if 'lengthText' in video_data:
                    duration = video_data['lengthText'].get('simpleText', 'Unknown duration')
                
                # Create video entry
                video_entry = {
                    'id': video_id,
                    'title': title,
                    'thumbnail': f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
                    'duration': duration,
                    'channel': channel_name,
                    'url': f"https://www.youtube.com/embed/{video_id}"
                }
                
                videos.append(video_entry)
                
                if len(videos) >= max_results:
                    break
        
        print(f"Successfully found {len(videos)} videos from various channels for query: {query}")
        return videos
        
    except Exception as e:
        print(f"Error searching YouTube: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
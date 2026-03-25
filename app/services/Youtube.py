import requests

def get_video(query_string):
	api_key = "AIzaSyByOaZ-HzeujAhOcWwriN1u5YBJMaKjxzs"
	url = "https://www.googleapis.com/youtube/v3/search"

	params = {
		"part":"snippet",
		"key": api_key,
		"q": query_string,
		"maxResults": 1,
		"type": "video",
		"order": "relevance"
	}

	response = requests.get(url, params=params)
	data = response.json()

	items = data.get("items", [])

	video_id = items[0]["id"]["videoId"]
	return f"https://www.youtube.com/watch?v={video_id}"
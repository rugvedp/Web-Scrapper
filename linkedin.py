import requests
import pandas as pd

class LinkedInPostsFetcher:
    def __init__(self, username, rapidapi_key="db05871bedmsh4beab14ea18a00cp11ad63jsnd3ea2d798d53"):
        """
        Initialize the fetcher with the LinkedIn username and RapidAPI key.
        """
        self.username = username
        self.rapidapi_key = rapidapi_key
        self.url = "https://linkedin-data-api.p.rapidapi.com/get-profile-posts"
        self.headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
        }

    def fetch_posts(self):
        """
        Fetches the LinkedIn posts for the given username.
        
        Returns:
            A list of dictionaries, each containing details of a post.
        """
        querystring = {"username": self.username}
        response = requests.get(self.url, headers=self.headers, params=querystring)
        
        # Check for a successful response
        if response.status_code != 200:
            raise Exception(f"Error fetching posts: {response.status_code} - {response.text}")
        
        data = response.json()
        posts = []
        for post in data.get('data', []):
            posts.append({
                "Post URL": post.get('postUrl', ''),
                "Text": post.get('text', ''),
                "Like Count": post.get('likeCount', 0),
                "Total Reactions": post.get('totalReactionCount', 0),
                "Posted Date": post.get('postedDate', ''),
                "Posted Timestamp": post.get('postedDateTimestamp', ''),
                "Share URL": post.get('shareUrl', ''),
                "Author Name": f"{post.get('author', {}).get('firstName', '')} {post.get('author', {}).get('lastName', '')}",
                "Author Profile": post.get('author', {}).get('url', ''),
                "Author Headline": post.get('author', {}).get('headline', ''),
                "Author Profile Picture": post.get('author', {}).get('profilePictures', [{}])[0].get('url', ''),
                "Main Image": post.get('image', [{}])[0].get('url', '') if post.get('image') else '',
                "All Images": ", ".join([img.get('url', '') for img in post.get('image', [])]),
            })
        return posts

    def save_to_excel(self, posts, filename="LinkedIn_Posts.xlsx"):
        """
        Converts the list of posts to a DataFrame and saves it as an Excel file.
        
        Args:
            posts: List of post dictionaries.
            filename: Name of the Excel file to save.
        """
        df = pd.DataFrame(posts)
        df.to_excel(filename, index=False)
        print(f"Excel file saved: {filename}")

    def run(self, filename="LinkedIn_Posts.xlsx"):
        """
        Fetches the posts and saves them to an Excel file.
        """
        posts = self.fetch_posts()
        self.save_to_excel(posts, filename)


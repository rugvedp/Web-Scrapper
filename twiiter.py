import os
import json
import re
import requests
import google.generativeai as genai
import pandas as pd

class TwitterDataProcessor:
    def __init__(self, user_id, rapidapi_key="db05871bedmsh4beab14ea18a00cp11ad63jsnd3ea2d798d53"):
        """
        Initialize the processor with the Twitter user ID and RapidAPI key.
        """
        self.user_id = user_id
        self.rapidapi_key = rapidapi_key
        self.user_url = f"https://twitter-aio.p.rapidapi.com/user/{self.user_id}"
        self.tweet_url = f"https://twitter-aio.p.rapidapi.com/user/{self.user_id}/tweets"
        self.headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "twitter-aio.p.rapidapi.com"
        }
        self.max_itr = 0  # Will be set after fetching user data

    @staticmethod
    def parse_gemini_output(json_string):
        """
        Clean and parse Gemini's JSON output.
        """
        json_string = re.sub(r"^```json\n", "", json_string)
        json_string = re.sub(r"^```", "", json_string)
        json_string = re.sub(r"```$", "", json_string)
        json_string = json_string.strip()
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Invalid JSON string (after cleaning): {json_string}")
            return None

    def fetch_tweets(self):
        """
        Fetch tweets for the given user and save each page's result in a separate file.
        """
        # First, get user details to determine total tweet count.
        user_response = requests.get(self.user_url, headers=self.headers)
        if user_response.status_code != 200:
            raise Exception(f"Error fetching user details: {user_response.status_code}")
        user_data = user_response.json()
        media_count = user_data['user']['result']['legacy']['statuses_count']
        self.max_itr = (media_count // 20) + 1
        
        cursor = None
        page = 1
        
        while True:
            querystring = {"count": "20"}
            if cursor:
                querystring["cursor"] = cursor
            
            response = requests.get(self.tweet_url, headers=self.headers, params=querystring)
            if response.status_code != 200:
                print("Error:", response.status_code)
                break
            
            data = response.json()
            # Save current page's tweets in a text file.
            filename = f"tweets_page_{page}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data["user"]['result'], ensure_ascii=False, indent=4) + "\n")
            print(f"Fetched Page {page} tweets and saved to {filename}...")
            
            # Get next cursor if available.
            try:
                cursor = data['user']['result']['timeline_v2']['timeline']['instructions'][-1]['entries'][-1]['content']['value']
            except (KeyError, IndexError) as e:
                print("No further cursor found. Ending pagination.")
                break
            
            if page == self.max_itr:
                break
            
            page += 1
        
        print("✅ Done! All tweets saved in separate files.")

    def process_tweets(self):
        """
        Process each tweet file using Gemini to extract structured tweet details,
        and save the combined output in a JSON file.
        """
        # Configure Gemini generative API.
        if "GEMINI_API_KEY" not in os.environ:
            raise Exception("GEMINI_API_KEY environment variable is not set!")
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash-001")
        
        prompt = """
        You are an AI assistant that extracts structured details from a Twitter API JSON response. Given a JSON file containing Twitter posts, extract and return the following fields for each post in JSON format:
        
        - `post_id`: The unique identifier of the tweet.
        - `likes`: The number of likes the tweet has received.
        - `retweets`: The number of retweets.
        - `display_url`: A list of all external links in the tweet.
        - `urls`: Any URLs present in the tweet content.
        - `post_images`: A list of URLs of any images attached to the tweet.
        - `posted_date`: The timestamp when the tweet was posted.
        - `user_mentions`: A list of usernames mentioned in the tweet.
        - `full_text`: Description or full_text of the post.
        - `views`: Number of views on the post.
        - `favorite_count`: Number of favorite_count.
        - `lang`: Language used in the post.
        - `quote_count`: Quote count for the post.
        
        ### **Guidelines:**
        - Extract only the required fields; do not modify data.
        - Remove duplicate entries.
        - Ensure URLs and media links are correctly parsed.
        - Return **valid JSON format only**, with no extra text or explanations.
        """
        final_output = []
        # Process tweet files (assuming pages 1 to max_itr)
        for page in range(1, self.max_itr):
            filename = f"tweets_page_{page}.txt"
            try:
                # Upload the file to Gemini.
                doc = genai.upload_file(filename)
                response = model.generate_content([prompt, doc])
                extracted_data = self.parse_gemini_output(response.text)
                if extracted_data:
                    final_output.extend(extracted_data)
                print(f"Page {page} processed and added to final output.")
            except FileNotFoundError:
                print(f"Error: {filename} was not found.")
            except Exception as e:
                print(f"An error occurred while processing {filename}: {e}")
        
        with open("final_output.json", "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=4)
        print("✅ All tweets processed and saved to final_output.json!")

    def convert_to_excel(self):
        """
        Convert the final JSON output to an Excel file.
        """
        try:
            with open("final_output.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            df.to_excel("Twitter_Final.xlsx", index=False, engine="openpyxl")
            print("✅ JSON data successfully converted to Excel (Twitter_Final.xlsx)!")
        except Exception as e:
            print(f"Error converting JSON to Excel: {e}")

    def run(self):
        """
        Run all steps: fetching tweets, processing via Gemini, and converting to Excel.
        """
        self.fetch_tweets()
        self.process_tweets()
        self.convert_to_excel()


# if __name__ == "__main__":
#     # Example usage: Pass the Twitter user ID as a parameter.
#     # Replace '1414828099997290499' with the desired Twitter user ID.
#     processor = TwitterDataProcessor(user_id="1414828099997290499")
#     processor.run()

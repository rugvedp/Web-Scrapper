import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import instaloader

class InstagramBotSelenium:
    def __init__(self, username, password, target_profile, max_posts=10000):
        """
        Initialize the InstagramBotSelenium.
        
        Args:
            username (str): Your Instagram login username.
            password (str): Your Instagram login password.
            target_profile (str): The target Instagram profile (without '@') to scrape.
            max_posts (int): Maximum number of posts to collect.
        """
        self.username = username
        self.password = password
        self.target_profile = target_profile
        self.max_posts = max_posts

    def run(self):
        # Set up Selenium ChromeDriver in headless mode.
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Step 1: Log in to Instagram.
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)  # Wait for the login page to load.
        driver.find_element(By.NAME, "username").send_keys(self.username)
        driver.find_element(By.NAME, "password").send_keys(self.password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(7)  # Allow time for login to complete.

        # Step 2: Navigate to the target profile.
        profile_url = f"https://www.instagram.com/{self.target_profile}/"
        driver.get(profile_url)
        time.sleep(5)  # Wait for the profile page to load.

        # Step 3: Scroll to collect post and reel links.
        SCROLL_PAUSE_TIME = 3
        post_reel_links = set()
        last_height = driver.execute_script("return document.body.scrollHeight")
        while len(post_reel_links) < self.max_posts:
            posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
            for post in posts:
                link = post.get_attribute("href")
                if link:
                    post_reel_links.add(link)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            print(f"Collected {len(post_reel_links)} posts and reels so far...")
        
        # Save collected links to a text file.
        with open("posts_reels.txt", "w", encoding="utf-8") as file:
            for link in post_reel_links:
                file.write(link + "\n")
        print(f"✅ Successfully saved {len(post_reel_links)} post and reel links to posts_reels.txt")
        driver.quit()

        # Step 4: Use Instaloader to fetch details for each post.
        loader = instaloader.Instaloader()
        
        def extract_shortcode(url):
            match = re.search(r"/(p|reel)/([A-Za-z0-9_-]+)", url)
            return match.group(2) if match else None
        
        with open("posts_reels.txt", "r", encoding="utf-8") as file:
            post_links = [line.strip() for line in file.readlines()]
        
        data = []
        for link in post_links:
            shortcode = extract_shortcode(link)
            if shortcode:
                try:
                    post = instaloader.Post.from_shortcode(loader.context, shortcode)
                    data.append({
                        "Post URL": link,
                        "Caption": post.caption or "",
                        "Likes": post.likes,
                        "Comments": post.comments,
                        "Engagement": post.likes + post.comments,
                        "Timestamp": post.date_utc.strftime("%Y-%m-%d %H:%M:%S") if post.date_utc else ""
                    })
                    print(f"✅ Fetched: {link}")
                except Exception as e:
                    print(f"❌ Error fetching {link}: {e}")

        # Convert the data to a DataFrame and save as Excel.
        df = pd.DataFrame(data)
        df.to_excel("instagram_posts.xlsx", index=False)
        print("✅ All data saved to 'instagram_posts.xlsx'")

import os
import json
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class YouTubeDataCollector:
    def __init__(self, channel_url, pause_time=2, timeout=15, headless=True):
        """
        Initialize the YouTubeDataCollector.
        
        Args:
            channel_url (str): Base URL of the YouTube channel (e.g., "https://www.youtube.com/@ChannelName").
            pause_time (int, optional): Pause time between scrolls. Default is 2 seconds.
            timeout (int, optional): Maximum time to wait for scrolling. Default is 180 seconds.
            headless (bool, optional): Whether to run Selenium ChromeDriver in headless mode.
        """
        self.channel_url = channel_url.rstrip("/")
        self.pause_time = pause_time
        self.timeout = timeout
        self.headless = headless
        
        # Derived URLs for each tab
        self.videos_url = self.channel_url + "/videos"
        self.live_url   = self.channel_url + "/streams"
        self.shorts_url = self.channel_url + "/shorts"

    def _get_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    # -------- Standard Video Methods --------
    def scroll_until_all_videos_loaded(self, driver):
        """
        Scrolls down the Videos page until the timeout is reached.
        Collects unique standard video URLs (excluding Shorts).
        """
        start_time = time.time()
        unique_links = set()
        last_count = 0

        while time.time() - start_time < self.timeout:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(self.pause_time)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # Look for links containing "watch?v=" and exclude "/shorts/"
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "watch?v=" in href and "/shorts/" not in href:
                    if not href.startswith("http"):
                        href = "https://www.youtube.com" + href
                    unique_links.add(href)
            current_count = len(unique_links)
            print(f"Standard Videos: Found {current_count} unique links so far.")
            if current_count == last_count:
                time.sleep(self.pause_time)
            else:
                last_count = current_count

        elapsed = time.time() - start_time
        print(f"Standard Videos: Scrolling finished after {elapsed:.2f} seconds with {len(unique_links)} links.")
        return list(unique_links)

    def get_video_details(self, driver, video_url):
        """
        Loads a YouTube video page and extracts basic details such as view count and comment count.
        """
        driver.get(video_url)
        time.sleep(4)  # Allow page to load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        views = "Not found"
        view_elem = soup.find("span", class_="view-count")
        if view_elem:
            views = view_elem.get_text(strip=True)
        
        comments = "Not found"
        comment_elem = soup.find("yt-formatted-string", {"id": "count"})
        if comment_elem:
            comments = comment_elem.get_text(strip=True)
        
        return {"url": video_url, "views": views, "comments": comments}

    def scrape_standard_videos(self):
        """
        Opens the channel's Videos page, scrolls to load video links, scrapes details for each video,
        and returns the collected data.
        """
        driver = self._get_driver()
        driver.get(self.videos_url)
        time.sleep(3)
        video_links = self.scroll_until_all_videos_loaded(driver)
        print(f"Standard Videos: Total unique video links collected: {len(video_links)}")
        
        video_data = []
        for idx, link in enumerate(video_links, start=1):
            print(f"Standard Videos: Processing video {idx}/{len(video_links)}: {link}")
            details = self.get_video_details(driver, link)
            video_data.append(details)
        
        driver.quit()
        # Save to JSON (optional)
        with open("video_details.json", "w", encoding="utf-8") as f:
            json.dump(video_data, f, ensure_ascii=False, indent=4)
        print("Standard Videos: Saved details to video_details.json")
        return video_data

    # -------- Live Stream Methods --------
    def scroll_until_all_streams_loaded(self, driver):
        """
        Scrolls down the Live Streams page until the timeout is reached.
        Collects unique live stream video URLs.
        """
        start_time = time.time()
        unique_links = set()
        last_count = 0

        while time.time() - start_time < self.timeout:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(self.pause_time)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "watch?v=" in href:  # Live streams are also video links
                    if not href.startswith("http"):
                        href = "https://www.youtube.com" + href
                    unique_links.add(href)
            current_count = len(unique_links)
            print(f"Live Streams: Found {current_count} unique links so far.")
            if current_count == last_count:
                time.sleep(self.pause_time)
            else:
                last_count = current_count

        elapsed = time.time() - start_time
        print(f"Live Streams: Scrolling finished after {elapsed:.2f} seconds with {len(unique_links)} links.")
        return list(unique_links)

    def get_stream_details(self, driver, video_url):
        """
        Loads a live stream video page and extracts details such as view count, live status, and scheduled time.
        """
        driver.get(video_url)
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        views = "Not found"
        view_elem = soup.find("span", class_="view-count")
        if view_elem:
            views = view_elem.get_text(strip=True)
        
        live_status = "Not found"
        live_elem = soup.find("span", string="LIVE")
        if live_elem:
            live_status = "LIVE"
        
        scheduled = "Not found"
        scheduled_elem = soup.find("div", id="date")
        if scheduled_elem:
            scheduled = scheduled_elem.get_text(strip=True)
        
        return {"url": video_url, "views": views, "live_status": live_status, "scheduled": scheduled}

    def scrape_live_streams(self):
        """
        Opens the channel's Live Streams page, scrolls to load links, scrapes details for each live stream,
        and returns the collected data.
        """
        driver = self._get_driver()
        driver.get(self.live_url)
        time.sleep(3)
        stream_links = self.scroll_until_all_streams_loaded(driver)
        print(f"Live Streams: Total unique stream links collected: {len(stream_links)}")
        
        stream_data = []
        for idx, link in enumerate(stream_links, start=1):
            print(f"Live Streams: Processing stream video {idx}/{len(stream_links)}: {link}")
            details = self.get_stream_details(driver, link)
            stream_data.append(details)
        
        driver.quit()
        # Save to JSON (optional)
        with open("streams_details.json", "w", encoding="utf-8") as f:
            json.dump(stream_data, f, ensure_ascii=False, indent=4)
        print("Live Streams: Saved details to streams_details.json")
        return stream_data

    # -------- Shorts Methods --------
    def scroll_until_all_shorts_loaded(self, driver):
        """
        Scrolls down the Shorts page until the timeout is reached.
        Collects unique Shorts video URLs.
        """
        start_time = time.time()
        unique_links = set()
        last_count = 0

        while time.time() - start_time < self.timeout:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(self.pause_time)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "/shorts/" in href:
                    if not href.startswith("http"):
                        href = "https://www.youtube.com" + href
                    unique_links.add(href)
            current_count = len(unique_links)
            print(f"Shorts: Found {current_count} unique Shorts links so far.")
            if current_count == last_count:
                time.sleep(self.pause_time)
            else:
                last_count = current_count

        elapsed = time.time() - start_time
        print(f"Shorts: Scrolling finished after {elapsed:.2f} seconds with {len(unique_links)} links.")
        return list(unique_links)

    def get_shorts_details(self, driver, video_url):
        """
        Loads a Shorts video page and extracts details such as view count and comment count.
        """
        driver.get(video_url)
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        views = "Not found"
        view_elem = soup.find("span", class_="view-count")
        if view_elem:
            views = view_elem.get_text(strip=True)
        
        comments = "Not found"
        comment_elem = soup.find("yt-formatted-string", {"id": "count"})
        if comment_elem:
            comments = comment_elem.get_text(strip=True)
        
        return {"url": video_url, "views": views, "comments": comments}

    def scrape_shorts(self):
        """
        Opens the channel's Shorts page, scrolls to load links, scrapes details for each Shorts video,
        and returns the collected data.
        """
        driver = self._get_driver()
        driver.get(self.shorts_url)
        time.sleep(3)
        shorts_links = self.scroll_until_all_shorts_loaded(driver)
        print(f"Shorts: Total unique Shorts links collected: {len(shorts_links)}")
        
        shorts_data = []
        for idx, link in enumerate(shorts_links, start=1):
            print(f"Shorts: Processing Shorts video {idx}/{len(shorts_links)}: {link}")
            details = self.get_shorts_details(driver, link)
            shorts_data.append(details)
        
        driver.quit()
        # Save to JSON (optional)
        with open("shorts_details.json", "w", encoding="utf-8") as f:
            json.dump(shorts_data, f, ensure_ascii=False, indent=4)
        print("Shorts: Saved details to shorts_details.json")
        return shorts_data

    # -------- Final Excel Saving --------
    def save_all_to_excel(self, video_data, stream_data, shorts_data, excel_filename="youtube.xlsx"):
        """
        Combines all collected data into a single Excel file with three sheets.
        """
        video_df = pd.DataFrame(video_data)
        stream_df = pd.DataFrame(stream_data)
        shorts_df = pd.DataFrame(shorts_data)
        
        with pd.ExcelWriter(excel_filename) as writer:
            video_df.to_excel(writer, sheet_name="Standard Videos", index=False)
            stream_df.to_excel(writer, sheet_name="Live Streams", index=False)
            shorts_df.to_excel(writer, sheet_name="Shorts", index=False)
        print(f"Combined details saved to {excel_filename}")

    # -------- Unified Run Method --------
    def run(self):
        print("Starting standard video scraping...")
        video_data = self.scrape_standard_videos()
        print("Standard video scraping complete.\n")
        
        print("Starting live stream scraping...")
        stream_data = self.scrape_live_streams()
        print("Live stream scraping complete.\n")
        
        print("Starting Shorts scraping...")
        shorts_data = self.scrape_shorts()
        print("Shorts scraping complete.\n")
        
        # Combine all data into one Excel file.
        self.save_all_to_excel(video_data, stream_data, shorts_data)
        return {
            "video_data": video_data,
            "stream_data": stream_data,
            "shorts_data": shorts_data
        }

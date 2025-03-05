#for streamlit
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
#for streamlit

import asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    import nest_asyncio
    nest_asyncio.apply()

import streamlit as st
import os
from web import WebCrawlerSummarizer
from linkedin import LinkedInPostsFetcher
from youtube import YouTubeDataCollector 
from twiiter import TwitterDataProcessor
from instagram import InstagramBotSelenium  # New Instagram scraper module

# Secrets from Streamlit secrets
username = st.secrets['username']
password = st.secrets['password']
os.environ['GEMINI_API_KEY'] = st.secrets['GEMINI_API_KEY']
os.environ['SAMBANOVA_API_KEY'] = st.secrets['SAMBANOVA_API_KEY']
os.environ['GROQ_API_KEY'] = st.secrets['GROQ_API_KEY']

def main():
    st.title("Web Crawler & Summarizer")
    st.write("Enter a website URL to crawl and generate summaries.")

    # Input for website URL (default empty)
    website_url = st.text_input("Website URL", value="")

    st.write("Select social media platforms to process:")

    # Arrange social media toggles (with icons) in one row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/174/174857.png", width=50)
        linkedin_toggle = st.checkbox("LinkedIn", value=False)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1384/1384060.png", width=50)
        youtube_toggle = st.checkbox("YouTube", value=False)
    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/733/733579.png", width=50)
        twitter_toggle = st.checkbox("Twitter", value=False)
    with col4:
        st.image("https://cdn-icons-png.flaticon.com/512/2111/2111463.png", width=50)
        instagram_toggle = st.checkbox("Instagram", value=False)

    # Conditionally display input fields for each platform
    linkedin_username = ""
    if linkedin_toggle:
        linkedin_username = st.text_input("LinkedIn Username")
    
    youtube_channel = ""
    if youtube_toggle:
        youtube_channel = st.text_input("YouTube Channel URL")
    
    twitter_userid = ""
    if twitter_toggle:
        st.write("Enter Twitter User ID (numeric). To obtain your Twitter ID, use a service like [tweeterid.com](https://tweeterid.com/).")
        twitter_userid = st.text_input("Twitter User ID")
    
    instagram_url = ""
    if instagram_toggle:
        instagram_url = st.text_input("Instagram Page URL")

    # Run summarization when button is clicked
    if st.button("Run Summarizer"):
        st.info("Running the website summarizer. This may take a while...")
        if website_url:
            processor = WebCrawlerSummarizer(website_url)
            processor.run()
            st.success("Website summarization complete!")
            # Download buttons for website summarizer outputs
            for file in ["final.docx", "temp.docx"]:
                if os.path.exists(file):
                    with open(file, "rb") as f:
                        st.download_button(label=f"Download {file}", data=f, file_name=file, mime="application/octet-stream")
        else:
            st.warning("Please enter a website URL.")

        # LinkedIn Processing
        if linkedin_toggle and linkedin_username:
            st.info("Fetching LinkedIn posts...")
            LinkedInPostsFetcher(linkedin_username).run()
            if os.path.exists("LinkedIn_Posts.xlsx"):
                with open("LinkedIn_Posts.xlsx", "rb") as f:
                    st.download_button("Download LinkedIn Posts", f, "LinkedIn_Posts.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # YouTube Processing
        if youtube_toggle and youtube_channel:
            st.info("Scraping YouTube channel...")
            yt_scraper = YouTubeDataCollector(youtube_channel)
            yt_scraper.run()
            if os.path.exists("youtube.xlsx"):
                with open("youtube.xlsx", "rb") as f:
                    st.download_button("Download YouTube Data (Excel)", data=f, file_name="youtube.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Twitter Processing
        if twitter_toggle and twitter_userid:
            st.info("Processing Twitter data...")
            TwitterDataProcessor(twitter_userid).run()
            if os.path.exists("Twitter_Final.xlsx"):
                with open("Twitter_Final.xlsx", "rb") as f:
                    st.download_button("Download Twitter Data", f, "Twitter_Final.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Instagram Processing
        if instagram_toggle and instagram_url:
            st.info("Scraping Instagram posts...")
            InstagramBotSelenium(username, password, instagram_url).run()
            if os.path.exists("instagram_posts.xlsx"):
                with open("instagram_posts.xlsx", "rb") as f:
                    st.download_button("Download Instagram Posts", f, "instagram_posts.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()

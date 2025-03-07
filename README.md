
# Web Crawler & Summarizer 🚀

A multi-functional web scraping and summarization project that collects data from websites and various social media platforms (LinkedIn, YouTube, Twitter, Instagram) and provides the results via a user-friendly Streamlit UI. This project leverages Selenium, BeautifulSoup, API calls, and Streamlit to extract and display data in downloadable formats (e.g., DOCX, Excel). 

---

## Features ✨

- **Website Summarization 🌐:**  
  Extracts and summarizes content from a provided website URL.

- **LinkedIn Posts Fetcher 💼:**  
  Scrapes posts from a specified LinkedIn profile.

- **YouTube Data Collector 🎥:**  
  Scrapes standard videos, live streams, and Shorts from a YouTube channel. Extracts details including title, views, and comments, and combines all data into a single Excel file with separate sheets for each category.

- **Twitter Data Processor 🐦:**  
  Processes Twitter data using a numeric Twitter User ID.  
  **Note:** To obtain your numeric Twitter ID, use a service like [tweeterid.com](https://tweeterid.com/) 🔍.

- **Instagram Bot 📸:**  
  Scrapes Instagram posts using Selenium in headless mode so no browser window is opened.

- **Streamlit User Interface 💻:**  
  An interactive UI featuring icon-based toggle buttons (arranged in one line) for each social media platform, allowing users to selectively enable processing. Download buttons provide access to the generated output files.

---

## Installation 🛠️

### Prerequisites

- Python 3.10 or higher.
- Google Chrome installed on your system.
- A compatible Chromedriver (or use the `webdriver_manager` to manage the driver automatically).

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/rugvedp/Web-Scrapper.git
   cd Web-Scrapper
   ```

2. **Install Dependencies:**

   Use the provided `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Secrets:**

   Create a `secrets.toml` (or use Streamlit's secrets management) with your credentials:

   ```toml
   username = "your_instagram_username"
   password = "your_instagram_password"
   GEMINI_API_KEY = "your_gemini_api_key"
   SAMBANOVA_API_KEY = "your_sambanova_api_key"
   ```

---

## Usage 🚀

1. **Run the Streamlit App:**

   From the command line, run:

   ```bash
   streamlit run main.py
   ```

2. **Interact with the UI:**

   - **Website URL:**  
     Enter the URL of the website you want to summarize.

   - **Social Media Toggles:**  
     At the top, you'll see four icon-based toggles for LinkedIn, YouTube, Twitter, and Instagram arranged in one row.  
     - Clicking an icon enables its corresponding input field.
     - **Twitter:** An instruction is provided above the Twitter ID input—use a service like [tweeterid.com](https://tweeterid.com/) to obtain your numeric Twitter ID.

   - **Input Fields:**  
     - **LinkedIn:** Enter the LinkedIn profile username.
     - **YouTube:** Enter the YouTube channel URL.
     - **Twitter:** Enter the numeric Twitter User ID.
     - **Instagram:** Enter the Instagram page URL.

   - **Run Summarizer:**  
     Click the **"Run Summarizer"** button to start processing. The UI will display status messages and, once complete, provide download buttons for each output (e.g., website DOCX files, LinkedIn Excel, combined YouTube Excel, Twitter Excel, Instagram Excel).

---

## Project Structure 📁

- **main.py:**  
  The main Streamlit UI script that integrates all modules.

- **web.py:**  
  Contains the `WebCrawlerSummarizer` class for website summarization.

- **linkedin.py:**  
  Contains the `LinkedInPostsFetcher` class for fetching LinkedIn posts.

- **youtube.py:**  
  Contains the `YouTubeDataCollector` class for scraping YouTube standard videos, live streams, and Shorts, and for saving combined results to an Excel file.

- **twiiter.py:**  
  Contains the `TwitterDataProcessor` class for processing Twitter data.

- **instagram.py:**  
  Contains the `InstagramBotSelenium` class for scraping Instagram posts using Selenium in headless mode.

- **requirements.txt:**  
  Lists all required Python packages.

- **README.md:**  
  This file.

---

## Troubleshooting ⚠️

- **Playwright/Async Subprocess Errors on Windows:**  
  Ensure you set the Windows Proactor Event Loop Policy and apply `nest_asyncio` as shown at the top of `main.py`.

- **Pydantic Warnings:**  
  These are deprecation warnings from Pydantic V2 and can be safely ignored for now.

---

## Acknowledgments 🙏

- Thanks to the contributors of the libraries used (Streamlit, Selenium, BeautifulSoup, Pandas, Requests, etc.).
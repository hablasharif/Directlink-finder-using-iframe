import streamlit as st
import requests
import random
from bs4 import BeautifulSoup
from lxml import html
import re
from urllib.parse import urlparse

# User agents to mimic different browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/94.0.992.50",
]

# Function to extract a link from a URL
def extract_link(url):
    try:
        # Check if the URL contains the specified text
        if "https://expeditesimplicity.com/safe.php?link=" in url:
            # Extract the part after the specified text
            link = url.split("https://expeditesimplicity.com/safe.php?link=")[1]
            return link
        else:
            # Create a custom session with a random user agent
            session = requests.Session()
            session.verify = False
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            session.headers.update(headers)

            # Send an HTTP GET request to the URL with retries
            for _ in range(3):
                response = session.get(url)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Find the element with the data-drive attribute
                    episode_item = soup.find('li', {'data-drive': True})

                    # Extract the URL from the data-drive attribute
                    if episode_item:
                        link = episode_item['data-drive']
                        return link

            return None
    except Exception as e:
        return None

# Function to extract all iframe sources from a URL
def extract_all_iframe_srcs(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if urlparse(url).netloc == "www.hindimovies.to" and re.match(r'^/movie/', urlparse(url).path):
            st.write("IFrame Sources are not applicable for this URL.")
            return [find_custom_url(url)]

        iframes = soup.find_all('iframe')
        if not iframes:
            return ["No iframes found on this page."]
        
        iframe_srcs = [iframe.get('src') for iframe in iframes if iframe.get('src')]
        return iframe_srcs
    except Exception as e:
        return [f"Error: {e}"]

# Function to find the custom URL for "www.hindimovies.to" domain and specific URL pattern
def find_custom_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Add code to find the custom URL for "www.hindimovies.to" domain and specific URL pattern
        # Here's a placeholder code to extract the URL from a div with id "iframe-screen":
        div = soup.find('div', id="iframe-screen")
        if div:
            a = div.find('a', href=True)
            if a:
                return a['href']
            else:
                return "No custom URL found on this page."
        else:
            return "No custom URL found on this page."
    except Exception as e:
        return f"Error: {e}"

# Function to extract links 01, 03, and 04 from the provided URL pattern
def extract_links_010304(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        link_pattern = re.compile(r'Link\s+(\d{2})')
        link_elements = soup.find_all(text=link_pattern)

        links = {}
        for link_element in link_elements:
            match = link_pattern.search(link_element)
            if match:
                link_number = match.group(1)
                link_container = link_element.find_next('div', class_='OptionBx on')
                if link_container:
                    link_url = link_container.find('a', href=True)
                    if link_url:
                        links[f"Link {link_number}"] = link_url['href']
        
        return links
    except Exception as e:
        return {}

# Define the Streamlit app
def main():
    st.title("Combined Streamlit App")

    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose the App Mode", ["Link Extractor", "IFrame SRC Extractor"])

    if app_mode == "Link Extractor":
        st.subheader("Link Extractor")

        # User input for multiple URLs
        urls = st.text_area("Enter multiple URLs (one URL per line):")

        if st.button("Extract Links"):
            urls_list = urls.split('\n')
            for url in urls_list:
                url = url.strip()
                if url:
                    extracted_link = extract_link(url)
                    if extracted_link:
                        st.success(f"Extracted Link from {url}:")
                        st.write(extracted_link)
                        show_source_code(extracted_link)
                    else:
                        st.error(f"Link not found on the page: {url}")

    elif app_mode == "IFrame SRC Extractor":
        st.subheader("IFrame SRC Extractor for Streaming Websites")

        st.write("Enter the URLs of streaming websites (one per line) to extract iframe sources:")
        user_input = st.text_area("Enter URLs", "")

        if st.button("Extract"):
            urls = user_input.split('\n')
            for url in urls:
                if url.strip():
                    iframe_srcs = extract_all_iframe_srcs(url.strip())
                    st.write(f"URL: {url.strip()}")
                    if iframe_srcs:
                        st.write("IFrame Sources:")
                        for i, src in enumerate(iframe_srcs):
                            st.write(f"{i + 1}. {src}")
                    else:
                        st.write("No IFrame Sources found.")
                    
                    st.write("Link 01, Link 03, Link 04:")
                    links = extract_links_010304(url.strip())
                    for link, href in links.items():
                        st.write(f"{link}: {href}")
                    st.write("-" * 50)

# Function to fetch and display the source code of a URL using dynamically extracted XPath
def show_source_code(link):
    try:
        # Create a custom session with a random user agent
        session = requests.Session()
        session.verify = False
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        session.headers.update(headers)

        # Send an HTTP GET request to the link with retries
        for _ in range(3):
            response = session.get(link)
            if response.status_code == 200:
                # Parse the HTML content of the page using lxml
                tree = html.fromstring(response.content)

                # Use XPath expression to find all href URLs
                href_urls = tree.xpath('//a/@href')
                if href_urls:
                    st.subheader("Href URLs Extracted Using Dynamically Detected XPath:")
                    for url in href_urls:
                        # Split the URL by "=" and print the part after "="
                        parts = url.split("=")
                        if len(parts) > 1:
                            st.write(parts[1])
                    return

        st.error("Failed to fetch href URLs using dynamically detected XPath after multiple attempts.")
    except Exception as e:
        st.error("An error occurred while fetching the content.")

if __name__ == "__main__":
    main()

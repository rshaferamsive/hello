import streamlit as st
import requests
from bs4 import BeautifulSoup

# Streamlit app title
st.title("Google Search Title Scraper")

# User inputs for keyword and number of results
keyword = st.text_input("Enter the keyword to search for:")
num_results = st.number_input("Enter the number of results to scrape (up to 10):", min_value=1, max_value=10, value=5)

# Function to scrape the titles and URLs directly from Google search results page
def scrape_google_titles_and_urls(keyword, num_results):
    # Construct the URL for the search engine's results page
    url = f'https://www.google.com/search?q={keyword}&num={num_results}'

    # Send a GET request to the search engine's results page
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the title tags and URLs in the search results
    results = soup.select('.BNeawe.vvjwJb.AP7Wnd')  # Titles
    links = soup.select('.BNeawe.UPmit.AP7Wnd')     # URLs

    # Extract the titles and URLs
    titles_and_urls = [(results[i].get_text(), links[i].get_text()) for i in range(len(results))]

    return titles_and_urls

# List of months to search for in the titles
months = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]

# Button to trigger the scraping process
if st.button("Search"):
    if keyword:
        # Scrape the specified number of Google titles and URLs for the entered keyword
        titles_and_urls = scrape_google_titles_and_urls(keyword, num_results)

        # Count the number of titles that contain any month and display titles with their URLs and ranks
        month_count = 0
        titles_with_months = []

        for index, (title, url) in enumerate(titles_and_urls):
            if any(month in title.lower() for month in months):
                month_count += 1
                titles_with_months.append((index + 1, url, title))  # Store rank (index + 1), URL, and title

        # Display the month count at the top
        st.write(f"\nNumber of titles with a month: {month_count}\n")

        # Display the titles, URLs, and ranks that contain a month
        if titles_with_months:
            st.write("Sites with a month in the title:")
            for rank, url, title in titles_with_months:
                st.write(f"Rank: {rank}")
                st.write(f"Site: {url}")
                st.write(f"Title: {title}\n")
        else:
            st.write("No titles with a month were found.")
    else:
        st.warning("Please enter a keyword to search.")
